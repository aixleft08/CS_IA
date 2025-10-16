import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

export function useAuth() {
  const router = useRouter()

  const user = ref(loadUser())
  const token = ref(localStorage.getItem('authToken') || '')

  const isAuthenticated = computed(() => !!token.value)

  function loadUser() {
    try {
      const raw = localStorage.getItem('user')
      return raw ? JSON.parse(raw) : null
    } catch {
      return null
    }
  }

  function setAuth(t, u) {
    if (t) {
      localStorage.setItem('authToken', t)
      token.value = t
    }
    if (u) {
      localStorage.setItem('user', JSON.stringify(u))
      user.value = u
    }
  }

  async function login(name, password) {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, password }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Login failed')
    setAuth(data.token, data.user)
    // optional: navigate after login
    router.push('/dashboard')
  }

  async function register(name, password, confirm_password) {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, password, confirm_password }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Register failed')
    setAuth(data.token, data.user)
    router.push('/dashboard')
  }

  function signOut() {
    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
    token.value = ''
    user.value = null
    router.push('/sign-in')
  }

  return { user, token, isAuthenticated, setAuth, login, register, signOut }
}
