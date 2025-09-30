<script setup>
import { reactive, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import BaseInput from '@/components/BaseInput.vue'
import { useAuth } from '@/composables/useAuth'

const props = defineProps({ mode: { type: String, default: 'sign-in' } }) // 'sign-in' | 'sign-up'
const router = useRouter()
const { setAuth } = useAuth()

const form = reactive({ username:'', password:'', confirmPassword:'' })
const errors = reactive({ username:'', password:'', confirmPassword:'' })
const generalError = ref('')
const loading = ref(false)

function clearError(field){ errors[field]=''; generalError.value='' }
function clearAll(){ errors.username=''; errors.password=''; errors.confirmPassword=''; generalError.value='' }

function validate(){
  let ok = true; clearAll()
  if(!form.username.trim()){ errors.username='Username is required'; ok=false }
  else if(props.mode==='sign-up' && form.username.length<3){ errors.username='Username must be at least 3 characters'; ok=false }
  if(!form.password){ errors.password='Password is required'; ok=false }
  else if(props.mode==='sign-up' && form.password.length<6){ errors.password='Password must be at least 6 characters'; ok=false }
  if(props.mode==='sign-up'){
    if(!form.confirmPassword){ errors.confirmPassword='Please confirm your password'; ok=false }
    else if(form.password!==form.confirmPassword){ errors.confirmPassword='Passwords do not match'; ok=false }
  }
  return ok
}

async function onSubmit(){
  if(!validate()) return
  loading.value = true; generalError.value = ''
  try{
    const url = props.mode==='sign-up' ? '/api/auth/register' : '/api/auth/login'
    const body = props.mode==='sign-up'
      ? { name: form.username, password: form.password, confirm_password: form.confirmPassword }
      : { name: form.username, password: form.password }

    const res = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body) })
    const data = await res.json()

    if(res.ok){
      setAuth(data.token || 'dummy-token', data.user || { name: form.username })
      router.push('/dashboard')
    }else{
      if(res.status===409 && (data.error||'').includes('username')) errors.username='Username already exists'
      else generalError.value = data.error || 'Something went wrong.'
    }
  }catch(e){
    generalError.value = 'Network error. Please try again.'
  }finally{
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="onSubmit" class="auth-form" novalidate>
    <BaseInput id="username" label="Username" v-model="form.username" placeholder="Your username"
               :error="errors.username" @clear="() => clearError('username')" />
    <BaseInput id="password" label="Password" type="password" v-model="form.password" placeholder="••••••••"
               :error="errors.password" @clear="() => clearError('password')" />
    <BaseInput v-if="mode==='sign-up'" id="confirmPassword" label="Confirm Password" type="password"
               v-model="form.confirmPassword" placeholder="••••••••"
               :error="errors.confirmPassword" @clear="() => clearError('confirmPassword')" />

    <p v-if="generalError" class="general-error" role="alert">{{ generalError }}</p>

    <button class="cta" :disabled="loading">
      <span v-if="!loading">{{ mode==='sign-up' ? 'Sign up' : 'Sign in' }}</span>
      <span v-else>{{ mode==='sign-up' ? 'Signing up…' : 'Signing in…' }}</span>
    </button>

    <p class="switch">
      <span v-if="mode==='sign-in'">New to Enlingo?</span>
      <span v-else>Already have an account?</span>
      <RouterLink :to="mode==='sign-in' ? '/sign-up' : '/sign-in'">
        {{ mode==='sign-in' ? 'Sign up' : 'Sign in' }}
      </RouterLink>
    </p>
  </form>
</template>

<style scoped>
.auth-form{margin-bottom:1.5rem}
.general-error{background:#fee;border:1px solid #fcc;color:#c33;padding:.75rem;border-radius:6px;margin-bottom:1rem;text-align:center;font-size:.875rem}
.cta{width:100%;padding:.75rem;background:#333;color:#fff;border:none;border-radius:6px;font-size:1rem;font-weight:600;cursor:pointer}
.cta:disabled{background:#95a5a6;cursor:not-allowed}
.switch{margin-top:.75rem;text-align:center;color:#666}
.switch a{color:#667eea;text-decoration:none;font-weight:500}
.switch a:hover{text-decoration:underline}
</style>
