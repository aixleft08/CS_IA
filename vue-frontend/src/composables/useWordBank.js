import { ref } from "vue"
import { useAuth } from "@/composables/useAuth"
import { useDictionary } from "@/composables/useDictionary"
import { useTranslations } from "@/composables/useTranslations"

export function useWordBank() {
  const { token } = useAuth()
  const { lookup } = useDictionary()
  const { translate } = useTranslations()

  // UI state
  const words = ref([])
  const loading = ref(false)
  const error = ref("")

  // Get all saved words for the user
  async function fetchWords() {
    if (!token.value) {
      words.value = []
      return
    }

    loading.value = true
    error.value = ""

    try {
      const res = await fetch("/api/words", {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      const data = await res.json().catch(() => ({}))

      if (!res.ok) {
        error.value = data.error || "Failed to load words"
        words.value = []
        return
      }

      // Shape the backend data into what the UI uses
      const rows = (data.words || []).map((w) => ({
        id: w.id,
        word: w.lemma,
        translation: w.translation || "",
        entry: null,
        entryError: "",
      }))

      // If translation is missing, auto-fill it
      await Promise.all(
        rows.map(async (row) => {
          if (!row.translation && row.word) {
            const r = await translate(row.word, { source: "en", target: "zh" })
            if (r.ok) row.translation = r.translation
          }
        })
      )

      words.value = rows
    } catch {
      error.value = "Network error"
      words.value = []
    } finally {
      loading.value = false
    }
  }

  // Add a new word to the user's word bank
  async function addWord(word) {
    if (!token.value) return { ok: false, reason: "unauthorized" }

    try {
      const res = await fetch("/api/words", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token.value}`,
        },
        body: JSON.stringify({ word }),
      })
      const data = await res.json().catch(() => ({}))

      // Add new row locally if backend succeeded
      if (res.ok && data.word) {
        const row = {
          id: data.word.id,
          word: data.word.lemma,
          translation: data.word.translation || "",
          entry: null,
          entryError: "",
        }

        // Fill translation if backend didn't return one
        if (!row.translation && row.word) {
          const r = await translate(row.word, { source: "en", target: "zh" })
          if (r.ok) row.translation = r.translation
        }

        words.value.push(row)
        return { ok: true, id: row.id }
      }

      // Duplicate word
      if (res.status === 409) return { ok: false, reason: "duplicate" }
      return { ok: false, reason: data.error || "unknown" }
    } catch {
      return { ok: false, reason: "network" }
    }
  }

  // Clear the whole word bank
  async function clearWords() {
    if (!token.value) return
    const res = await fetch("/api/words", {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token.value}` },
    })
    if (res.ok) words.value = []
  }

  // Delete one word from the word bank
  async function deleteWord(id) {
    if (!token.value) return
    const res = await fetch(`/api/words/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token.value}` },
    })
    if (res.ok) words.value = words.value.filter((w) => w.id !== id)
  }

  // Load dictionary info for one row (only when needed)
  async function fetchEntry(row) {
    if (!row?.word) return
    if (row.entry) return // already fetched

    const result = await lookup(row.word)
    if (!result.ok) {
      row.entryError =
        result.reason === "no_def"
          ? "Definition not found"
          : result.reason === "network"
          ? "Error fetching definition"
          : "No definition available"
      return
    }

    row.entryError = ""
    row.entry = [result.entry]
  }

  return {
    words,
    loading,
    error,
    fetchWords,
    addWord,
    clearWords,
    deleteWord,
    fetchEntry,
  }
}
