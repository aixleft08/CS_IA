import { computed } from 'vue'
import { useRouter } from 'vue-router'


export function useAuth() {
  const router = useRouter()

  const user = computed(() => {
    try { return JSON.parse(localStorage.getItem('user') || '{}') } catch { return {} }
  })
  const token = computed(() => localStorage.getItem('authToken') || '')
  const isAuthenticated = computed(() => !!token.value)

  function setAuth(t, u) {
    if (t) localStorage.setItem('authToken', t)
    if (u) localStorage.setItem('user', JSON.stringify(u))
  }

  function signOut() {
    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
    router.push('/sign-in')
  }

  return { user, token, isAuthenticated, setAuth, signOut }
}
