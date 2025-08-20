<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const user = JSON.parse(localStorage.getItem('user') || '{}')

function handleSignOut() {
  localStorage.removeItem('authToken')
  localStorage.removeItem('user')
  router.push('/')
}
</script>

<template>
  <div class="dash">
    <!-- Top bar -->
    <header class="appbar">
      <div class="left">
        <router-link v-if="isAuthenticated" to="/dashboard" class="brand">Enlingo</router-link>
        <router-link v-else to="/" class="brand">Enlingo</router-link>
      </div>
      <div class="center">Wordbank</div>
      <div class="right">
        <button class="link-btn" @click="handleSignOut">Sign Out</button>
      </div>
    </header>

    <!-- Main content -->
    <main class="dash-main">
      <section class="panel">
        <h1>Welcome home<span v-if="user?.name">, {{ user.name }}</span></h1>
        <p class="sub">You were reading <router-link to="/search" class="inline-link">xxx</router-link>.</p>

        <div class="divider"></div>

        <p class="progress-title">Your progress:</p>
        <div class="metrics">
          <div class="metric">
            <span class="label">Minutes read:</span>
            <span class="value">#</span>
          </div>
          <div class="metric">
            <span class="label">Wordbank size:</span>
            <span class="value">#</span>
          </div>
        </div>

        <router-link to="/search" class="primary-btn">Start reading</router-link>
      </section>

      <!-- child routes render here if you need -->
      <router-view />
    </main>
  </div>
</template>

<style scoped>
/* Page layout */
.dash {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  /* keep the app-wide gradient so it matches SignIn/SignUp/Home */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Top bar */
.appbar {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: saturate(180%) blur(8px);
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.appbar .left { justify-self: start; }
.appbar .center { justify-self: center; font-weight: 700; color: #333; }
.appbar .right { justify-self: end; }

.brand {
  text-decoration: none;
  font-weight: 700;
  color: #333;
}

/* Buttons in the bar */
.link-btn {
  border: none;
  border-radius: 6px;
  padding: 0.5rem 0.9rem;
  background: #333;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}
.link-btn:hover { background: #555; }

/* Main area */
.dash-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

/* Central panel (card) */
.panel {
  width: 100%;
  max-width: 800px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  padding: 2rem 2.25rem;
  text-align: center;
}

.panel h1 {
  font-size: 1.5rem;
  color: #111;
  margin: 0;
}

.sub {
  margin: 0.25rem 0 0;
  color: #666;
}

.inline-link {
  color: #667eea;
  text-decoration: none;
}
.inline-link:hover { text-decoration: underline; }

.divider {
  height: 1px;
  background: #e1e5e9;
  margin: 1.25rem 0 1.5rem;
}

.progress-title {
  color: #333;
  margin-bottom: 0.75rem;
}

/* Metrics */
.metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem 2rem;
  justify-items: center;
  margin-bottom: 1.75rem;
}
.metric { display: flex; gap: 0.5rem; }
.label { color: #555; }
.value { font-weight: 700; color: #111; }

/* CTA */
.primary-btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 700;
  text-decoration: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  transition: opacity 0.2s ease;
}
.primary-btn:hover { opacity: 0.9; }

/* Responsive */
@media (max-width: 600px) {
  .panel { padding: 1.25rem; margin: 0 1rem; }
  .metrics { grid-template-columns: 1fr; }
}
</style>
