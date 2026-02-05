import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

// Handles article data and API calls
export function useArticles() {
  // Auth token from login
  const { token } = useAuth()

  // Article list state
  const articles = ref([])
  const loading = ref(false)
  const error = ref('')

  // Single article state
  const currentArticle = ref(null)
  const currentLoading = ref(false)
  const currentError = ref('')

  // Load articles (supports title or tag search)
  async function fetchArticles(query = '') {
    // No token = no data
    if (!token.value) {
      articles.value = []
      return
    }

    const raw = (query || '').trim()

    let title = ''
    let tag = ''

    // tag:science or #science
    if (raw.toLowerCase().startsWith('tag:')) {
      tag = raw.slice(4).trim()
    } else if (raw.startsWith('#')) {
      tag = raw.slice(1).trim()
    } else {
      title = raw
    }

    loading.value = true
    error.value = ''

    try {
      // Build query params
      const params = new URLSearchParams()
      if (title) params.set('title', title)
      if (tag) params.set('tag', tag)

      const url =
        params.toString()
          ? `/api/articles/search?${params.toString()}`
          : '/api/articles/search'

      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token.value}` },
      })

      const data = await res.json()

      if (!res.ok) {
        error.value = data.error || 'Failed to load articles'
        articles.value = []
        return
      }

      // Keep only what the UI needs
      articles.value = (data.results || []).map(a => ({
        id: a.id,
        title: a.title,
        summary: a.excerpt || '',
        authors: a.authors || '',
        tags: a.tags || [],
        difficulty: a.difficulty ?? null,
        date: a.date || null,
      }))
    } catch {
      error.value = 'Network error'
      articles.value = []
    } finally {
      loading.value = false
    }
  }

  // Load one article by id
  async function fetchArticle(id) {
    if (!token.value) return

    currentLoading.value = true
    currentError.value = ''
    currentArticle.value = null

    try {
      const res = await fetch(`/api/articles/${id}`, {
        headers: { Authorization: `Bearer ${token.value}` },
      })

      const data = await res.json()

      if (!res.ok) {
        currentError.value = data.error || 'Failed to load article'
        return
      }

      currentArticle.value = data.article
    } catch {
      currentError.value = 'Network error'
    } finally {
      currentLoading.value = false
    }
  }

  // Dev helper to add sample articles
  async function seedArticles() {
    if (!token.value) return

    loading.value = true
    error.value = ''

    try {
      const res = await fetch('/api/dev/seed-articles', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token.value}` },
      })

      const data = await res.json()

      if (!res.ok) {
        error.value = data.error || 'Failed to seed'
      } else {
        fetchArticles()
      }
    } catch {
      error.value = 'Network error'
    } finally {
      loading.value = false
    }
  }

  // Send reading time to backend
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
    } catch {
      // ignore
    }
  }

  // Delete article and update local state
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
