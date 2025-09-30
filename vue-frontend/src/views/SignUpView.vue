<template>
  <div class="page">
    <div class="card">
      <div class="head"><h1>Enlingo</h1><h2>Welcome</h2></div>
      <AuthForm mode="sign-up" />
    </div>
  </div>
</template>

<script setup>
import AuthForm from '@/components/AuthForm.vue'
</script>

<style scoped>
.page{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:20px}
.card{background:#fff;padding:2.5rem;border-radius:12px;box-shadow:0 10px 25px rgba(0,0,0,.1);width:100%;max-width:400px}
.head{text-align:center;margin-bottom:2rem}
.head h1{color:#333;font-size:2rem;font-weight:700;margin-bottom:.5rem}
.head h2{color:#666;font-size:1.25rem;margin:0}
@media (max-width:480px){.card{padding:1.5rem;margin:1rem}.head h1{font-size:1.75rem}.head h2{font-size:1.1rem}}
</style>
