<script setup>
const props = defineProps({
  rows: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['reset'])
</script>

<template>
  <section class="wrap">
    <h1 class="title">Wordbank</h1>
    <p class="sub">
      Your were reading
      <router-link to="/search" class="inline-link">xxx</router-link>.
    </p>

    <div class="table">
      <div class="thead">
        <div>#</div>
        <div>Word</div>
        <div>Definition</div>
        <div>Translation</div>
      </div>

      <!-- loading -->
      <div v-if="loading" class="trow">
        <div></div>
        <div class="bold">Loading…</div>
        <div></div>
        <div></div>
      </div>

      <!-- error -->
      <div v-else-if="error" class="trow">
        <div></div>
        <div class="bold" style="color:#c33">{{ error }}</div>
        <div></div>
        <div></div>
      </div>

      <!-- empty -->
      <div v-else-if="!rows.length" class="trow">
        <div></div>
        <div class="bold">No words yet.</div>
        <div></div>
        <div></div>
      </div>

      <!-- data -->
      <div v-else v-for="(r, i) in rows" :key="r.id" class="trow">
        <div>{{ i + 1 }}</div>
        <div class="bold">{{ r.word }}</div>
        <div>{{ r.definition }}</div>
        <div>{{ r.translation }}</div>
      </div>
    </div>

    <div class="actions">
      <button class="ghost" @click="$emit('reset')">Reset wordbank</button>
    </div>
  </section>
</template>

<style scoped>
.wrap {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  padding: 2rem 2.25rem;
  max-width: 1000px;
  margin: 0 auto;
}
.title {
  margin: 0 0 0.25rem;
  text-align: center;
  font-size: 2rem;
}
.sub {
  margin: 0 0 1.25rem;
  text-align: center;
  color: #666;
}
.inline-link {
  color: #667eea;
  text-decoration: underline;
}
.table {
  border: 2px solid #cfd4dc;
  border-radius: 8px;
  overflow: hidden;
}
.thead,
.trow {
  display: grid;
  grid-template-columns: 80px 1fr 2fr 1fr;
}
.thead {
  background: #f3f4f6;
  font-weight: 800;
}
.thead > div,
.trow > div {
  padding: 0.9rem 1rem;
  border-bottom: 2px solid #e5e7eb;
}
.trow:last-child > div {
  border-bottom: none;
}
.bold {
  font-weight: 700;
}
.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.25rem;
}
.ghost {
  padding: 0.7rem 1rem;
  border: 2px solid #a7acb7;
  background: #efefef;
  border-radius: 8px;
  cursor: pointer;
}
.ghost:hover {
  background: #e8e8e8;
}
@media (max-width: 720px) {
  .thead,
  .trow {
    grid-template-columns: 60px 1fr 1.2fr 0.8fr;
  }
}
</style>
