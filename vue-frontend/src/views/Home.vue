<!-- REPLACE THE ENTIRE CONTENT OF src/App.vue -->
<template>
  <div id="app">
    <header v-if="$route.meta.showHeader !== false">
      <nav class="main-nav">
        <router-link to="/" class="logo">Enlingo</router-link>
        <div class="nav-links">
          <router-link v-if="isAuthenticated" to="/dashboard">Dashboard</router-link>
          <router-link v-if="isAuthenticated" to="/wordbank">Word Bank</router-link>
          <router-link v-if="!isAuthenticated" to="/signin">Sign In</router-link>
          <router-link v-if="!isAuthenticated" to="/signup">Sign Up</router-link>
          <button v-if="isAuthenticated" @click="handleSignOut" class="sign-out">Sign Out</button>
        </div>
      </nav>
    </header>
    
    <main :class="{'with-header': $route.meta.showHeader !== false}">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  computed: {
    isAuthenticated() {
      return localStorage.getItem('authToken')
    }
  },
  methods: {
    handleSignOut() {
      localStorage.removeItem('authToken')
      localStorage.removeItem('user')
      this.$router.push('/')
    }
  }
}
</script>

<style>
/* Add the CSS styles from Part 5 */
</style>