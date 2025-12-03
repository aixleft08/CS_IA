<script setup>
import { onMounted, ref } from 'vue'
import NavBar from '@/components/NavBar.vue'
import WordTable from '@/components/WordTable.vue'
import { useWordBank } from '@/composables/useWordBank'
import { useLastReading } from '@/composables/useLastReading'
import Toast from '@/components/Toast.vue'

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

const {
  last,
  loading: lastLoading,
  error: lastError,
  fetchLastReading,
} = useLastReading()

const toastOpen = ref(false)
const toastMsg = ref('')
const toastType = ref('success')

function notify(message, type = 'success') {
  toastMsg.value = message
  toastType.value = type
  toastOpen.value = false
  requestAnimationFrame(() => {
    toastOpen.value = true
  })
}

onMounted(() => {
  fetchWords()
  fetchLastReading()
})

async function handleReset() {
  await clearWords()
  notify('Wordbank cleared')
}

async function handleAdd(word) {
  const res = await addWord(word)
  if (res?.ok) {
    notify(`Added “${word}” to wordbank`)
  } else if (res?.reason === 'duplicate') {
    notify(`“${word}” is already in your wordbank`, 'info')
  } else if (res?.reason === 'unauthorized') {
    notify('Please sign in to manage your wordbank', 'warn')
  } else if (res?.reason === 'network') {
    notify('Network error — please try again', 'error')
  } else {
    notify('Could not add word', 'error')
  }
}

async function handleDelete(id) {
  const row = words.value.find(w => w.id === id)
  await deleteWord(id)
  if (row) {
    notify(`Removed “${row.word}”`, 'info')
  } else {
    notify('Word removed', 'info')
  }
}

function handleToggleDetails(wordObj) {
  fetchEntry(wordObj)
}
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

    <Toast
      :open="toastOpen"
      :message="toastMsg"
      :type="toastType"
      @close="toastOpen = false"
    />
  </div>
</template>

<style scoped>
.page{
  min-height:100vh;
  display:flex;
  flex-direction:column;
  background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
}
.main{
  flex:1;
  padding:40px 20px;
}
</style>
