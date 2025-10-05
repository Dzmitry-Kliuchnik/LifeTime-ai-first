<template>
  <div class="about">
    <h1>About LifeTime AI-First</h1>
    <p>This is the frontend application for the LifeTime AI-First project.</p>
    
    <div class="tech-stack">
      <h2>Technology Stack</h2>
      <div class="tech-grid">
        <div class="tech-item">
          <h3>Frontend</h3>
          <p>Vue 3, TypeScript, Vite</p>
        </div>
        <div class="tech-item">
          <h3>State Management</h3>
          <p>Pinia</p>
        </div>
        <div class="tech-item">
          <h3>Routing</h3>
          <p>Vue Router 4</p>
        </div>
        <div class="tech-item">
          <h3>HTTP Client</h3>
          <p>Axios</p>
        </div>
        <div class="tech-item">
          <h3>Testing</h3>
          <p>Vitest, Cypress</p>
        </div>
        <div class="tech-item">
          <h3>Code Quality</h3>
          <p>ESLint, Prettier</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// No reactive data needed for this static view
</script>

<style scoped>
.about {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.tech-stack {
  margin-top: 2rem;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.tech-item {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #42b883;
}

.tech-item h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.tech-item p {
  color: #666;
  margin: 0;
}
</style>