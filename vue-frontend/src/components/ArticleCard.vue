<script setup>
const props = defineProps({
  article: { type: Object, required: true },
  showDelete: { type: Boolean, default: false },
})
const emit = defineEmits(['delete', 'tag'])
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

    <div v-if="article.tags?.length" class="tags">
      <button
        v-for="t in article.tags"
        :key="t"
        class="tag"
        type="button"
        @click.stop="emit('tag', t)"
      >
        {{ t }}
      </button>
    </div>

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

.tags{
  display:flex;
  flex-wrap:wrap;
  gap:.4rem;
  margin:.2rem 0 .55rem;
}

.tag{
  font-size:.8rem;
  padding:.18rem .55rem;
  border-radius:999px;
  border:1px solid #d7dbe2;
  background:#f6f7f9;
  color:#444;
  font-weight:700;
}

.tag{ cursor:pointer; }
.tag:hover{ background:#eef0f4; }

.meta{
  color:#666;
  font-size:.85rem;
}

.card:hover{background:#fafafa}
</style>
