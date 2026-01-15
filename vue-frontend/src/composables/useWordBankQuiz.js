import { ref, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'

export function useWordbankQuiz() {
  const { token } = useAuth()

  const questions = ref([])
  const loading = ref(false)
  const error = ref('')
  const currentIndex = ref(0)
  const answer = ref('')
  const userAnswers = ref([])
  const result = ref(null)
  const finished = ref(false)
  const submitting = ref(false)

  const currentQuestion = computed(
    () => questions.value[currentIndex.value] || {}
  )

  const isLastQuestion = computed(
    () => currentIndex.value === questions.value.length - 1
  )

  const progressPercent = computed(() => {
    if (!questions.value.length) return 0
    return (currentIndex.value / questions.value.length) * 100
  })

  function recordCurrentAnswer() {
    const q = currentQuestion.value
    if (!q?.id) return
    const trimmed = (answer.value || '').trim()
    const idx = userAnswers.value.findIndex(a => a.id === q.id)
    if (idx >= 0) {
      userAnswers.value[idx].answer = trimmed
    } else {
      userAnswers.value.push({ id: q.id, answer: trimmed })
    }
  }

  async function fetchQuiz(limit = 10) {
    if (!token.value) {
      error.value = 'Please sign in to take a quiz'
      return
    }

    loading.value = true
    error.value = ''
    finished.value = false
    result.value = null
    questions.value = []
    currentIndex.value = 0
    answer.value = ''
    userAnswers.value = []

    try {
      const res = await fetch(`/api/quizzes/wordbank?limit=${limit}`, {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      const data = await res.json()
      if (!res.ok) {
        error.value = data.error || 'Failed to load quiz'
        return
      }

      questions.value = data.questions || []
      if (!questions.value.length) {
        error.value = 'No quiz questions available'
        return
      }

      currentIndex.value = 0
      answer.value = ''
    } catch {
      error.value = 'Network error while loading quiz'
    } finally {
      loading.value = false
    }
  }

  async function submitQuiz() {
    if (!token.value) {
      error.value = 'Please sign in to submit quiz'
      return { ok: false, error: error.value }
    }

    submitting.value = true
    error.value = ''

    try {
      const res = await fetch('/api/quizzes/wordbank/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token.value}`,
        },
        body: JSON.stringify({ answers: userAnswers.value }),
      })
      const data = await res.json()

      if (!res.ok) {
        error.value = data.error || 'Failed to submit quiz'
        return { ok: false, error: error.value }
      }

      result.value = data
      finished.value = true
      return { ok: true }
    } catch {
      error.value = 'Network error while submitting quiz'
      return { ok: false, error: error.value }
    } finally {
      submitting.value = false
    }
  }

  async function goNextOrSubmit() {
    if (!questions.value.length || finished.value) {
      return { submitted: false }
    }

    recordCurrentAnswer()

    if (isLastQuestion.value) {
      const submitRes = await submitQuiz()
      return { submitted: true, ...submitRes }
    }

    currentIndex.value += 1
    const nextQ = questions.value[currentIndex.value]
    const existing = userAnswers.value.find(a => a.id === nextQ.id)
    answer.value = existing ? existing.answer : ''

    return { submitted: false }
  }

  async function restartQuiz(limit = 10) {
    await fetchQuiz(limit)
  }

  function getZhForDetail(id) {
    const q = questions.value.find(q => q.id === id)
    return q ? q.zh : ''
  }

  return {
    questions,
    loading,
    error,
    currentIndex,
    answer,
    userAnswers,
    result,
    finished,
    submitting,
    currentQuestion,
    isLastQuestion,
    progressPercent,
    fetchQuiz,
    goNextOrSubmit,
    restartQuiz,
    getZhForDetail,
  }
}
