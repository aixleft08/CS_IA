<script setup>
import { onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import WordTable from '@/components/WordTable.vue'
import { useWordBank } from '@/composables/useWordBank'
import { useLastReading } from '@/composables/useLastReading'

const {
  words,
  loading,
  error,
  fetchWords,
  clearWords,
  addWord,
  deleteWord,
  fetchEntry,
} = useWordBank()

const { last, loading: lastLoading, error: lastError, fetchLastReading } = useLastReading()

onMounted(() => {
  fetchWords()
  fetchLastReading()
})

function handleReset() { clearWords() }
function handleAdd(word) { addWord(word) }
function handleDelete(id) { deleteWord(id) }
function handleToggleDetails(wordObj) { fetchEntry(wordObj) }
</script>

<template>
  <div class="page">
    <NavBar />
    <main class="main">
      <WordTable
        :rows="words"
        :loading="loading"
        :error="error"
        :last="last"
        :last-loading="lastLoading"
        :last-error="lastError"
        @reset="handleReset"
        @add="handleAdd"
        @delete="handleDelete"
        @toggle-details="handleToggleDetails"
      />
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
.main { flex: 1; padding: 40px 20px; }
</style>
