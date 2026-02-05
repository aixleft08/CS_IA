import { ref } from "vue"
import { HashTable } from "@/utils/hashTable"

// Cache for finished lookups
const cache = new HashTable(1021)
// Tracks ongoing requests so we don’t fetch the same word twice
const inFlight = new HashTable(1021)

// Limits for how many definitions + how long each one can be
const MAX_ITEMS = 4
const MAX_LEN = 110

// Cache time depending on result type
const TTL_OK_MS = 24 * 60 * 60 * 1000
const TTL_NO_DEF_MS = 6 * 60 * 60 * 1000
const TTL_NETWORK_MS = 2 * 60 * 1000

// Current time helper
function nowMs() {
  return Date.now()
}

// Basic cleanup: remove punctuation + lowercase
function cleanWord(raw) {
  return (raw || "").replace(/[.,!?;:()'"“”]/g, "").toLowerCase()
}

// Cut long strings for UI preview
function truncate(s, n = MAX_LEN) {
  if (!s) return ""
  return s.length > n ? s.slice(0, n - 1) + "…" : s
}

// Turn API meanings into a small list (1 per part of speech)
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

// One-line string used in the UI
function buildPreview(defs) {
  if (!defs?.length) return "No definition found."
  return defs.map((d) => `${d.pos}: ${d.text}`).join("; ")
}

// Safe wrapper so hash table errors don’t break the app
function cacheGet(table, key) {
  try {
    return table.get(key)
  } catch {
    return null
  }
}

// Get cached result if it exists and hasn’t expired
function getCachedResult(key) {
  const item = cacheGet(cache, key)
  if (!item) return null

  // Backwards-safe: if entry isn’t the expected shape, just return it
  if (!item.expiresAt || !("value" in item)) return item

  // Expired entry: remove it and treat as miss
  if (item.expiresAt <= nowMs()) {
    try {
      cache.removeKey(key)
    } catch {}
    return null
  }
  return item.value
}

// Pick cache lifetime based on what happened
function ttlForResult(result) {
  if (!result || result.ok) return TTL_OK_MS
  if (result.reason === "no_def") return TTL_NO_DEF_MS
  if (result.reason === "network") return TTL_NETWORK_MS
  return TTL_NETWORK_MS
}

// Save result into cache (and recover if cache got corrupted/full)
function cacheSetResult(key, result) {
  const ttl = ttlForResult(result)
  const entry = { value: result, expiresAt: nowMs() + ttl }

  try {
    cache.set(key, entry)
  } catch {
    // Reset cache and try again (simple fallback)
    try {
      cache._arr = new Array(cache._cap).fill(null)
      cache._size = 0
      cache.set(key, entry)
    } catch {}
  }
}

export function useDictionary() {
  // Global "lookup running" flag for UI
  const loading = ref(false)

  // Look up a word using cache + in-flight dedupe
  async function lookup(rawWord) {
    const word = cleanWord(rawWord)
    if (!word) return { ok: false, reason: "empty" }

    // Fast path: cached answer
    const cached = getCachedResult(word)
    if (cached) return cached

    // If already fetching this word, reuse the same promise
    const existingPromise = cacheGet(inFlight, word)
    if (existingPromise) return await existingPromise

    loading.value = true

    // Do the fetch inside a promise so we can share it via inFlight
    const p = (async () => {
      try {
        const res = await fetch(
          // Dictionaryapi.dev
          `https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(word)}`
        )

        // API returns non-OK when word doesn’t exist
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
        // Network or JSON error
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
        // Always clear in-flight entry and stop spinner
        try {
          inFlight.removeKey(word)
        } catch {}
        loading.value = false
      }
    })()

    // Store promise so other calls can reuse it
    try {
      inFlight.set(word, p)
    } catch {}

    return await p
  }

  return { lookup, loading, cleanWord }
}
