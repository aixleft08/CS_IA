import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import SignInView from '@/views/SignInView.vue'
import SignUpView from '@/views/SignUpView.vue'
import DashboardView from '@/views/DashboardView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import WordbankView from '@/views/WordBankView.vue'
import SearchView from '@/views/SearchView.vue'
import ReadingView from '@/views/ReadingView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/sign-in', component: SignInView },
    { path: '/sign-up', component: SignUpView },
    { path: '/dashboard', component: DashboardView, meta: { requiresAuth: false } },
    { path: '/wordbank', component: WordbankView, meta: { requiresAuth: false } },
    { path: '/search', component: SearchView, meta: { requiresAuth: false } },
    { path: '/read/:id', component: ReadingView, meta: { requiresAuth: false } },

    // Catch-all 404
    { path: '/:pathMatch(.*)*', component: NotFoundView },
  ],
})

// Simple auth guard
router.beforeEach((to) => {
  const token = localStorage.getItem('authToken')
  if (to.meta.requiresAuth && !token) {
    return { path: '/sign-in', query: { next: to.fullPath } }
  }
})

export default router