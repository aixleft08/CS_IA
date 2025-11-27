import { ref } from 'vue'

const cache = new Map()

const MAX_ITEMS = 4
const MAX_LEN = 110

function cleanWord(raw) {
  return (raw || '').replace(/[.,!?;:()'"“”]/g, '').toLowerCase()
}
function truncate(s, n = MAX_LEN) {
  if (!s) return ''
  return s.length > n ? s.slice(0, n - 1) + '…' : s
}
function formatMeanings(entry) {
  if (!entry?.meanings?.length) return []
  const seenPos = new Set()
  const items = []
  for (const m of entry.meanings) {
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

export function useDictionary() {
  const loading = ref(false)

  async function lookup(rawWord) {
    const word = cleanWord(rawWord)
    if (!word) return { ok: false, reason: 'empty' }

    if (cache.has(word)) return cache.get(word)

    loading.value = true
    try {
      const res = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(word)}`)
      if (!res.ok) {
        const result = { ok: false, reason: 'no_def', entry: null, defs: [], preview: 'No definition found.' }
        cache.set(word, result)
        return result
      }
      const data = await res.json()
      const entry = data?.[0]
      const defs = formatMeanings(entry)
      const ok = defs.length > 0
      const result = {
        ok,
        reason: ok ? 'ok' : 'no_def',
        entry,
        defs,
        preview: buildPreview(defs),
        word
      }
      cache.set(word, result)
      return result
    } catch {
      const result = { ok: false, reason: 'network', entry: null, defs: [], preview: 'Error fetching definition.' }
      return result
    } finally {
      loading.value = false
    }
  }

  return { lookup, loading, cleanWord }
}
