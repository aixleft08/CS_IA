<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['submit'])
const q = ref('')

let t = null
const DEBOUNCE_MS = 350

function submit() {
  emit('submit', q.value.trim())
}

onMounted(() => {
  const el = document.getElementById('search-input')
  if (el) el.focus()
})

watch(q, (val) => {
  const term = (val || '').trim()

  clearTimeout(t)

  if (!term) {
    emit('submit', '')
    return
  }

  // ✅ Otherwise, debounce the search
  t = setTimeout(() => {
    emit('submit', term)
  }, DEBOUNCE_MS)
})

onBeforeUnmount(() => {
  clearTimeout(t)
})
</script>

<template>
  <form class="search" @submit.prevent="submit" role="search">
    <input
      id="search-input"
      v-model="q"
      type="search"
      placeholder="Search for articles…"
      autocomplete="off"
    />
    <button type="submit">Enter</button>
  </form>
</template>

<style scoped>
.search{display:grid;grid-template-columns:1fr auto;gap:.6rem;max-width:680px;margin:0 auto}
input{padding:.85rem 1rem;border:2px solid #d7dbe2;border-radius:8px;font-size:1.05rem;background:#fff}
input:focus{outline:none;border-color:#667eea}
button{padding:.75rem 1.2rem;border:2px solid #a7acb7;border-radius:8px;background:#efefef;font-weight:700;cursor:pointer}
button:hover{background:#e6e6e6}
</style>
