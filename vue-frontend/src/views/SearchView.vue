<script setup>
import NavBar from '@/components/NavBar.vue'
import SearchBar from '@/components/SearchBar.vue'
import ArticleCard from '@/components/ArticleCard.vue'
import { onMounted } from 'vue'
import { useArticles } from '@/composables/useArticles'

const {
  articles,
  loading,
  error,
  fetchArticles,
  seedArticles,
  deleteArticle,
} = useArticles()

onMounted(() => {
  fetchArticles()
})

function doSearch(query) {
  fetchArticles(query)
}

async function onDeleteArticle(id) {
  const ok = confirm('Delete this article?')
  if (!ok) return
  await deleteArticle(id)
}
</script>

<template>
  <div class="page">
    <NavBar />
    <main class="main">
      <div class="top-bar">
        <SearchBar @submit="doSearch" />
        <button class="seed-btn" @click="seedArticles">Seed example articles</button>
      </div>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="loading" class="loading">Loading…</p>

      <section v-else class="list">
        <ArticleCard
          v-for="a in articles"
          :key="a.id"
          :article="a"
          show-delete
          @delete="onDeleteArticle(a.id)"
        />
        <p v-if="!articles.length">No articles yet.</p>
      </section>
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
  max-width: 980px;
  margin: 0 auto;
  padding: 40px 20px;
}

.top-bar {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.seed-btn {
  background: #fff;
  border: none;
  border-radius: 999px;
  padding: 0.55rem 1.1rem;
  font-weight: 600;
  color: #333;
  box-shadow: 0 4px 12px rgba(0,0,0,.12);
  cursor: pointer;
  white-space: nowrap;
}
.seed-btn:hover {
  background: #f3f4f6;
}

.error {
  margin-top: 1rem;
  background: rgba(255, 236, 236, 0.95);
  border: 1px solid rgba(255, 174, 174, 0.5);
  color: #c33;
  padding: .6rem .9rem;
  border-radius: 8px;
}

.loading {
  margin-top: 1rem;
  color: #fff;
  font-weight: 500;
}

.list {
  margin: 28px auto 0;
  max-width: 820px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (max-width: 720px) {
  .main {
    padding-top: 28px;
  }
  .top-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .seed-btn {
    width: fit-content;
  }
  .list {
    margin-top: 20px;
  }
}
</style>
