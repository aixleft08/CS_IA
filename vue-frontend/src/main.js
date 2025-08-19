import { createApp } from 'vue'
import './style.css'
import App from './views/App.vue'
import router from './router'

createApp(App).mount('#app')
app.use(router)