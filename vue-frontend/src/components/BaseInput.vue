<script setup>
import { computed } from 'vue'
const props = defineProps({
  modelValue: String,
  type: { type: String, default: 'text' },
  placeholder: String,
  id: String,
  error: String,
  label: String
})
const emit = defineEmits(['update:modelValue','clear'])
const model = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v)
})
</script>

<template>
  <div class="form-group">
    <label v-if="label" :for="id">{{ label }}</label>
    <input :id="id" v-model="model" :type="type" :placeholder="placeholder"
           :class="{ 'error-input': !!error }" @input="$emit('clear')" />
    <span v-if="error" class="error-message">{{ error }}</span>
  </div>
</template>

<style scoped>
.form-group{margin-bottom:1.5rem}
label{display:block;margin-bottom:.5rem;color:#333;font-weight:500}
input{width:100%;padding:.75rem;border:2px solid #e1e5e9;border-radius:6px;font-size:1rem;box-sizing:border-box;background:#f8f9fa;transition:border-color .3s}
input:focus{outline:none;border-color:#667eea;background:#fff}
.error-input{border-color:#e74c3c;background:#fee}
.error-message{color:#e74c3c;font-size:.875rem;margin-top:.25rem;display:block}
</style>

