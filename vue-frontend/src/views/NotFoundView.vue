<template>
  <main class="wrap">
    <div class="card">
      <h1 class="code">404</h1>
      <p class="msg">Page not found.</p>
      <router-link to="/" class="btn">Go home</router-link>
    </div>
  </main>
</template>

<style scoped>
.wrap{
  min-height:100vh;
  display:flex;
  align-items:center;
  justify-content:center;
  padding:24px;
  background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
}
.card{
  width:100%;
  max-width:520px;
  background:#fff;
  border-radius:12px;
  box-shadow:0 10px 25px rgba(0,0,0,.12);
  padding:2rem;
  text-align:center;
}
.code{
  margin:0;
  font-size:3rem;
  color:#111;
}
.msg{
  margin:.5rem 0 1.25rem;
  color:#666;
}
.btn{
  display:inline-block;
  padding:.75rem 1.25rem;
  border-radius:8px;
  text-decoration:none;
  font-weight:700;
  color:#fff;
  background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
}
.btn:hover{opacity:.92}
</style>
