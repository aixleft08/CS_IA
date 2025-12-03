<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'

const props = defineProps({
  question:        { type: Object, required: true },
  index:           { type: Number, required: true },
  total:           { type: Number, required: true },
  answer:          { type: String, default: '' },
  progressPercent: { type: Number, default: 0 },
  isLast:          { type: Boolean, default: false },
  submitting:      { type: Boolean, default: false },
})

const emit = defineEmits(['update:answer', 'next', 'restart'])

const answerInput = ref(null)

function focusInput() {
  nextTick(() => {
    if (answerInput.value) {
      answerInput.value.focus()
      answerInput.value.select?.()
    }
  })
}

onMounted(() => {
  focusInput()
})

watch(
  () => props.question && props.question.id,
  () => focusInput()
)

function onSubmit() {
  emit('next')
}
</script>

<template>
  <section class="card quiz-card">
    <header class="quiz-header">
      <h1>Wordbank Quiz</h1>
      <p class="quiz-sub">
        Type the English word for each Chinese translation.<br />
        Question {{ index + 1 }} of {{ total }}
      </p>

      <div class="progress-bar">
        <div class="progress-inner" :style="{ width: progressPercent + '%' }"></div>
      </div>
    </header>

    <div class="quiz-body">
      <p class="prompt">
        <span class="label">Chinese</span>
        <span class="zh">{{ question.zh }}</span>
      </p>

      <p v-if="question.hint" class="hint">
        Hint: starts with
        <strong>{{ question.hint }}</strong>
      </p>

      <form class="answer-form" @submit.prevent="onSubmit">
        <label class="answer-label">
          Your answer
          <input
            ref="answerInput"
            :value="answer"
            @input="emit('update:answer', $event.target.value)"
            type="text"
            class="answer-input"
            autocomplete="off"
          />
        </label>

        <div class="controls">
          <button
            type="submit"
            class="btn primary"
            :disabled="submitting"
          >
            <span v-if="isLast">
              {{ submitting ? 'Submitting…' : 'Submit quiz' }}
            </span>
            <span v-else>Next</span>
          </button>

          <button
            type="button"
            class="btn ghost"
            @click="emit('restart')"
            :disabled="submitting"
          >
            Restart
          </button>
        </div>
      </form>
    </div>
  </section>
</template>

<style scoped>
.card{
  background:#fff;
  border-radius:16px;
  box-shadow:0 14px 35px rgba(0,0,0,.16);
  padding:1.8rem 2rem 2.2rem;
  max-width:720px;
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
.progress-bar{
  height:6px;
  border-radius:999px;
  background:#e5e7eb;
  overflow:hidden;
  margin-bottom:1.4rem;
}
.progress-inner{
  height:100%;
  background:linear-gradient(90deg,#667eea,#764ba2);
  transition:width .2s ease-out;
}
.quiz-body{
  display:flex;
  flex-direction:column;
  gap:1rem;
}
.prompt{
  margin:0;
}
.label{
  display:inline-block;
  font-size:.85rem;
  text-transform:uppercase;
  letter-spacing:.06em;
  color:#888;
  margin-bottom:.15rem;
}
.zh{
  display:block;
  font-size:1.7rem;
  font-weight:700;
  margin-top:.1rem;
}

/* hint */
.hint{
  margin:0;
  font-size:.9rem;
  color:#666;
}

.answer-form{
  margin-top:.75rem;
}
.answer-label{
  display:block;
  font-size:.9rem;
  margin-bottom:.75rem;
}
.answer-input{
  margin-top:.25rem;
  width:100%;
  max-width:100%;
  padding:.6rem .75rem;
  border-radius:10px;
  border:1px solid #d1d5db;
  font-size:1rem;
  box-sizing:border-box;
}
.answer-input:focus{
  outline:none;
  border-color:#667eea;
  box-shadow:0 0 0 1px rgba(102,126,234,.25);
}
.controls{
  margin-top:.3rem;
  display:flex;
  gap:.6rem;
  justify-content:flex-end;
  flex-wrap:wrap;
}

/* Buttons */
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
.btn.primary:disabled{
  opacity:.7;
  cursor:not-allowed;
}
.btn.primary:not(:disabled):hover{
  background:#333;
}
.btn.ghost{
  background:#f3f4f6;
  color:#111;
  border:1px solid #d1d5db;
}
.btn.ghost:disabled{
  opacity:.7;
  cursor:not-allowed;
}
.btn.ghost:not(:disabled):hover{
  background:#e5e7eb;
}
</style>
