<script setup>
import Header from '@/components/Header.vue'
import SearchBar from '@/components/SearchBar.vue'
import ArticleCard from '@/components/ArticleCard.vue'
import { ref } from 'vue'

const results = ref([
  { id: 101, title: 'Lorem ipsum dolor sit amet', summary: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua...' },
  { id: 102, title: 'Lorem ipsum dolor sit amet', summary: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua...' },
  { id: 103, title: 'Lorem ipsum dolor sit amet', summary: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua...' },
])

function doSearch(query) {
  // hook this to your Flask API later; keep mocked for now
  // Example: fetch(`/api/search?q=${encodeURIComponent(query)}`).then(...)
  console.log('search:', query)
}
</script>

<template>
  <div class="page">
    <Header />
    <main class="main">
      <SearchBar @submit="doSearch" />
      <section class="list">
        <ArticleCard v-for="a in results" :key="a.id" :article="a" />
      </section>
    </main>
  </div>
</template>

<style scoped>
.page{min-height:100vh;display:flex;flex-direction:column;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)}
.main{flex:1;max-width:980px;margin:0 auto;padding:40px 20px}
.list{margin:28px auto 0;max-width:820px}
</style>
