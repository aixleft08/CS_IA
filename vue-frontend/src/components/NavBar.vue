<script setup>
import { RouterLink, useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const { isAuthenticated, signOut } = useAuth()
const route = useRoute()

function isActive(path) {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<template>
  <header
    class="appbar"
    :class="{ 'no-center': !isAuthenticated, guest: !isAuthenticated }"
  >
    <div class="left">
      <RouterLink to="/" class="brand">Enlingo</RouterLink>
    </div>

    <nav v-if="isAuthenticated" class="center">
      <RouterLink
        to="/dashboard"
        class="tab"
        :class="{ active: isActive('/dashboard') }"
      >
        Dashboard
      </RouterLink>

      <RouterLink
        to="/search"
        class="tab"
        :class="{ active: isActive('/search') }"
      >
        Articles
      </RouterLink>

      <RouterLink
        to="/wordbank"
        class="tab"
        :class="{ active: isActive('/wordbank') }"
      >
        Wordbank
      </RouterLink>

      <RouterLink
        to="/quiz"
        class="tab"
        :class="{ active: isActive('/quiz') }"
      >
        Quiz
      </RouterLink>
    </nav>

    <div class="right">
      <button
        v-if="isAuthenticated"
        class="btn"
        @click="signOut"
      >
        Sign Out
      </button>
      <RouterLink v-else to="/sign-in" class="btn guest-btn">
        Sign In
      </RouterLink>
    </div>
  </header>
</template>

<style scoped>
.appbar{
  position: sticky; top: 0; z-index: 40;
  display:grid; grid-template-columns:1fr auto 1fr; align-items:center;
  gap:1rem; padding:.6rem .9rem;
  background: linear-gradient(0deg, rgba(255,255,255,.82), rgba(255,255,255,.82));
  backdrop-filter: saturate(180%) blur(10px);
  border-bottom: 1px solid rgba(0,0,0,.06);
}

.appbar.no-center{
  grid-template-columns: 1fr auto;
}

.appbar.guest{
  padding:.9rem 1rem;
  border-bottom: 1.5px solid rgba(0,0,0,.07);
}

.left{justify-self:start}
.center{
  justify-self:center; display:flex; gap:.5rem; padding:.25rem; border-radius:999px;
  background: rgba(255,255,255,.6);
  box-shadow: 0 4px 16px rgba(0,0,0,.06) inset, 0 2px 10px rgba(0,0,0,.05);
}
.right{justify-self:end}

.brand{
  font-weight:800; letter-spacing:.2px;
  text-decoration:none; color:#111; font-size:1.05rem;
}

.tab{
  position:relative;
  padding:.45rem .8rem; border-radius:10px; text-decoration:none;
  color:#333; font-weight:700; font-size:.95rem;
  transition: background .15s ease;
}
.tab:hover{ background: rgba(102,126,234,.10) }
.tab.active{ color:#111; background: rgba(102,126,234,.16) }
.tab.active::after{
  content:''; position:absolute; left:10px; right:10px; bottom:6px; height:2px;
  background: linear-gradient(90deg, #667eea, #764ba2); border-radius:2px;
}

.btn{
  border:none; border-radius:10px; padding:.5rem .9rem; font-weight:700;
  background:#111; color:#fff; cursor:pointer;
  box-shadow: 0 6px 14px rgba(0,0,0,.12);
}
.btn:hover{ background:#323232 }

.guest .guest-btn{
  padding:.38rem .7rem;
  font-size:.9rem;
  border-radius:8px;
  box-shadow: 0 4px 10px rgba(0,0,0,.10);
}

@media (max-width: 720px){
  .appbar{ gap:.5rem; padding:.5rem .7rem }
  .appbar.guest{ padding:.75rem .8rem }
  .center{ display:none }
}
</style>
