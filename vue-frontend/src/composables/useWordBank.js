import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useDictionary } from '@/composables/useDictionary'

export function useWordBank() {
  const { token } = useAuth()
  const { lookup } = useDictionary()

  const words = ref([])
  const loading = ref(false)
  const error = ref('')

  async function fetchWords() {
    if (!token.value) { words.value = []; return }
    loading.value = true; error.value = ''
    try {
      const res = await fetch('/api/words', { headers: { Authorization: `Bearer ${token.value}` } })
      const data = await res.json()
      if (!res.ok) { error.value = data.error || 'Failed to load words'; words.value = []; return }
      words.value = (data.words || []).map(w => ({ id: w.id, word: w.lemma, entry: null, entryError: '' }))
    } catch {
      error.value = 'Network error'; words.value = []
    } finally { loading.value = false }
  }

  async function addWord(word) {
    if (!token.value) return { ok: false, reason: 'unauthorized' }
    try {
      const res = await fetch('/api/words', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token.value}` },
        body: JSON.stringify({ word }),
      })
      const data = await res.json()
      if (res.ok && data.word) {
        words.value.push({ id: data.word.id, word: data.word.lemma, entry: null, entryError: '' })
        return { ok: true }
      } else if (res.status === 409) return { ok: false, reason: 'duplicate' }
      return { ok: false, reason: data.error || 'unknown' }
    } catch { return { ok: false, reason: 'network' } }
  }

  async function clearWords() {
    if (!token.value) return
    const res = await fetch('/api/words', { method: 'DELETE', headers: { Authorization: `Bearer ${token.value}` } })
    if (res.ok) words.value = []
  }

  async function deleteWord(id) {
    if (!token.value) return
    const res = await fetch(`/api/words/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token.value}` } })
    if (res.ok) words.value = words.value.filter(w => w.id !== id)
  }

  async function fetchEntry(row) {
    if (!row?.word) return
    if (row.entry) return
    const result = await lookup(row.word)
    if (!result.ok) {
      row.entryError = result.reason === 'no_def' ? 'Definition not found' :
                       result.reason === 'network' ? 'Error fetching definition' :
                       'No definition available'
      return
    }
    row.entryError = ''
    row.entry = [result.entry]
  }

  return { words, loading, error, fetchWords, addWord, clearWords, deleteWord, fetchEntry }
}
