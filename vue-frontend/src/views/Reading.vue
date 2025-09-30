<script setup>
import Header from '@/components/Header.vue'
import DictionaryCard from '@/components/DictionaryCard.vue'
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const articleId = route.params.id

// Mock article
const articleTitle = ref('Lorem ipsum')
const paragraphs = ref([
  'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
  'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
  'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
  'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod…'
])

const currentEntry = ref({ word: 'Lorem', definition: 'dolor sit amet', translation: '文本' })

function addToWordbank(entry) {
  // later: POST to Flask to save word
  console.log('add to wordbank:', entry)
  alert(`Added "${entry.word}" to wordbank`)
}
</script>

<template>
  <div class="page">
    <Header />
    <main class="main">
      <section class="grid">
        <article class="reader">
          <h1 class="title">{{ articleTitle }}</h1>
          <p v-for="(p, i) in paragraphs" :key="i">{{ p }}</p>
        </article>

        <DictionaryCard class="side" :entry="currentEntry" @add="addToWordbank" />
      </section>
    </main>
  </div>
</template>

<style scoped>
.page{min-height:100vh;display:flex;flex-direction:column;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)}
.main{flex:1;max-width:1100px;margin:0 auto;padding:40px 20px}
.grid{display:grid;grid-template-columns:1.5fr .9fr;gap:24px;align-items:start}
.reader{background:#fff;border-radius:12px;border:2px solid #cfd4dc;box-shadow:0 10px 25px rgba(0,0,0,.1);padding:1.5rem}
.title{text-align:center;margin:0 0 1rem;font-size:2.1rem}
.reader p{margin:1rem 0;color:#222;line-height:1.7}
.side{position:sticky;top:18px}
@media(max-width:960px){.grid{grid-template-columns:1fr}}
</style>
