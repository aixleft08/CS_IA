import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import DashboardView from '@/views/DashboardView.vue'
import SignUpView from '@/views/SignUpView.vue'
import SignInView from '@/views/SignInView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: HomeView, meta: { showHeader: true } },
    { path: '/dashboard', component: DashboardView, meta: { showHeader: true, requiresAuth: true } },
    { path: '/sign-up', component: SignUpView, meta: { showHeader: false } },
    { path: '/sign-in', component: SignInView, meta: { showHeader: false } },
    { path: '/:pathMatch(.*)*', component: NotFoundView, meta: { showHeader: true } },
  ],
})