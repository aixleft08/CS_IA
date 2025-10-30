<script setup>
import { onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import WordTable from '@/components/WordTable.vue'
import { useWordBank } from '@/composables/useWordBank'

const { words, loading, error, fetchWords, clearWords } = useWordBank()

onMounted(() => {
  fetchWords()
})

function reset() {
  clearWords()
}
</script>

<template>
  <div class="page">
    <NavBar />
    <main class="main">
      <WordTable :rows="words" :loading="loading" :error="error" @reset="reset" />
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.main {
  flex: 1;
  padding: 40px 20px;
}
</style>
