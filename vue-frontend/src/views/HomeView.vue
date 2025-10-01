<script setup>
import { computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import NavBar from '@/components/NavBar.vue'

const { isAuthenticated } = useAuth()
const authed = computed(() => isAuthenticated.value)
</script>

<template>
  <div class="home-container">
    <NavBar />

    <div class="home-card">
      <div class="home-header">
        <h1>Enlingo</h1>
        <h2>Your personal language companion</h2>
      </div>

      <div class="divider"></div>

      <div class="home-content">
        <p v-if="!authed">Sign up and start your journey</p>
        <p v-else>Welcome back</p>
      </div>

      <div class="home-actions">
        <router-link v-if="!authed" to="/sign-up" class="home-button">Sign Up</router-link>
        <router-link v-if="!authed" to="/sign-in" class="home-button secondary">Sign In</router-link>
        <router-link v-if="authed" to="/dashboard" class="home-button">Go to Dashboard</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container{min-height:100vh;display:flex;flex-direction:column;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:20px}
.home-card{background:#fff;padding:2.5rem;border-radius:12px;box-shadow:0 10px 25px rgba(0,0,0,.1);width:100%;max-width:450px;text-align:center;margin:40px auto 0}
.home-header{margin-bottom:1.5rem}
.home-header h1{color:#333;font-size:2rem;font-weight:700;margin-bottom:.5rem}
.home-header h2{color:#666;font-size:1.25rem;margin:0}
.divider{height:1px;background:#e1e5e9;margin:1.5rem 0}
.home-content{margin-bottom:2rem;color:#555;font-size:1.1rem}
.home-actions{display:flex;flex-direction:column;gap:1rem}
.home-button{display:block;padding:.75rem;border-radius:6px;font-size:1rem;font-weight:600;text-decoration:none;text-align:center;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;transition:opacity .3s}
.home-button:hover{opacity:.9}
.home-button.secondary{background:#333}
.home-button.secondary:hover{background:#555}
@media (max-width:480px){.home-card{padding:1.5rem;margin:1rem}.home-header h1{font-size:1.75rem}.home-header h2{font-size:1.1rem}}
</style>
