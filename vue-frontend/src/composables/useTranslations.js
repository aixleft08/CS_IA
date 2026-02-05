import { ref } from "vue"
import { useAuth } from "@/composables/useAuth"
import { HashTable } from "@/utils/hashTable"

const CACHE_CAPACITY = 509

// Cache longer for good results, short for errors
const TTL_OK_MS = 24 * 60 * 60 * 1000
const TTL_ERR_MS = 2 * 60 * 1000

// Translation cache
let cache = new HashTable(CACHE_CAPACITY)
const inFlight = new Map()

// Trim input so " hi " and "hi" behave the same
function normText(text) {
  return (text || "").trim()
}

// Unique key per (source, target, text)
function makeKey(text, source, target) {
  const t = normText(text).toLowerCase()
  return `${source}:${target}:${t}`
}

// Read from cache and drop expired entries
function cacheGet(key) {
  try {
    const record = cache.get(key)
    if (!record) return null

    if (record.expiresAt && Date.now() > record.expiresAt) {
      try { cache.removeKey(key) } catch {}
      return null
    }

    return record.value
  } catch {
    return null
  }
}

// Reset cache if it is full
function cacheSet(key, value, ttlMs) {
  const record = { value, expiresAt: Date.now() + ttlMs }

  try {
    cache.set(key, record)
    return
  } catch (e) {
    cache = new HashTable(CACHE_CAPACITY)
    try { cache.set(key, record) } catch {}
  }
}

export function useTranslations() {
  const { token } = useAuth()
  const loading = ref(false)

  // Translate text via backend API with caching + dedupe
  async function translate(text, opts = {}) {
    const source = opts.source || "en"
    const target = opts.target || "zh"
    const normalized = normText(text)

    // Quick rejects
    if (!normalized) return { ok: false, reason: "empty", translation: "" }
    if (!token.value) return { ok: false, reason: "unauthorized", translation: "" }

    const key = makeKey(normalized, source, target)

    // Cached answer
    const cached = cacheGet(key)
    if (cached) return { ...cached, cached: true }

    // If same request is already running, reuse it
    if (inFlight.has(key)) {
      return inFlight.get(key)
    }

    const p = (async () => {
      loading.value = true
      try {
        // Build request URL
        const url =
          `/api/translations?text=${encodeURIComponent(normalized)}` +
          `&source=${encodeURIComponent(source)}` +
          `&target=${encodeURIComponent(target)}`

        const res = await fetch(url, {
          headers: {
            Authorization: `Bearer ${token.value}`,
          },
        })

        const data = await res.json().catch(() => ({}))

        if (!res.ok) {
          const result = {
            ok: false,
            reason: res.status === 401 ? "unauthorized" : "error",
            translation: "",
          }
          cacheSet(key, result, TTL_ERR_MS)
          return result
        }

        const translation = (data.translation || "").trim()
        const ok = !!translation

        const result = {
          ok,
          reason: ok ? "ok" : "no_translation",
          translation,
          source_lang: data.source_lang || source,
          target_lang: data.target_lang || target,
        }

        cacheSet(key, result, ok ? TTL_OK_MS : TTL_ERR_MS)
        return result
      } catch {
        const result = { ok: false, reason: "network", translation: "" }
        cacheSet(key, result, TTL_ERR_MS)
        return result
      } finally {
        loading.value = false
        inFlight.delete(key)
      }
    })()

    inFlight.set(key, p)
    return p
  }

  return { translate, loading }
}
