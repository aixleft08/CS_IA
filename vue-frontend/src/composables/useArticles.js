import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

export function useArticles() {
  const { token } = useAuth()

  const articles = ref([])
  const loading = ref(false)
  const error = ref('')

  const currentArticle = ref(null)
  const currentLoading = ref(false)
  const currentError = ref('')

  async function fetchArticles(query = '') {
    if (!token.value) {
      articles.value = []
      return
    }
    loading.value = true
    error.value = ''
    try {
      const url = query
        ? `/api/articles/search?title=${encodeURIComponent(query)}`
        : '/api/articles/search'
      const res = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      })
      const data = await res.json()
      if (!res.ok) {
        error.value = data.error || 'Failed to load articles'
        articles.value = []
        return
      }

      articles.value = (data.results || []).map((a) => ({
        id: a.id,
        title: a.title,
        summary: a.excerpt || '',
        authors: a.authors || '',
        tags: a.tags || [],
        difficulty: a.difficulty ?? null,
        date: a.date || null,
      }))
    } catch (e) {
      error.value = 'Network error'
      articles.value = []
    } finally {
      loading.value = false
    }
  }

  async function fetchArticle(id) {
    if (!token.value) return
    currentLoading.value = true
    currentError.value = ''
    currentArticle.value = null
    try {
      const res = await fetch(`/api/articles/${id}`, {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      })
      const data = await res.json()
      if (!res.ok) {
        currentError.value = data.error || 'Failed to load article'
        return
      }
      currentArticle.value = data.article
    } catch (e) {
      currentError.value = 'Network error'
    } finally {
      currentLoading.value = false
    }
  }

  async function seedArticles() {
    if (!token.value) return
    loading.value = true
    error.value = ''
    try {
      const res = await fetch('/api/dev/seed-articles', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      })
      const data = await res.json()
      if (!res.ok) {
        error.value = data.error || 'Failed to seed'
      } else {
        // reload list after seeding
        await fetchArticles()
      }
    } catch (e) {
      error.value = 'Network error'
    } finally {
      loading.value = false
    }
  }

  async function logReadingTime(id, elapsedSeconds) {
    if (!token.value) return
    try {
      await fetch(`/api/articles/${id}/reading-time`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token.value}`,
        },
        body: JSON.stringify({ elapsed_time_seconds: elapsedSeconds }),
      })
      // you can ignore response for now
    } catch (e) {
      // swallow for now
    }
  }

  async function deleteArticle(id) {
    if (!token.value) return
    try {
      const res = await fetch(`/api/articles/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token.value}` },
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.error || 'Failed to delete')
      }
      articles.value = articles.value.filter(a => a.id !== id)
      if (currentArticle.value?.id === id) {
        currentArticle.value = null
      }
      return true
    } catch (e) {
      error.value = e.message || 'Network error'
      return false
    }
  }

  return {
    articles,
    loading,
    error,
    fetchArticles,
    seedArticles,
    currentArticle,
    currentLoading,
    currentError,
    fetchArticle,
    logReadingTime,
    deleteArticle,
  }
}
