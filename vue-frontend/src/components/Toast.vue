<script setup>
import { onMounted, onBeforeUnmount, watch, ref } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  message: { type: String, default: '' },
  type: { type: String, default: 'success' },
  duration: { type: Number, default: 2200 }
})
const emit = defineEmits(['close'])

let timer = null
const visible = ref(false)

function startTimer() {
  clearTimeout(timer)
  if (props.open) {
    timer = setTimeout(() => emit('close'), props.duration)
  }
}

watch(() => props.open, (val) => {
  visible.value = val
  if (val) startTimer()
})

onMounted(() => {
  if (props.open) startTimer()
})
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
  <transition name="toast-fade">
    <div
      v-if="visible"
      class="toast"
      :class="type"
      role="status"
      @mouseenter="clearTimeout(timer)"
      @mouseleave="startTimer"
    >
      <span class="dot" />
      <span class="msg">{{ message }}</span>
      <button class="x" @click="$emit('close')" aria-label="Close">×</button>
    </div>
  </transition>
</template>

<style scoped>
.toast{
  position: fixed; right: 18px; bottom: 18px; z-index: 60;
  display: inline-flex; align-items: center; gap: .6rem;
  padding: .7rem .9rem; border-radius: 10px; box-shadow: 0 10px 24px rgba(0,0,0,.18);
  color: #111; background: #fff; border: 1px solid #e6e9ef; max-width: 78vw;
}
.toast.success .dot{ background: #22c55e; border-color:#16a34a }
.toast.error   .dot{ background: #ef4444; border-color:#dc2626 }
.toast.info    .dot{ background: #3b82f6; border-color:#2563eb }
.toast.warn    .dot{ background: #f59e0b; border-color:#d97706 }

.dot{ width:10px; height:10px; border-radius:999px; border:2px solid currentColor; }
.msg{ line-height:1.3 }
.x{
  margin-left:.25rem; border:none; background:transparent; font-size:1.1rem; cursor:pointer;
  color:#555;
}
.x:hover{ color:#111 }

.toast-fade-enter-active,.toast-fade-leave-active{ transition: all .18s ease }
.toast-fade-enter-from,.toast-fade-leave-to{ opacity:0; transform: translateY(6px) scale(.98) }
</style>
