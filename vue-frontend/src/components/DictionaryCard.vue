<script setup>
const props = defineProps({
  entry: { type: Object, required: true } // { word, definition, translation }
})
const emit = defineEmits(['add'])
</script>

<template>
  <aside class="dict">
    <h2>Dictionary</h2>

    <div class="row">
      <span class="icon" aria-hidden="true">🔊</span>
      <span class="term">{{ entry.word }}</span>
    </div>

    <p class="def">{{ entry.definition }}</p>
    <p class="trans">{{ entry.translation }}</p>

    <button class="add" @click="$emit('add', entry)">Add to wordbank</button>
  </aside>
</template>

<style scoped>
.dict{background:#fff;border-radius:12px;box-shadow:0 10px 25px rgba(0,0,0,.1);padding:1.25rem 1.4rem;border:2px solid #cfd4dc}
h2{margin:.25rem 0 1rem;font-size:1.8rem}
.row{display:flex;align-items:center;gap:.6rem;margin:.5rem 0 1rem}
.icon{font-size:1.3rem}
.term{font-weight:700}
.def{margin:.25rem 0 1rem;color:#333}
.trans{margin:0 0 1.25rem;color:#111}
.add{padding:.75rem 1rem;border:0;border-radius:8px;background:#333;color:#fff;cursor:pointer}
.add:hover{background:#555}
</style>
