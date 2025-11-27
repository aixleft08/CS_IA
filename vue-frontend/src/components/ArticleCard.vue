<script setup>
const props = defineProps({
  article: { type: Object, required: true },
  showDelete: { type: Boolean, default: false },
})
const emit = defineEmits(['delete'])
</script>

<template>
  <article class="card">
    <header class="row">
      <RouterLink class="title" :to="`/read/${article.id}`">
        {{ article.title }}
      </RouterLink>

      <button
        v-if="showDelete"
        class="delete-btn"
        title="Delete article"
        @click.stop="emit('delete')"
      >
        Delete
      </button>
    </header>

    <p class="summary">{{ article.summary }}</p>

    <footer class="meta">
      <span v-if="article.authors">{{ article.authors }}</span>
      <span v-if="article.date"> · {{ new Date(article.date).toLocaleDateString() }}</span>
      <span v-if="article.difficulty !== null && article.difficulty !== undefined">
        · Diff: {{ article.difficulty }}
      </span>
    </footer>
  </article>
</template>

<style scoped>
.card{
  background:#fff;
  border:2px solid #cfd4dc;
  border-radius:8px;
  padding:1rem 1.2rem;
  color:#222;
}
.card + .card{margin-top:.75rem}

.row{
  display:flex;
  align-items:center;
  gap:.75rem;
}

.title{
  font-weight:800;
  color:#111;
  text-decoration:none;
  font-size:1.1rem;
  line-height:1.2;
  flex:1;
}
.title:hover{text-decoration:underline}

.delete-btn{
  border:none;
  background:#ffe9e9;
  color:#b51f1f;
  font-weight:700;
  padding:.35rem .7rem;
  border-radius:8px;
  cursor:pointer;
}
.delete-btn:hover{background:#ffdede}

.summary{
  margin:.45rem 0 .4rem;
  color:#555;
  line-height:1.4;
  display:-webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow:hidden;
  text-overflow: ellipsis;
  line-clamp: 3;
}

.meta{
  color:#666;
  font-size:.85rem;
}

.card:hover{background:#fafafa}
</style>
