<script setup>
const props = defineProps({
  entry: { type: Object, required: true }
})
const emit = defineEmits(['add'])
</script>

<template>
  <aside class="dict">
    <h2>Dictionary</h2>

    <div class="row">
      <span class="term">{{ entry.word || '—' }}</span>
    </div>

    <ul v-if="entry.defs?.length" class="defs">
      <li v-for="(d, i) in entry.defs" :key="i">
        <span class="pos">{{ d.pos }}</span>
        <span class="text">{{ d.text }}</span>
      </li>
    </ul>

    <p v-else class="def">{{ entry.definition || 'No definition found.' }}</p>

    <p v-if="entry.translation" class="trans">{{ entry.translation }}</p>

    <button class="add" :disabled="!entry.word" @click="$emit('add', entry)">
      Add to wordbank
    </button>
  </aside>
</template>

<style scoped>
.dict{
  background:#fff;border-radius:12px;box-shadow:0 10px 25px rgba(0,0,0,.1);
  padding:1.25rem 1.4rem;border:2px solid #cfd4dc
}
h2{margin:.25rem 0 1rem;font-size:1.8rem}
.row{display:flex;align-items:baseline;gap:.6rem;margin:.25rem 0 1rem}
.term{font-weight:800;font-size:1.15rem}

.defs{
  list-style:none;padding:0;margin:0 0 1rem 0;display:flex;flex-direction:column;gap:.5rem
}
.defs li{
  display:flex;align-items:flex-start;gap:.5rem
}
.pos{
  flex:0 0 auto;
  font-size:.75rem;
  text-transform:uppercase;
  letter-spacing:.02em;
  background:#eef2ff;
  color:#4338ca;
  border:1px solid #c7d2fe;
  border-radius:6px;
  padding:.15rem .4rem;
}
.text{
  flex:1 1 auto;
  color:#333;
  display:-webkit-box;
  line-clamp:2;
  -webkit-line-clamp:2;
  -webkit-box-orient:vertical;
  overflow:hidden;
}

.def{margin:.25rem 0 1rem;color:#333}
.trans{margin:0 0 1.25rem;color:#111}

.add{
  padding:.75rem 1rem;border:0;border-radius:8px;background:#333;color:#fff;cursor:pointer
}
.add:disabled{opacity:.6;cursor:not-allowed}
.add:hover:not(:disabled){background:#555}
</style>
