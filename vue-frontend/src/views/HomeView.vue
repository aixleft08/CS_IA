<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const isAuthenticated = computed(() => !!localStorage.getItem('authToken'))

function handleSignOut() {
  localStorage.removeItem('authToken')
  localStorage.removeItem('user')
  router.push('/')
}
</script>

<template>
  <div class="home-container">
    <div class="home-card">
      <!-- Header -->
      <div class="home-header">
        <h1>Enlingo</h1>
        <h2>Your personal language companion</h2>
      </div>

      <!-- Divider -->
      <div class="divider"></div>

      <!-- Content -->
      <div class="home-content">
        <p v-if="!isAuthenticated">Sign up today and start your journey!</p>
        <p v-else>Welcome back 👋 Ready to continue learning?</p>
      </div>

      <!-- Buttons -->
      <div class="home-actions">
        <router-link v-if="!isAuthenticated" to="/sign-up" class="home-button">Sign Up</router-link>
        <router-link v-if="!isAuthenticated" to="/sign-in" class="home-button secondary">Sign In</router-link>
        <router-link v-if="!isAuthenticated" to="/dashboard" class="home-button">Go to Dashboard</router-link>
        <button v-if="isAuthenticated" @click="handleSignOut" class="home-button secondary">Sign Out</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.home-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
  text-align: center;
}

.home-header {
  margin-bottom: 1.5rem;
}

.home-header h1 {
  color: #333;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.home-header h2 {
  color: #666;
  font-size: 1.25rem;
  font-weight: normal;
  margin: 0;
}

.divider {
  height: 1px;
  background: #e1e5e9;
  margin: 1.5rem 0;
}

.home-content {
  margin-bottom: 2rem;
  color: #555;
  font-size: 1.1rem;
}

.home-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.home-button {
  display: block;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  text-decoration: none;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transition: opacity 0.3s ease;
}

.home-button:hover {
  opacity: 0.9;
}

.home-button.secondary {
  background: #333;
}

.home-button.secondary:hover {
  background: #555;
}

/* Responsive */
@media (max-width: 480px) {
  .home-card {
    padding: 1.5rem;
    margin: 1rem;
  }

  .home-header h1 {
    font-size: 1.75rem;
  }

  .home-header h2 {
    font-size: 1.1rem;
  }
}
</style>
