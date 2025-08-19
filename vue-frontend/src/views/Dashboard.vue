<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <nav class="sidebar">
      <router-link to="/dashboard" class="nav-item">Home</router-link>
      <router-link to="/wordbank" class="nav-item">Word Bank</router-link>
      <router-link to="/search" class="nav-item">Search Articles</router-link>
      <button @click="handleSignOut" class="nav-item">Sign Out</button>
    </nav>
    <main class="content">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
export default {
  methods: {
    handleSignOut() {
      localStorage.removeItem('authToken')
      localStorage.removeItem('user')
      this.$router.push('/')
    }
  }
}
</script>