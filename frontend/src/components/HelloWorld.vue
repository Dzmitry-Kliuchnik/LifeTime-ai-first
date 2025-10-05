<template>
  <div class="hello-world">
    <h1>{{ title }}</h1>
    <p>{{ message }}</p>
    <button @click="increment" :disabled="loading">
      Count: {{ count }} ({{ loading ? 'Loading...' : 'Click me!' }})
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  title?: string
  message?: string
}

// Props are automatically available in template
withDefaults(defineProps<Props>(), {
  title: 'Hello World',
  message: 'Welcome to Vue 3 + TypeScript + Vite'
})

const count = ref(0)
const loading = ref(false)

const increment = async () => {
  loading.value = true
  // Simulate async operation
  await new Promise(resolve => setTimeout(resolve, 500))
  count.value++
  loading.value = false
}
</script>

<style scoped>
.hello-world {
  text-align: center;
  padding: 2rem;
}

h1 {
  color: #42b883;
  margin-bottom: 1rem;
}

button {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

button:hover:not(:disabled) {
  background-color: #369870;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>