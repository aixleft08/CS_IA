<script setup>
import { onMounted, ref } from 'vue'
import NavBar from '@/components/NavBar.vue'
import Toast from '@/components/Toast.vue'
import QuizQuestion from '@/components/QuizQuestion.vue'
import QuizResult from '@/components/QuizResult.vue'
import { useWordbankQuiz } from '@/composables/useWordBankQuiz'

const {
  questions,
  loading,
  error,
  currentIndex,
  answer,
  result,
  finished,
  submitting,
  currentQuestion,
  isLastQuestion,
  progressPercent,
  fetchQuiz,
  goNextOrSubmit,
  restartQuiz,
} = useWordbankQuiz()

const toastOpen = ref(false)
const toastMsg = ref('')
const toastType = ref('success')

function notify(message, type = 'success') {
  toastMsg.value = message
  toastType.value = type
  toastOpen.value = false
  requestAnimationFrame(() => {
    toastOpen.value = true
  })
}

async function loadQuiz() {
  await fetchQuiz()
  if (error.value) {
    notify(error.value, 'error')
  }
}

async function handleNext() {
  const res = await goNextOrSubmit()
  if (res?.submitted) {
    if (!res.ok) {
      notify(res.error || 'Failed to submit quiz', 'error')
    } else {
      notify('Quiz submitted!', 'success')
    }
  }
}

async function handleRestart() {
  await restartQuiz()
  if (error.value) {
    notify(error.value, 'error')
  }
}

onMounted(() => {
  loadQuiz()
})
</script>

<template>
  <div class="page">
    <NavBar />

    <main class="main">
      <section class="card" v-if="loading && !error">
        <p>Loading quiz…</p>
      </section>

      <section class="card error" v-else-if="error">
        <h1>Quiz</h1>
        <p>{{ error }}</p>
        <button type="button" class="btn primary" @click="loadQuiz">
          Try again
        </button>
      </section>

      <QuizQuestion
        v-else-if="questions.length && !finished"
        :question="currentQuestion"
        :index="currentIndex"
        :total="questions.length"
        v-model:answer="answer"
        :progress-percent="progressPercent"
        :is-last="isLastQuestion"
        :submitting="submitting"
        @next="handleNext"
        @restart="handleRestart"
      />

      <QuizResult
        v-if="result && finished"
        :result="result"
        :questions="questions"
        @restart="handleRestart"
      />
    </main>

    <Toast
      :open="toastOpen"
      :message="toastMsg"
      :type="toastType"
      @close="toastOpen = false"
    />
  </div>
</template>

<style scoped>
.page{
  min-height:100vh;
  display:flex;
  flex-direction:column;
  background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
}
.main{
  flex:1;
  padding:40px 20px;
  display:flex;
  justify-content:center;
  align-items:flex-start;
}
.card{
  background:#fff;
  border-radius:16px;
  box-shadow:0 14px 35px rgba(0,0,0,.16);
  padding:1.8rem 2rem 2.2rem;
  max-width:720px;
  width:100%;
}
.card.error{
  text-align:center;
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
@media (max-width:720px){
  .main{
    padding:24px 12px;
  }
  .card{
    padding:1.4rem 1.4rem 1.6rem;
  }
}
</style>
