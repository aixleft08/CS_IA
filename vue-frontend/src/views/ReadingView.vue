<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import DictionaryCard from '@/components/DictionaryCard.vue'
import Toast from '@/components/Toast.vue'
import { useArticles } from '@/composables/useArticles'
import { useWordBank } from '@/composables/useWordBank'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const articleId = route.params.id
const { token } = useAuth()

const {
  currentArticle,
  currentLoading,
  currentError,
  fetchArticle,
} = useArticles()

const { addWord } = useWordBank()

const currentEntry = ref({ word: '', definition: '', translation: '', defs: [] })

const toastOpen = ref(false)
const toastMsg = ref('')
const toastType = ref('success')
function notify(message, type='success') {
  toastMsg.value = message
  toastType.value = type
  toastOpen.value = false
  requestAnimationFrame(() => { toastOpen.value = true })
}

async function pingLastReading(seconds = 0) {
  if (!token.value) return
  try {
    await fetch(`/api/articles/${articleId}/reading-time`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify({ elapsed_time_seconds: seconds }),
    })
  } catch {}
}

onMounted(async () => {
  await fetchArticle(articleId)
  pingLastReading(0)
})

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

async function addToWordbank(entry) {
  if (!entry?.word) return

  if (!entry.defs || entry.defs.length === 0) {
    notify(`No definition found for “${entry.word}”. Not added.`, 'warn')
    return
  }

  const res = await addWord(entry.word)
  if (res?.ok) {
    notify(`Added “${entry.word}” to wordbank`)
  } else if (res?.reason === 'duplicate') {
    notify(`“${entry.word}” is already in your wordbank`, 'info')
  } else if (res?.reason === 'unauthorized') {
    notify('Please sign in to save words', 'warn')
  } else if (res?.reason === 'network') {
    notify('Network error—try again', 'error')
  } else {
    notify('Could not add word', 'error')
  }
}


</script>

<template>
  <div class="page">
    <NavBar />
    <main class="main">
      <section class="grid">
        <article class="reader">
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
.page{min-height:100vh;display:flex;flex-direction:column;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)}
.main{flex:1;max-width:1100px;margin:0 auto;padding:40px 20px}
.grid{display:grid;grid-template-columns:1.5fr .9fr;gap:24px;align-items:start}
.reader{background:#fff;border-radius:12px;border:2px solid #cfd4dc;box-shadow:0 10px 25px rgba(0,0,0,.1);padding:1.5rem;min-height:400px}
.title{text-align:center;margin:0 0 1rem;font-size:2.1rem}
.reader p{margin:1rem 0;color:#222;line-height:1.7}
.word{cursor:pointer;padding:0 .1rem}
.word:hover{background:rgba(102,126,234,.18);border-radius:4px}
.side{position:sticky;top:18px}
@media(max-width:960px){.grid{grid-template-columns:1fr}}
</style>
