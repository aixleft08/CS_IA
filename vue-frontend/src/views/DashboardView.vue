<script setup>
import NavBar from '@/components/NavBar.vue'
import { useAuth } from '@/composables/useAuth'
import { useLastReading } from '@/composables/useLastReading'
import { onMounted, computed } from 'vue'

const { user, fetchMe, isLoggedIn } = useAuth()
const { last, loading, fetchLastReading } = useLastReading()

onMounted(async () => {
  if (isLoggedIn()) {
    await fetchMe()
    await fetchLastReading()
  }
})

const lastHref = computed(() => last.value ? `/read/${last.value.id}` : '/search')
const lastText = computed(() => last.value?.title || '—')
</script>

<template>
  <div class="dash">
    <NavBar />

    <main class="dash-main">
      <section class="panel">
        <h1>Welcome home<span v-if="user?.name">, {{ user.name }}</span></h1>

        <p class="sub" v-if="loading">You were reading …</p>
        <p class="sub" v-else>
          You were reading
          <router-link :to="lastHref" class="inline-link">
            {{ lastText }}
          </router-link>.
        </p>

        <div class="divider"></div>

        <p class="progress-title">Your progress:</p>
        <div class="metrics">
          <div class="metric"><span class="label">Minutes read:</span><span class="value">#</span></div>
          <div class="metric"><span class="label">Wordbank size:</span><span class="value">#</span></div>
        </div>

        <router-link to="/search" class="primary-btn">Start reading</router-link>
      </section>

      <router-view />
    </main>
  </div>
</template>


<style scoped>
.dash{min-height:100vh;display:flex;flex-direction:column;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)}
.dash-main{flex:1;display:flex;align-items:center;justify-content:center;padding:24px}
.panel{width:100%;max-width:800px;background:#fff;border-radius:12px;box-shadow:0 10px 25px rgba(0,0,0,.1);padding:2rem 2.25rem;text-align:center}
.panel h1{font-size:1.5rem;color:#111;margin:0}
.sub{margin:.25rem 0 0;color:#666}
.inline-link{color:#667eea;text-decoration:none}.inline-link:hover{text-decoration:underline}
.divider{height:1px;background:#e1e5e9;margin:1.25rem 0 1.5rem}
.progress-title{color:#333;margin-bottom:.75rem}
.metrics{display:grid;grid-template-columns:1fr 1fr;gap:.75rem 2rem;justify-items:center;margin-bottom:1.75rem}
.metric{display:flex;gap:.5rem}.label{color:#555}.value{font-weight:700;color:#111}
.primary-btn{display:inline-block;padding:.75rem 1.5rem;border-radius:6px;font-size:1rem;font-weight:700;text-decoration:none;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;transition:opacity .2s}
.primary-btn:hover{opacity:.9}
@media (max-width:600px){.panel{padding:1.25rem;margin:0 1rem}.metrics{grid-template-columns:1fr}}
</style>
