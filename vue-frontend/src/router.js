import { createRouter, createWebHistory } from 'vue-router'

const Home = () => import('../views/Home.vue')
const SignIn = () => import('../views/SignIn.vue')
const SignUp = () => import('../views/SignUp.vue')
const Dashboard = () => import('../views/Dashboard.vue')
const WordBank = () => import('../views/WordBank.vue')
const Search = () => import('../views/Search.vue')
const Reading = () => import('../views/Reading.vue')
const NotFound = () => import('../views/NotFound.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { 
      requiresAuth: false,
      title: 'Enlingo - Language Learning'
    }
  },
  {
    path: '/signin',
    name: 'SignIn',
    component: SignIn,
    meta: { 
      requiresAuth: false,
      title: 'Sign In - Enlingo',
      hideHeader: true
    }
  },
  {
    path: '/signup',
    name: 'SignUp',
    component: SignUp,
    meta: { 
      requiresAuth: false,
      title: 'Sign Up - Enlingo',
      hideHeader: true
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { 
      requiresAuth: true,
      title: 'Dashboard - Enlingo'
    }
  },
  {
    path: '/wordbank',
    name: 'WordBank',
    component: WordBank,
    meta: { 
      requiresAuth: true,
      title: 'Word Bank - Enlingo'
    }
  },
  {
    path: '/search',
    name: 'Search',
    component: Search,
    meta: { 
      requiresAuth: true,
      title: 'Search Articles - Enlingo'
    }
  },
  {
    path: '/reading/:id?',
    name: 'Reading',
    component: Reading,
    meta: { 
      requiresAuth: true,
      title: 'Reading - Enlingo'
    },
    props: true
  },
  // Redirect from old routes if needed
  {
    path: '/login',
    redirect: '/signin'
  },
  {
    path: '/register',
    redirect: '/signup'
  },
  // 404 page - should keep this last
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { 
      requiresAuth: false,
      title: 'Page Not Found - Enlingo'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  // Scroll behavior
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth',
        top: 20 // offset for fixed headers
      }
    } else {
      return { top: 0, behavior: 'smooth' }
    }
  }
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  // Check authentication - I might need to use a store instead of localStorage directly
  const isAuthenticated = localStorage.getItem('authToken')
  const userData = JSON.parse(localStorage.getItem('user') || '{}')
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  // Update page title
  if (to.meta.title) {
    document.title = to.meta.title
  }

  // Auth protection
  if (requiresAuth && !isAuthenticated) {
    // Redirect to signin with return url
    next({
      path: '/signin',
      query: { redirect: to.fullPath }
    })
  } 
  // Prevent authenticated users from accessing auth pages
  else if ((to.name === 'SignIn' || to.name === 'SignUp') && isAuthenticated) {
    next('/dashboard')
  }
  // Add additional guards here if needed (admin routes, etc.)
  else if (to.meta.requiresAdmin && userData.role !== 'admin') {
    next('/dashboard') // or create an unauthorized page
  }
  else {
    next()
  }
})

// Handle navigation errors
router.onError((error) => {
  console.error('Router error:', error)
  // I might need to redirect to an error page here
})

export default router