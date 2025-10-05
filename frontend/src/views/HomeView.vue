<template>
  <div class="home">
    <HelloWorld 
      title="LifeTime AI-First Frontend"
      message="Vue 3 + TypeScript + Vite + Pinia setup is ready!"
    />
    
    <div class="features">
      <h2>Features Included:</h2>
      <ul>
        <li>✅ Vue 3 with Composition API</li>
        <li>✅ TypeScript support</li>
        <li>✅ Vue Router for navigation</li>
        <li>✅ Pinia for state management</li>
        <li>✅ Axios for API calls</li>
        <li>✅ Vitest for unit testing</li>
        <li>✅ Cypress for E2E testing</li>
        <li>✅ ESLint + Prettier for code quality</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import HelloWorld from '@/components/HelloWorld.vue'
</script>

<style scoped>
.home {
  padding: 2rem;
}

.features {
  max-width: 600px;
  margin: 2rem auto;
  text-align: left;
}

.features h2 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.features ul {
  list-style: none;
  padding: 0;
}

.features li {
  padding: 0.5rem 0;
  font-size: 1.1rem;
}
</style>