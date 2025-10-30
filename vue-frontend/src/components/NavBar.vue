<script setup>
import { RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const { isAuthenticated, signOut } = useAuth()
</script>

<template>
  <header class="appbar">
    <div class="left">
      <RouterLink :to="isAuthenticated ? '/dashboard' : '/'" class="brand">Enlingo</RouterLink>
    </div>
    <div class="center">
      <RouterLink v-if="isAuthenticated" to="/wordbank" class="brand">Wordbank</RouterLink>
      <span v-else class="brand" style="opacity:.4;cursor:not-allowed">Wordbank</span>
    </div>
    <div class="right">
      <button v-if="isAuthenticated" class="link-btn" @click="signOut">Sign Out</button>
      <RouterLink v-else to="/sign-in" class="link-btn">Sign In</RouterLink>
    </div>
  </header>
</template>

<style scoped>
.appbar{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:1rem;padding:.75rem 1rem;background:rgba(255,255,255,.9);
backdrop-filter:saturate(180%) blur(8px);box-shadow:0 2px 12px rgba(0,0,0,.06)}
.appbar .left{justify-self:start}.appbar .center{justify-self:center;font-weight:700;color:#333}.appbar .right{justify-self:end}
.brand{text-decoration:none;font-weight:700;color:#333}
.link-btn{border:none;border-radius:6px;padding:.5rem .9rem;background:#333;color:#fff;font-weight:600;cursor:pointer}
.link-btn:hover{background:#555}
</style>
