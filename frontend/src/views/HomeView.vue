<template>
  <div class="home">
    <!-- Header Section -->
    <div class="hero-section">
      <h1>Your Life in Weeks</h1>
      <p class="hero-subtitle">
        Visualize your entire lifetime as a grid of weeks. Each square represents one week of your life.
      </p>
    </div>

    <!-- User Setup Section -->
    <div v-if="!isUserSetup" class="setup-section">
      <div class="setup-card">
        <h2>Let's Get Started</h2>
        <p>To display your life grid, we need some basic information:</p>
        
        <form @submit.prevent="handleQuickSetup" class="setup-form">
          <div class="form-group">
            <label for="birth-date">Date of Birth:</label>
            <input
              id="birth-date"
              v-model="setupData.dateOfBirth"
              type="date"
              required
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="lifespan">Expected Lifespan (years):</label>
            <input
              id="lifespan"
              v-model.number="setupData.lifespan"
              type="number"
              min="50"
              max="120"
              required
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="full-name">Full Name (optional):</label>
            <input
              id="full-name"
              v-model="setupData.fullName"
              type="text"
              class="form-control"
              placeholder="Your full name"
            />
          </div>
          
          <button type="submit" class="btn-primary" :disabled="isLoading">
            {{ isLoading ? 'Setting up...' : 'Create My Life Grid' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Life Grid Section -->
    <div v-else class="grid-section">
      <div class="grid-header">
        <h2>Your Life Journey</h2>
        <div class="life-stats" v-if="lifeProgress">
          <div class="stat-item">
            <span class="stat-label">Age:</span>
            <span class="stat-value">{{ lifeProgress.age_info.years }} years</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Weeks Lived:</span>
            <span class="stat-value">{{ lifeProgress.weeks_lived.toLocaleString() }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Progress:</span>
            <span class="stat-value">{{ lifeProgress.progress_percentage.toFixed(1) }}%</span>
          </div>
        </div>
      </div>

      <!-- The LifetimeGrid Component -->
      <LifetimeGrid
        :interactive="true"
        :show-notes="true"
        :highlighted-weeks="highlightedWeeks"
        :cell-size="12"
        max-width="100%"
        @week-click="handleWeekClick"
        @week-hover="handleWeekHover"
        @week-focus="handleWeekFocus"
      />

      <!-- Grid Controls -->
      <div class="grid-controls">
        <button @click="jumpToCurrentWeek" class="btn-secondary">
          Jump to Current Week
        </button>
        <button @click="clearHighlights" class="btn-secondary">
          Clear Highlights
        </button>
        <button @click="resetUser" class="btn-outline">
          Change User Info
        </button>
      </div>

      <!-- Selected Week Info -->
      <div v-if="selectedWeekInfo" class="week-info-panel">
        <h3>Week Information</h3>
        <div class="week-details">
          <p><strong>Week {{ selectedWeekInfo.weekIndex + 1 }}</strong></p>
          <p>Year {{ Math.floor(selectedWeekInfo.weekIndex / 52) + 1 }} of life</p>
          <p>Week {{ (selectedWeekInfo.weekIndex % 52) + 1 }} of year</p>
          <p>Status: {{ selectedWeekInfo.weekData.type }}</p>
          <p v-if="selectedWeekInfo.weekData.specialDateType">
            Special: {{ selectedWeekInfo.weekData.specialDateType }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useWeekCalculationStore } from '@/stores/week-calculation'
import LifetimeGrid from '@/components/LifetimeGrid.vue'

// Stores
const userStore = useUserStore()
const weekCalculationStore = useWeekCalculationStore()

// Setup form data
const setupData = ref({
  dateOfBirth: '',
  lifespan: 80,
  fullName: ''
})

// Component state
const isLoading = ref(false)
const highlightedWeeks = ref<number[]>([])
const selectedWeekInfo = ref<{
  weekIndex: number
  weekData: any
} | null>(null)

// Computed properties
const isUserSetup = computed(() => {
  return userStore.currentUser?.date_of_birth && userStore.currentUser?.lifespan
})

const lifeProgress = computed(() => weekCalculationStore.lifeProgress)

// Methods
async function handleQuickSetup() {
  if (!setupData.value.dateOfBirth || !setupData.value.lifespan) {
    return
  }

  isLoading.value = true
  
  try {
    // Create a mock user for demonstration
    // In a real app, this would call the user API
    userStore.currentUser = {
      id: 1,
      username: 'demo-user',
      email: 'demo@example.com',
      full_name: setupData.value.fullName || 'Demo User',
      date_of_birth: setupData.value.dateOfBirth,
      lifespan: setupData.value.lifespan,
      theme: 'light' as const,
      is_active: true,
      is_verified: true,
      is_superuser: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    // Mock life progress calculation for demo
    const birthDate = new Date(setupData.value.dateOfBirth)
    const now = new Date()
    const daysSinceBirth = Math.floor((now.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24))
    const weeksSinceBirth = Math.floor(daysSinceBirth / 7)
    const totalLifetimeWeeks = Math.floor(setupData.value.lifespan * 52.1775)
    const progressPercentage = (weeksSinceBirth / totalLifetimeWeeks) * 100
    
    const ageYears = Math.floor((now.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24 * 365.25))
    const ageMonths = Math.floor(((now.getTime() - birthDate.getTime()) % (1000 * 60 * 60 * 24 * 365.25)) / (1000 * 60 * 60 * 24 * 30.44))
    const ageDays = Math.floor(((now.getTime() - birthDate.getTime()) % (1000 * 60 * 60 * 24 * 30.44)) / (1000 * 60 * 60 * 24))

    // Manually set the store values for demo
    const mockLifeProgress = {
      date_of_birth: setupData.value.dateOfBirth,
      timezone: 'UTC',
      lifespan_years: setupData.value.lifespan,
      total_weeks: totalLifetimeWeeks,
      current_week_index: weeksSinceBirth,
      weeks_lived: weeksSinceBirth,
      progress_percentage: Math.min(100, progressPercentage),
      age_info: {
        years: ageYears,
        months: ageMonths,
        days: ageDays
      },
      current_date: now.toISOString().split('T')[0]!
    }

    // Set store values directly for demo (since we don't have API)
    weekCalculationStore.lifeProgress = mockLifeProgress
    weekCalculationStore.totalWeeks = {
      date_of_birth: setupData.value.dateOfBirth,
      lifespan_years: setupData.value.lifespan,
      total_weeks: totalLifetimeWeeks
    }
    weekCalculationStore.currentWeek = {
      date_of_birth: setupData.value.dateOfBirth,
      timezone: 'UTC',
      current_week_index: weeksSinceBirth,
      weeks_lived: weeksSinceBirth,
      current_date: now.toISOString().split('T')[0]!
    }

  } catch (error) {
    console.error('Setup failed:', error)
    // Handle error appropriately
  } finally {
    isLoading.value = false
  }
}

function handleWeekClick(weekIndex: number, weekData: any) {
  selectedWeekInfo.value = { weekIndex, weekData }
  
  // Add to highlights if not already there
  if (!highlightedWeeks.value.includes(weekIndex)) {
    highlightedWeeks.value.push(weekIndex)
  }
}

function handleWeekHover(weekIndex: number, weekData: any) {
  // Optional: Show tooltip or temporary info
  console.log('Hovered week:', weekIndex, weekData)
}

function handleWeekFocus(weekIndex: number, weekData: any) {
  // Update accessibility info or show details
  console.log('Focused week:', weekIndex, weekData)
}

function jumpToCurrentWeek() {
  const currentWeek = weekCalculationStore.currentWeekIndex
  if (currentWeek !== null) {
    highlightedWeeks.value = [currentWeek]
    selectedWeekInfo.value = null
  }
}

function clearHighlights() {
  highlightedWeeks.value = []
  selectedWeekInfo.value = null
}

function resetUser() {
  userStore.currentUser = null
  
  // Reset form data
  setupData.value = {
    dateOfBirth: '',
    lifespan: 80,
    fullName: ''
  }
  highlightedWeeks.value = []
  selectedWeekInfo.value = null
  
  // Set default birth date again
  const thirtyYearsAgo = new Date()
  thirtyYearsAgo.setFullYear(thirtyYearsAgo.getFullYear() - 30)
  setupData.value.dateOfBirth = thirtyYearsAgo.toISOString().split('T')[0]!
}

// Lifecycle
onMounted(() => {
  // Set default birth date to 30 years ago for demo
  const thirtyYearsAgo = new Date()
  thirtyYearsAgo.setFullYear(thirtyYearsAgo.getFullYear() - 30)
  setupData.value.dateOfBirth = thirtyYearsAgo.toISOString().split('T')[0]!
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
}

/* Hero Section */
.hero-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: white;
  text-align: center;
  padding: 3rem 2rem;
  margin-bottom: 2rem;
}

.hero-section h1 {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

/* Setup Section */
.setup-section {
  max-width: 500px;
  margin: 0 auto;
  padding: 0 2rem 4rem;
}

.setup-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.setup-card h2 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.8rem;
}

.setup-card p {
  color: #666;
  margin-bottom: 1.5rem;
}

/* Form Styles */
.setup-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.form-control {
  padding: 0.75rem;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  margin-top: 1rem;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Grid Section */
.grid-section {
  background: white;
  min-height: 100vh;
  padding: 2rem;
}

.grid-header {
  text-align: center;
  margin-bottom: 2rem;
}

.grid-header h2 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.life-stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  min-width: 120px;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2c3e50;
}

/* Grid Controls */
.grid-controls {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin: 2rem 0;
  flex-wrap: wrap;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-outline {
  background: transparent;
  color: #6c757d;
  border: 2px solid #6c757d;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-outline:hover {
  background: #6c757d;
  color: white;
}

/* Week Info Panel */
.week-info-panel {
  max-width: 400px;
  margin: 2rem auto;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  border-left: 4px solid #667eea;
}

.week-info-panel h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.week-details p {
  margin: 0.5rem 0;
  color: #555;
}

.week-details strong {
  color: #2c3e50;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-section {
    padding: 2rem 1rem;
  }
  
  .hero-section h1 {
    font-size: 2rem;
  }
  
  .setup-section {
    padding: 0 1rem 2rem;
  }
  
  .setup-card {
    padding: 1.5rem;
  }
  
  .grid-section {
    padding: 1rem;
  }
  
  .grid-header h2 {
    font-size: 2rem;
  }
  
  .life-stats {
    gap: 1rem;
  }
  
  .stat-item {
    min-width: 100px;
    padding: 0.75rem;
  }
  
  .grid-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .btn-secondary,
  .btn-outline {
    width: 100%;
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .hero-section h1 {
    font-size: 1.8rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .life-stats {
    flex-direction: column;
    align-items: center;
  }
}
</style>