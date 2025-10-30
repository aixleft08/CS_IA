<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import BaseInput from '@/components/BaseInput.vue'
import { useAuth } from '@/composables/useAuth'

const props = defineProps({
  mode: { type: String, default: 'sign-in' }, // 'sign-in' | 'sign-up'
})

const route = useRoute()
const { login, register } = useAuth()

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
})

const errors = reactive({
  username: '',
  password: '',
  confirmPassword: '',
})
const generalError = ref('')
const loading = ref(false)

function clearAll() {
  errors.username = ''
  errors.password = ''
  errors.confirmPassword = ''
  generalError.value = ''
}
function clearError(field) {
  errors[field] = ''
  if (!errors.username && !errors.password && !errors.confirmPassword) {
    generalError.value = ''
  }
}

async function onSubmit() {
  clearAll()

  if (!form.username.trim()) {
    errors.username = 'Username is required'
    return
  }
  if (!form.password) {
    errors.password = 'Password is required'
    return
  }
  if (props.mode === 'sign-up') {
    if (!form.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password'
      return
    }
    if (form.password !== form.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match'
      return
    }
  }

  loading.value = true

  const next = route.query.next || '/dashboard'

  try {
    let result
    if (props.mode === 'sign-in') {
      result = await login({
        name: form.username.trim(),
        password: form.password,
        redirectTo: next,
      })
    } else {
      result = await register({
        name: form.username.trim(),
        password: form.password,
        confirm_password: form.confirmPassword,
        redirectTo: next,
      })
    }

    if (!result.ok) {
      if (result.fieldErrors) {
        if (result.fieldErrors.username) errors.username = result.fieldErrors.username
        if (result.fieldErrors.password) errors.password = result.fieldErrors.password
        if (result.fieldErrors.confirmPassword)
          errors.confirmPassword = result.fieldErrors.confirmPassword
      }
      if (result.generalError) {
        generalError.value = result.generalError
      }
      return
    }

  } catch (e) {
    generalError.value = 'Network error. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="onSubmit" class="auth-form" novalidate>
    <BaseInput
      id="username"
      label="Username"
      v-model="form.username"
      placeholder="Your username"
      :error="errors.username"
      @clear="() => clearError('username')"
    />
    <BaseInput
      id="password"
      label="Password"
      type="password"
      v-model="form.password"
      placeholder="••••••••"
      :error="errors.password"
      @clear="() => clearError('password')"
    />
    <BaseInput
      v-if="mode === 'sign-up'"
      id="confirmPassword"
      label="Confirm Password"
      type="password"
      v-model="form.confirmPassword"
      placeholder="••••••••"
      :error="errors.confirmPassword"
      @clear="() => clearError('confirmPassword')"
    />

    <p v-if="generalError" class="general-error" role="alert">
      {{ generalError }}
    </p>

    <button class="cta" :disabled="loading">
      <span v-if="!loading">{{ mode === 'sign-up' ? 'Sign up' : 'Sign in' }}</span>
      <span v-else>{{ mode === 'sign-up' ? 'Signing up…' : 'Signing in…' }}</span>
    </button>

    <p class="switch">
      <span v-if="mode === 'sign-in'">New to Enlingo?&nbsp;</span>
      <span v-else>Already have an account?&nbsp;</span>
      <RouterLink :to="mode === 'sign-in' ? '/sign-up' : '/sign-in'">
        {{ mode === 'sign-in' ? 'Sign up' : 'Sign in' }}
      </RouterLink>
    </p>
  </form>
</template>

<style scoped>
.auth-form {
  margin-bottom: 1.5rem;
}
.general-error {
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  text-align: center;
  font-size: 0.875rem;
}
.cta {
  width: 100%;
  padding: 0.75rem;
  background: #333;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}
.cta:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}
.switch {
  margin-top: 0.75rem;
  text-align: center;
  color: #666;
}
.switch a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}
.switch a:hover {
  text-decoration: underline;
}
</style>
