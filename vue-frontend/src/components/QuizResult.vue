<script setup>
import { computed } from 'vue'

const props = defineProps({
  result:    { type: Object, required: true },
  questions: { type: Array,  required: true },
})

const emit = defineEmits(['restart'])

const zhById = computed(() => {
  const map = {}
  for (const q of props.questions) {
    if (q && q.id != null) {
      map[q.id] = q.zh
    }
  }
  return map
})

function getZh(id) {
  return zhById.value[id] || ''
}
</script>

<template>
  <section class="card result-card">
    <header class="quiz-header">
      <h1>Results</h1>
      <p class="quiz-sub">
        You answered {{ result.correct }} out of {{ result.total }} correctly
        ({{ (result.accuracy * 100).toFixed(0) }}%).
      </p>
    </header>

    <ul class="details">
      <li
        v-for="d in result.details"
        :key="d.id"
        class="detail-row"
        :class="{ correct: d.correct, wrong: !d.correct }"
      >
        <div class="detail-main">
          <span class="badge" v-if="d.correct">Correct</span>
          <span class="badge bad" v-else>Wrong</span>
        </div>

        <p class="detail-text">
          <span class="detail-zh" v-if="getZh(d.id)">
            Chinese:
            <strong>{{ getZh(d.id) }}</strong><br />
          </span>
          Your answer:
          <strong>{{ d.given || '—' }}</strong><br />
          Expected:
          <strong>{{ d.expected }}</strong>
        </p>
      </li>
    </ul>

    <div class="controls">
      <button
        type="button"
        class="btn primary"
        @click="$emit('restart')"
      >
        Try another quiz
      </button>
    </div>
  </section>
</template>

<style scoped>
.card{
  background:#fff;
  border-radius:16px;
  box-shadow:0 14px 35px rgba(0,0,0,.16);
  padding:1.8rem 2rem 2.2rem;
  max-width:800px;
  width:100%;
}
.quiz-header h1{
  margin:0 0 .25rem;
  font-size:1.6rem;
}
.quiz-sub{
  margin:0 0 1.2rem;
  color:#555;
  font-size:.95rem;
}

.details{
  list-style:none;
  padding:0;
  margin:1.2rem 0 0;
}
.detail-row{
  border-radius:10px;
  padding:.7rem .8rem;
  margin-bottom:.55rem;
  border:1px solid #e5e7eb;
  background:#fafafa;
}
.detail-row.correct{
  border-color:#bbf7d0;
  background:#f0fdf4;
}
.detail-row.wrong{
  border-color:#fecaca;
  background:#fef2f2;
}
.detail-main{
  display:flex;
  justify-content:space-between;
  align-items:center;
}
.badge{
  display:inline-flex;
  align-items:center;
  padding:.1rem .45rem;
  border-radius:999px;
  font-size:.75rem;
  font-weight:700;
  background:#22c55e1a;
  color:#16a34a;
}
.badge.bad{
  background:#ef44441a;
  color:#b91c1c;
}
.detail-text{
  margin:.4rem 0 0;
  font-size:.9rem;
  color:#444;
}
.detail-zh{
  display:block;
  margin-bottom:.15rem;
}
.controls{
  margin-top:1rem;
  display:flex;
  justify-content:flex-end;
}
.btn{
  border:none;
  border-radius:10px;
  padding:.55rem .95rem;
  font-weight:700;
  cursor:pointer;
  font-size:.95rem;
}
.btn.primary{
  background:#111;
  color:#fff;
  box-shadow:0 6px 14px rgba(0,0,0,.15);
}
.btn.primary:hover{
  background:#333;
}
</style>
