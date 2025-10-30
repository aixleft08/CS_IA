import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

export function useWordBank() {
  const { token } = useAuth()

  const words = ref([])
  const loading = ref(false)
  const error = ref('')

  async function fetchWords() {
    if (!token.value) {
      words.value = []
      return
    }
    loading.value = true
    error.value = ''
    try {
      const res = await fetch('/api/words', {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token.value}`,
        },
      })
      const data = await res.json()
      if (!res.ok) {
        error.value = data.error || 'Failed to load words'
        words.value = []
        return
      }

      words.value = (data.words || []).map((w) => ({
        id: w.id,
        word: w.lemma,
        definition: w.definition || '', // we don't have this yet in backend
        translation: '',                // we don't have this yet either
      }))
    } catch (e) {
      error.value = 'Network error'
      words.value = []
    } finally {
      loading.value = false
    }
  }

  async function addWord(word) {
    if (!token.value) return
    const res = await fetch('/api/words', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify({ word }),
    })
    const data = await res.json()
    if (res.ok && data.word) {
      words.value.push({
        id: data.word.id,
        word: data.word.lemma,
        definition: '',
        translation: '',
      })
    } else {
        // duplicate word
    }
  }

  async function clearWords() {
    if (!token.value) return
    const res = await fetch('/api/words', {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    })
    if (res.ok) {
      words.value = []
    }
  }

  async function deleteWord(id) {
    if (!token.value) return
    const res = await fetch(`/api/words/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    })
    if (res.ok) {
      words.value = words.value.filter((w) => w.id !== id)
    }
  }

  return {
    words,
    loading,
    error,
    fetchWords,
    addWord,
    clearWords,
    deleteWord,
  }
}
