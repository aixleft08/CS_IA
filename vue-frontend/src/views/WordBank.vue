<script setup>
import Header from '@/components/Header.vue'
import WordTable from '@/components/WordTable.vue'
import { reactive } from 'vue'

const rows = reactive([
  { id:1, word:'Lorem', definition:'Ipsum', translation:'文本' },
  { id:2, word:'Lorem', definition:'Ipsum', translation:'文本' },
  { id:3, word:'Lorem', definition:'Ipsum', translation:'文本' },
  { id:4, word:'Lorem', definition:'Ipsum', translation:'文本' },
  { id:5, word:'Lorem', definition:'Ipsum', translation:'文本' },
])

function reset() {
  rows.splice(0, rows.length) // clear
}
</script>

<template>
  <div class="page">
    <Header />
    <main class="main">
      <WordTable :rows="rows" @reset="reset" />
    </main>
  </div>
</template>

<style scoped>
.page{min-height:100vh;display:flex;flex-direction:column;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)}
.main{flex:1;padding:40px 20px}
</style>
