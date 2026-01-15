import { ref } from "vue"
import { HashTable } from "@/utils/hashTable"

const cache = new HashTable(1021)
const inFlight = new HashTable(1021)

const MAX_ITEMS = 4
const MAX_LEN = 110

const TTL_OK_MS = 24 * 60 * 60 * 1000
const TTL_NO_DEF_MS = 6 * 60 * 60 * 1000
const TTL_NETWORK_MS = 2 * 60 * 1000

function nowMs() {
  return Date.now()
}

function cleanWord(raw) {
  return (raw || "").replace(/[.,!?;:()'"“”]/g, "").toLowerCase()
}

function truncate(s, n = MAX_LEN) {
  if (!s) return ""
  return s.length > n ? s.slice(0, n - 1) + "…" : s
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
  if (!defs?.length) return "No definition found."
  return defs.map((d) => `${d.pos}: ${d.text}`).join("; ")
}

function cacheGet(table, key) {
  try {
    return table.get(key)
  } catch {
    return null
  }
}

function getCachedResult(key) {
  const item = cacheGet(cache, key)
  if (!item) return null

  if (!item.expiresAt || !("value" in item)) return item

  if (item.expiresAt <= nowMs()) {
    try {
      cache.removeKey(key)
    } catch {}
    return null
  }
  return item.value
}

function ttlForResult(result) {
  if (!result || result.ok) return TTL_OK_MS
  if (result.reason === "no_def") return TTL_NO_DEF_MS
  if (result.reason === "network") return TTL_NETWORK_MS
  return TTL_NETWORK_MS
}

function cacheSetResult(key, result) {
  const ttl = ttlForResult(result)
  const entry = { value: result, expiresAt: nowMs() + ttl }

  try {
    cache.set(key, entry)
  } catch {
    try {
      cache._arr = new Array(cache._cap).fill(null)
      cache._size = 0
      cache.set(key, entry)
    } catch {}
  }
}

export function useDictionary() {
  const loading = ref(false)

  async function lookup(rawWord) {
    const word = cleanWord(rawWord)
    if (!word) return { ok: false, reason: "empty" }

    const cached = getCachedResult(word)
    if (cached) return cached

    const existingPromise = cacheGet(inFlight, word)
    if (existingPromise) return await existingPromise

    loading.value = true

    const p = (async () => {
      try {
        const res = await fetch(
          `https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(word)}`
        )

        if (!res.ok) {
          const result = {
            ok: false,
            reason: "no_def",
            entry: null,
            defs: [],
            preview: "No definition found.",
            word,
          }
          cacheSetResult(word, result)
          return result
        }

        const data = await res.json()
        const entry = data?.[0]
        const defs = formatMeanings(entry)
        const ok = defs.length > 0

        const result = {
          ok,
          reason: ok ? "ok" : "no_def",
          entry,
          defs,
          preview: buildPreview(defs),
          word,
        }

        cacheSetResult(word, result)
        return result
      } catch {
        const result = {
          ok: false,
          reason: "network",
          entry: null,
          defs: [],
          preview: "Error fetching definition.",
          word,
        }
        cacheSetResult(word, result)
        return result
      } finally {
        try {
          inFlight.removeKey(word)
        } catch {}
        loading.value = false
      }
    })()

    try {
      inFlight.set(word, p)
    } catch {}

    return await p
  }

  return { lookup, loading, cleanWord }
}
