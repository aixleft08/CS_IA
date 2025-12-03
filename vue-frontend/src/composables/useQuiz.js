import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

export function useQuiz() {
  const { token } = useAuth()

  const questions = ref([])
  const loading = ref(false)
  const error = ref('')

  const submitting = ref(false)
  const submitError = ref('')
  const result = ref(null)

  function reset() {
    questions.value = []
    result.value = null
    error.value = ''
    submitError.value = ''
  }

  async function loadWordbankQuiz(limit = 10) {
    if (!token.value) {
      error.value = 'Please sign in to start a quiz'
      return { ok: false, reason: 'unauthorized' }
    }

    loading.value = true
    error.value = ''
    result.value = null
    questions.value = []

    try {
      const res = await fetch(`/api/quizzes/wordbank?limit=${encodeURIComponent(limit)}`, {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      })

      const data = await res.json().catch(() => ({}))

      if (!res.ok) {
        error.value = data.error || 'Failed to load quiz'
        return { ok: false, reason: data.error || 'failed' }
      }

      const qs = Array.isArray(data.questions) ? data.questions : []

      questions.value = qs.map(q => ({
        id: q.id,
        zh: q.zh,
        hint: q.hint || null,
        answer: '',
      }))

      if (!questions.value.length) {
        error.value = 'No questions available'
        return { ok: false, reason: 'empty' }
      }

      return { ok: true }
    } catch (e) {
      error.value = 'Network error while loading quiz'
      return { ok: false, reason: 'network' }
    } finally {
      loading.value = false
    }
  }

  async function submitWordbankQuiz() {
    if (!token.value) {
      submitError.value = 'Please sign in to submit the quiz'
      return { ok: false, reason: 'unauthorized' }
    }

    if (!questions.value.length) {
      submitError.value = 'No questions to submit'
      return { ok: false, reason: 'no_questions' }
    }

    submitting.value = true
    submitError.value = ''

    const payload = {
      answers: questions.value.map(q => ({
        id: q.id,
        answer: q.answer || '',
      })),
    }

    try {
      const res = await fetch('/api/quizzes/wordbank/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token.value}`,
        },
        body: JSON.stringify(payload),
      })

      const data = await res.json().catch(() => ({}))

      if (!res.ok) {
        submitError.value = data.error || 'Failed to submit quiz'
        return { ok: false, reason: data.error || 'failed' }
      }

      result.value = {
        total: data.total ?? 0,
        correct: data.correct ?? 0,
        accuracy: data.accuracy ?? 0,
        details: Array.isArray(data.details) ? data.details : [],
      }

      return { ok: true, result: result.value }
    } catch (e) {
      submitError.value = 'Network error while submitting quiz'
      return { ok: false, reason: 'network' }
    } finally {
      submitting.value = false
    }
  }

  return {
    questions,
    loading,
    error,
    submitting,
    submitError,
    result,
    loadWordbankQuiz,
    submitWordbankQuiz,
    reset,
  }
}
