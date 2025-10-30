//api calls of user authentication, give output to forntend components
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

  async function login({ name, password, redirectTo = '/dashboard' }) {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, password }),
    })
    const data = await res.json().catch(() => ({}))

    if (!res.ok) {
      // 400 from backend = missing fields
      if (res.status === 400) {
        return {
          ok: false,
          fieldErrors: {
            username: !name?.trim() ? 'Username is required' : '',
            password: !password ? 'Password is required' : '',
          },
          generalError: data.error || 'Please check your inputs.',
        }
      }
      // 401 invalid credentials
      if (res.status === 401) {
        return {
          ok: false,
          fieldErrors: {
            username: '',
            password: '',
          },
          generalError: data.error || 'Invalid username or password.',
        }
      }
      return {
        ok: false,
        fieldErrors: {},
        generalError: data.error || 'Login failed.',
      }
    }

    setAuth(data.token, data.user)
    if (redirectTo) router.push(redirectTo)
    return { ok: true, user: data.user }
  }

  async function register({ name, password, confirm_password, redirectTo = '/dashboard' }) {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, password, confirm_password }),
    })
    const data = await res.json().catch(() => ({}))

    if (!res.ok) {
      // 409 username exists
      if (res.status === 409) {
        return {
          ok: false,
          fieldErrors: {
            username: 'Username already exists',
            password: '',
            confirmPassword: '',
          },
          generalError: '',
        }
      }

      // 400 missing / mismatch
      if (res.status === 400) {
        const msg = data.error || 'Please check your inputs.'
        return {
          ok: false,
          fieldErrors: {
            username: msg.toLowerCase().includes('username') ? msg : '',
            password: msg.toLowerCase().includes('password') ? msg : '',
            confirmPassword: msg.toLowerCase().includes('confirm') ? msg : '',
          },
          generalError: msg,
        }
      }

      return {
        ok: false,
        fieldErrors: {},
        generalError: data.error || 'Registration failed.',
      }
    }

    setAuth(data.token, data.user)
    if (redirectTo) router.push(redirectTo)
    return { ok: true, user: data.user }
  }

  async function signOut() {
    try {
      await fetch('/api/auth/logout', { method: 'POST' })
    } catch (_) {}

    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
    token.value = ''
    user.value = null
    router.push('/sign-in')
  }

  async function fetchMe() {
    if (!token.value) return null

    const res = await fetch('/api/users/me', {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token.value}`,
      },
    })

    if (res.status === 401) {
      signOut()
      return null
    }

    const data = await res.json().catch(() => ({}))
    if (res.ok && data.user) {
      localStorage.setItem('user', JSON.stringify(data.user))
      user.value = data.user
      return data.user
    }

    return null
  }

  function isLoggedIn() {
    return !!token.value
  }


  return {
    user,
    token,
    isAuthenticated,
    setAuth,
    login,
    register,
    signOut,
    fetchMe,
    isLoggedIn,
  }

}
