import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import SignInView from '@/views/SignInView.vue'
import SignUpView from '@/views/SignUpView.vue'
import DashboardView from '@/views/DashboardView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import WordbankView from '@/views/WordBankView.vue'
import SearchView from '@/views/SearchView.vue'
import QuizView from '@/views/QuizView.vue'
import ReadingView from '@/views/ReadingView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/sign-in', component: SignInView, meta: { guestOnly: true } },
    { path: '/sign-up', component: SignUpView, meta: { guestOnly: true } },

    { path: '/dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/wordbank', component: WordbankView, meta: { requiresAuth: true } },
    { path: '/search', component: SearchView, meta: { requiresAuth: true } },
    { path: '/quiz', component: QuizView, meta: { requiresAuth: true } },
    { path: '/read/:id', component: ReadingView, meta: { requiresAuth: true } },

    { path: '/:pathMatch(.*)*', component: NotFoundView },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('authToken')
  if (to.meta.requiresAuth && !token) {
    return { path: '/sign-in', query: { next: to.fullPath } }
  }
})

export default router