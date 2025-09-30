<script setup>
const props = defineProps({
  article: { type: Object, required: true } // { id, title, summary }
})
</script>

<template>
  <router-link class="card" :to="`/read/${article.id}`">
    <h3>{{ article.title }}</h3>
    <p>{{ article.summary }}</p>
  </router-link>
</template>

<style scoped>
.card{display:block;background:#fff;border:2px solid #cfd4dc;border-radius:8px;padding:1rem 1.2rem;color:#222;text-decoration:none}
.card + .card{margin-top:.75rem}
h3{margin:0 0 .4rem;font-size:1.35rem}
p{margin:0;color:#555;line-height:1.4}
.card:hover{background:#fafafa}
</style>
