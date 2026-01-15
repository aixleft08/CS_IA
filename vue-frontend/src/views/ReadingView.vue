<script setup>
import { onMounted, onBeforeUnmount, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import DictionaryCard from '@/components/DictionaryCard.vue'
import Toast from '@/components/Toast.vue'
import { useArticles } from '@/composables/useArticles'
import { useWordBank } from '@/composables/useWordBank'
import { useAuth } from '@/composables/useAuth'
import { Stack } from '@/utils/stack'

const route = useRoute()
const articleId = route.params.id
const { token } = useAuth()

const { currentArticle, currentLoading, currentError, fetchArticle } = useArticles()
const { addWord, deleteWord } = useWordBank()

const currentEntry = ref({ word: '', definition: '', translation: '', defs: [] })

// toast
const toastOpen = ref(false)
const toastMsg = ref('')
const toastType = ref('success')
function notify(message, type='success') {
  toastMsg.value = message
  toastType.value = type
  toastOpen.value = false
  requestAnimationFrame(() => { toastOpen.value = true })
}

// ---- reading time tracking ----
const startedAt = ref(0)
const sentOnce = ref(false)

function secondsSinceStart() {
  if (!startedAt.value) return 0
  return Math.floor((Date.now() - startedAt.value) / 1000)
}

function sendReadingTime(seconds) {
  if (sentOnce.value) return
  if (!token.value) return
  if (!Number.isFinite(seconds) || seconds <= 0) return

  sentOnce.value = true

  const url = `/api/articles/${articleId}/reading-time`
  const payload = JSON.stringify({ elapsed_time_seconds: seconds })

  if (navigator.sendBeacon) {
    try {
      const blob = new Blob([payload], { type: 'application/json' })
      navigator.sendBeacon(url, blob)
      return
    } catch (_) {}
  }

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token.value}`,
    },
    body: payload,
    keepalive: true,
  }).catch(() => {})
}

function onPageHide() {
  sendReadingTime(secondsSinceStart())
}
function onVisibilityChange() {
  if (document.visibilityState === 'hidden') {
    sendReadingTime(secondsSinceStart())
  }
}

onMounted(async () => {
  startedAt.value = Date.now()
  await fetchArticle(articleId)
  window.addEventListener('pagehide', onPageHide)
  document.addEventListener('visibilitychange', onVisibilityChange)
})

onBeforeUnmount(() => {
  sendReadingTime(secondsSinceStart())
  window.removeEventListener('pagehide', onPageHide)
  document.removeEventListener('visibilitychange', onVisibilityChange)
})

// ---- dictionary helpers ----
function cleanWord(raw) {
  return raw.replace(/[.,!?;:()'"“”]/g, '').toLowerCase()
}

const MAX_ITEMS = 4
const MAX_LEN = 110
function truncate(s, n = MAX_LEN) { return !s ? '' : (s.length > n ? s.slice(0, n - 1) + '…' : s) }

function formatMeanings(apiEntry) {
  if (!apiEntry?.meanings?.length) return []
  const seenPos = new Set()
  const items = []
  for (const m of apiEntry.meanings) {
    if (!m?.partOfSpeech || seenPos.has(m.partOfSpeech)) continue
    const def = m.definitions?.[0]?.definition
    if (!def) continue
    items.push({ pos: m.partOfSpeech, text: truncate(def) })
    seenPos.add(m.partOfSpeech)
    if (items.length >= MAX_ITEMS) break
  }
  return items
}

function buildPreview(defs) {
  if (!defs?.length) return 'No definition found.'
  return defs.map(d => `${d.pos}: ${d.text}`).join('; ')
}

async function onWordClick(rawWord) {
  const word = cleanWord(rawWord)
  if (!word) return
  currentEntry.value = { word, definition: 'Loading definition…', translation: '', defs: [] }
  try {
    const res = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(word)}`)
    if (!res.ok) {
      currentEntry.value = { word, definition: 'No definition found.', translation: '', defs: [] }
      return
    }
    const data = await res.json()
    const entry = data?.[0]
    const defs = formatMeanings(entry)
    currentEntry.value = { word, definition: buildPreview(defs), translation: '', defs }
  } catch {
    currentEntry.value = { word, definition: 'Error fetching definition.', translation: '', defs: [] }
  }
}

// ---- undo/redo ----
const undoStack = new Stack({ maxSize: 200 })
const redoStack = new Stack({ maxSize: 200 })

const undoCount = ref(0)
const redoCount = ref(0)

function syncCounts() {
  try { undoCount.value = undoStack.size() } catch { undoCount.value = 0 }
  try { redoCount.value = redoStack.size() } catch { redoCount.value = 0 }
}

const canUndo = computed(() => undoCount.value > 0)
const canRedo = computed(() => redoCount.value > 0)

function safePop(stack) {
  try { return stack.pop() } catch { return null }
}
function safePush(stack, item) {
  try { stack.push(item); return true } catch { return false }
}
function safeClear(stack) {
  try { stack.clear() } catch {}
}

async function addToWordbank(entry) {
  if (!entry?.word) return

  if (!entry.defs || entry.defs.length === 0) {
    notify(`No definition found for “${entry.word}”. Not added.`, 'warn')
    return
  }

  const res = await addWord(entry.word)

  if (res?.ok) {
    const newId = res.id ?? null
    safePush(undoStack, { type: 'add', word: entry.word, id: newId })
    safeClear(redoStack)
    syncCounts()
    notify(`Added “${entry.word}” to wordbank`)
    return
  }

  if (res?.reason === 'duplicate') return notify(`“${entry.word}” is already in your wordbank`, 'info')
  if (res?.reason === 'unauthorized') return notify('Please sign in to save words', 'warn')
  if (res?.reason === 'network') return notify('Network error—try again', 'error')
  notify('Could not add word', 'error')
}

async function undo() {
  const action = safePop(undoStack)
  if (!action) return
  syncCounts()

  if (action.type === 'add') {
    if (!action.id) {
      safePush(undoStack, action)
      syncCounts()
      notify('Undo failed (missing id).', 'warn')
      return
    }

    await deleteWord(action.id)
    safePush(redoStack, action)
    syncCounts()
    notify(`Undid add: “${action.word}”`, 'info')
  }
}

async function redo() {
  const action = safePop(redoStack)
  if (!action) return
  syncCounts()

  if (action.type === 'add') {
    const res = await addWord(action.word)

    if (res?.ok) {
      const newId = res.id ?? null
      safePush(undoStack, { type: 'add', word: action.word, id: newId })
      syncCounts()
      notify(`Redid add: “${action.word}”`, 'info')
      return
    }

    safePush(redoStack, action)
    syncCounts()
    notify('Redo failed.', 'warn')
  }
}
</script>

<template>
  <div class="page">
    <NavBar />
    <main class="main">
      <section class="grid">
        <article class="reader">
          <div class="toolbar">
            <button class="toolbtn" :disabled="!canUndo" @click="undo">Undo</button>
            <button class="toolbtn" :disabled="!canRedo" @click="redo">Redo</button>
          </div>

          <p v-if="currentLoading">Loading article…</p>
          <p v-else-if="currentError" style="color:#c33">{{ currentError }}</p>

          <template v-else-if="currentArticle">
            <h1 class="title">{{ currentArticle.title }}</h1>

            <p
              v-for="(para, i) in (currentArticle.content || '').split('\n').filter(Boolean)"
              :key="i"
            >
              <span
                v-for="(w, wi) in para.split(' ')"
                :key="wi"
                class="word"
                :class="{ long: (w || '').length > 20 }"
                @click="onWordClick(w)"
              >{{ w }}</span>
            </p>
          </template>

          <p v-else>Article not found.</p>
        </article>

        <DictionaryCard class="side" :entry="currentEntry" @add="addToWordbank" />
      </section>
    </main>

    <Toast
      :open="toastOpen"
      :message="toastMsg"
      :type="toastType"
      @close="toastOpen = false"
    />
  </div>
</template>

<style scoped>
.page{
  min-height:100vh;
  display:flex;
  flex-direction:column;
  background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
  overflow-x:hidden;
}

.main{flex:1;max-width:1100px;margin:0 auto;padding:40px 20px}

.grid{
  display:grid;
  grid-template-columns:minmax(0, 1.5fr) minmax(0, .9fr);
  gap:24px;
  align-items:start;
}

.reader,.side{min-width:0}

.reader{
  background:#fff;
  border-radius:12px;
  border:2px solid #cfd4dc;
  box-shadow:0 10px 25px rgba(0,0,0,.1);
  padding:1.5rem;
  min-height:400px;
}

.title{text-align:center;margin:0 0 1rem;font-size:2.1rem}

.reader p{
  margin:1rem 0;
  color:#222;
  line-height:1.7;
  white-space:normal;
}

.word{
  display:inline-block;
  cursor:pointer;
  padding:0 .1rem;
  margin-right:.1rem;
  white-space:nowrap;
}

.word:hover{background:rgba(102,126,234,.18);border-radius:4px}

.word.long{
  white-space:normal;
  overflow-wrap:anywhere;
  word-break:break-word;
}

.side{position:sticky;top:18px}

.toolbar{
  display:flex;
  gap:.5rem;
  justify-content:flex-end;
  margin-bottom:.5rem;
}

.toolbtn{
  padding:.45rem .8rem;
  border:1px solid #cfd4dc;
  background:#f6f7fb;
  border-radius:8px;
  font-weight:700;
  cursor:pointer;
}
.toolbtn:hover{background:#eef0fb}
.toolbtn:disabled{
  opacity:.55;
  cursor:not-allowed;
}

@media(max-width:960px){.grid{grid-template-columns:1fr}}
</style>
