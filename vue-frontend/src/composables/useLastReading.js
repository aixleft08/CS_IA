import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

export function useLastReading() {
  const { token } = useAuth()
  const last = ref(null)
  const loading = ref(false)
  const error = ref('')

  async function fetchLastReading() {
    if (!token.value) { last.value = null; return }
    loading.value = true; error.value = ''
    try {
      const res = await fetch('/api/users/last-reading', {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to load')
      last.value = data.last
    } catch (e) {
      error.value = e.message || 'Network error'
      last.value = null
    } finally {
      loading.value = false
    }
  }

  return { last, loading, error, fetchLastReading }
}
