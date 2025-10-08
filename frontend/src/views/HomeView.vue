<template>
  <div class="home">
    <!-- Header Section -->
    <div class="hero-section">
      <h1>Your Life in Weeks</h1>
      <p class="hero-subtitle">
        Visualize your entire lifetime as a grid of weeks. Each square represents one week of your
        life.
      </p>
    </div>

    <!-- User Setup Section -->
    <div v-if="!isUserSetup" class="setup-section">
      <div class="setup-card">
        <h2>Let's Get Started</h2>
        <p>Enter your name to begin creating your life grid:</p>

        <form @submit.prevent="handleNameSubmit" class="setup-form">
          <div class="form-group">
            <label for="full-name">Full Name:</label>
            <input
              id="full-name"
              v-model="setupData.fullName"
              type="text"
              required
              class="form-control"
              placeholder="Enter your full name"
            />
          </div>

          <button type="submit" class="btn-primary" :disabled="isLoading || !setupData.fullName.trim()">
            {{ isLoading ? 'Checking...' : 'Continue' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Life Grid Section -->
    <div v-else class="grid-section">
      <div class="grid-header">
        <div class="life-stats" v-if="lifeProgress">
          <div class="stat-item" v-if="lifeProgress?.age_info?.years !== undefined">
            <span class="stat-label">Age:</span>
            <span class="stat-value">{{ lifeProgress.age_info?.years }} years</span>
          </div>
          <div class="stat-item" v-if="lifeProgress.weeks_lived !== undefined">
            <span class="stat-label">Weeks Lived:</span>
            <span class="stat-value">{{ lifeProgress.weeks_lived.toLocaleString() }}</span>
          </div>
          <div class="stat-item" v-if="lifeProgress.progress_percentage !== undefined">
            <span class="stat-label">Progress:</span>
            <span class="stat-value">{{ lifeProgress.progress_percentage.toFixed(1) }}%</span>
          </div>
        </div>
      </div>

      <!-- Grid Controls -->
      <div class="grid-controls">
        <button @click="resetUser" class="btn-outline">Change User Info</button>
      </div>

      <!-- The LifetimeGrid Component -->
      <LifetimeGrid
        :interactive="true"
        :show-notes="true"
        :highlighted-weeks="visibleHighlightedWeeks"
        :hide-selected-week="
          isNotesModalOpen && selectedWeekForNotes ? selectedWeekForNotes.weekIndex : null
        "
        :cell-size="12"
        max-width="none"
        @weekClick="handleWeekClick"
        @weekHover="handleWeekHover"
        @weekFocus="handleWeekFocus"
        @weekLeave="handleWeekLeave"
      />
    </div>

    <!-- Week Hover Tooltip -->
    <div
      v-if="hoveredWeekInfo"
      class="week-hover-tooltip"
      :style="{
        left: hoveredWeekInfo.x + 'px',
        top: hoveredWeekInfo.y + 'px',
      }"
    >
      <div class="tooltip-header">
        <strong>Week {{ hoveredWeekInfo.weekIndex + 1 }}</strong>
      </div>
      <div class="tooltip-content">
        <p>Year {{ Math.floor(hoveredWeekInfo.weekIndex / 52) + 1 }} of life</p>
        <p>Week {{ (hoveredWeekInfo.weekIndex % 52) + 1 }} of year</p>
        <p class="week-status" :class="`status-${hoveredWeekInfo.weekData.type}`">
          Status: {{ hoveredWeekInfo.weekData.type }}
        </p>
        <p v-if="hoveredWeekInfo.weekData.specialDateType" class="special-date">
          Special: {{ hoveredWeekInfo.weekData.specialDateType }}
        </p>
      </div>
    </div>



    <!-- Notes Modal -->
    <NotesModal
      :isOpen="isNotesModalOpen"
      @update:isOpen="isNotesModalOpen = $event"
      @close="handleNotesModalClose"
      :title="
        selectedWeekForNotes ? `Notes for Week ${selectedWeekForNotes.weekIndex + 1}` : 'Notes'
      "
      :description="
        selectedWeekForNotes
          ? `Year ${Math.floor(selectedWeekForNotes.weekIndex / 52) + 1}, Week ${(selectedWeekForNotes.weekIndex % 52) + 1}`
          : ''
      "
      variant="modal"
      size="large"
    >
      <template #headerActions>
        <NotesInterface
          v-if="selectedWeekForNotes"
          :initial-week-number="selectedWeekForNotes.weekIndex"
          :header-actions-only="true"
          @create-note-request="handleCreateNoteRequest"
          @toggle-search-request="handleToggleSearchRequest"
        />
      </template>

      <NotesInterface
        ref="mainNotesInterface"
        v-if="selectedWeekForNotes"
        :initial-week-number="selectedWeekForNotes.weekIndex"
        :hide-header-actions="true"
      />
    </NotesModal>

    <!-- User Confirmation Modal -->
    <UserConfirmationModal
      :is-open="isConfirmationModalOpen"
      :title="confirmationModalTitle"
      :message="confirmationModalMessage"
      :confirm-button-text="confirmationButtonText"
      :existing-date-of-birth="existingUserData?.date_of_birth"
      :existing-lifespan="existingUserData?.lifespan"
      @close="handleConfirmationModalClose"
      @confirm="handleUserDataConfirmation"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useWeekCalculationStore } from '@/stores/week-calculation'
import LifetimeGrid from '@/components/LifetimeGrid.vue'
import NotesModal from '@/components/notes/NotesModal.vue'
import NotesInterface from '@/components/notes/NotesInterface.vue'
import UserConfirmationModal from '@/components/UserConfirmationModal.vue'

// Stores
const userStore = useUserStore()
const weekCalculationStore = useWeekCalculationStore()

// Setup form data
const setupData = ref({
  dateOfBirth: '',
  lifespan: 80,
  fullName: '',
})

// Component state
const isLoading = ref(false)
const highlightedWeeks = ref<number[]>([])
const isNotesModalOpen = ref(false)
const selectedWeekForNotes = ref<{ weekIndex: number; weekData: any } | null>(null)
const mainNotesInterface = ref<InstanceType<typeof NotesInterface> | null>(null)
const hasConfirmedUser = ref(false) // Track if user has been confirmed in this session

// User confirmation modal state
const isConfirmationModalOpen = ref(false)
const confirmationModalTitle = ref('')
const confirmationModalMessage = ref('')
const confirmationButtonText = ref('Continue')
const existingUserData = ref<{ date_of_birth?: string; lifespan?: number } | null>(null)

// Hover tooltip state
const hoveredWeekInfo = ref<{
  weekIndex: number
  weekData: any
  x: number
  y: number
} | null>(null)

// Computed properties
const isUserSetup = computed(() => {
  // Always show setup form on page load unless user has been confirmed in this session
  return hasConfirmedUser.value && userStore.currentUser?.date_of_birth && userStore.currentUser?.lifespan
})

const lifeProgress = computed(() => weekCalculationStore.lifeProgress)

// Filter highlighted weeks to exclude the one with open modal
const visibleHighlightedWeeks = computed(() => {
  if (!isNotesModalOpen.value || !selectedWeekForNotes.value) {
    return highlightedWeeks.value
  }

  // Remove the week for which the modal is currently open
  const modalWeekIndex = selectedWeekForNotes.value.weekIndex
  return highlightedWeeks.value.filter((weekIndex) => weekIndex !== modalWeekIndex)
})

// Methods
async function handleNameSubmit() {
  if (!setupData.value.fullName.trim()) {
    return
  }

  isLoading.value = true

  try {
    // Check if user exists by name
    const existingUser = await userStore.getUserByName(setupData.value.fullName.trim())
    
    if (existingUser) {
      // User exists - show confirmation modal with prepopulated data
      existingUserData.value = {
        date_of_birth: existingUser.date_of_birth,
        lifespan: existingUser.lifespan,
      }
      confirmationModalTitle.value = 'User Found'
      confirmationModalMessage.value = `We found an existing user with the name "${setupData.value.fullName}". Please confirm or update your details:`
      confirmationButtonText.value = 'Update Life Grid'
    } else {
      // User doesn't exist - show confirmation modal for new user
      existingUserData.value = null
      confirmationModalTitle.value = 'Create Your Life Grid'
      confirmationModalMessage.value = `Hi ${setupData.value.fullName}! Please provide your birth date and expected lifespan to create your life grid:`
      confirmationButtonText.value = 'Create Life Grid'
    }
    
    isConfirmationModalOpen.value = true
  } catch (error) {
    console.error('Error checking user:', error)
    // If getUserByName fails (user doesn't exist), treat as new user
    existingUserData.value = null
    confirmationModalTitle.value = 'Create Your Life Grid'
    confirmationModalMessage.value = `Hi ${setupData.value.fullName}! Please provide your birth date and expected lifespan to create your life grid:`
    confirmationButtonText.value = 'Create Life Grid'
    isConfirmationModalOpen.value = true
  } finally {
    isLoading.value = false
  }
}

function handleConfirmationModalClose() {
  isConfirmationModalOpen.value = false
  existingUserData.value = null
}

async function handleUserDataConfirmation(userData: { dateOfBirth: string; lifespan: number }) {
  isLoading.value = true
  
  try {
    // Create or update user using the findOrCreateUserByName API
    const user = await userStore.findOrCreateUserByName({
      full_name: setupData.value.fullName.trim(),
      date_of_birth: userData.dateOfBirth,
      lifespan: userData.lifespan,
      theme: 'light',
      font_size: 14,
    })

    if (!user) {
      console.error('Failed to create or find user')
      return
    }

    await setupUserData(user, userData)
    hasConfirmedUser.value = true // Mark user as confirmed in this session
    isConfirmationModalOpen.value = false
    existingUserData.value = null
  } catch (error) {
    console.error('User setup failed:', error)
  } finally {
    isLoading.value = false
  }
}

async function setupUserData(user: any, userData: { dateOfBirth: string; lifespan: number }) {
  // Use the user's settings for life progress calculation
  const birthDate = new Date(user.date_of_birth || userData.dateOfBirth)
  const now = new Date()
  const daysSinceBirth = Math.floor((now.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24))
  const weeksSinceBirth = Math.floor(daysSinceBirth / 7)
  const totalLifetimeWeeks = Math.floor((user.lifespan || userData.lifespan) * 52.1775)
  const progressPercentage = (weeksSinceBirth / totalLifetimeWeeks) * 100

  const ageYears = Math.floor(
    (now.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24 * 365.25),
  )
  const ageMonths = Math.floor(
    ((now.getTime() - birthDate.getTime()) % (1000 * 60 * 60 * 24 * 365.25)) /
      (1000 * 60 * 60 * 24 * 30.44),
  )
  const ageDays = Math.floor(
    ((now.getTime() - birthDate.getTime()) % (1000 * 60 * 60 * 24 * 30.44)) /
      (1000 * 60 * 60 * 24),
  )

  // Set store values using user data
  const lifeProgress = {
    date_of_birth: user.date_of_birth || userData.dateOfBirth,
    timezone: 'UTC',
    lifespan_years: user.lifespan || userData.lifespan,
    total_weeks: totalLifetimeWeeks,
    current_week_index: weeksSinceBirth,
    weeks_lived: weeksSinceBirth,
    progress_percentage: Math.min(100, progressPercentage),
    age_info: {
      years: ageYears,
      months: ageMonths,
      days: ageDays,
    },
    current_date: now.toISOString().split('T')[0]!,
  }

  // Set store values using persisted user data
  weekCalculationStore.lifeProgress = lifeProgress
  weekCalculationStore.totalWeeks = {
    date_of_birth: user.date_of_birth || userData.dateOfBirth,
    lifespan_years: user.lifespan || userData.lifespan,
    total_weeks: totalLifetimeWeeks,
  }
  weekCalculationStore.currentWeek = {
    date_of_birth: user.date_of_birth || userData.dateOfBirth,
    timezone: 'UTC',
    current_week_index: weeksSinceBirth,
    weeks_lived: weeksSinceBirth,
    current_date: now.toISOString().split('T')[0]!,
  }
}



function handleWeekClick(weekIndex: number, weekData: any) {
  // Add to highlights if not already there
  if (!highlightedWeeks.value.includes(weekIndex)) {
    highlightedWeeks.value.push(weekIndex)
  }

  // Open notes modal for the selected week
  selectedWeekForNotes.value = { weekIndex, weekData }
  isNotesModalOpen.value = true
}

function handleWeekHover(weekIndex: number, weekData: any, event?: MouseEvent) {
  if (event) {
    const rect = (event.target as HTMLElement).getBoundingClientRect()
    const tooltipOffset = 20

    hoveredWeekInfo.value = {
      weekIndex,
      weekData,
      x: rect.left + rect.width / 2,
      y: rect.top - tooltipOffset,
    }
  }
}

function handleWeekFocus(weekIndex: number, weekData: any) {
  // Update accessibility info or show details
  console.log('Focused week:', weekIndex, weekData)
}

function handleWeekLeave() {
  hoveredWeekInfo.value = null
}

function handleNotesModalClose() {
  isNotesModalOpen.value = false
  selectedWeekForNotes.value = null
  // The highlighted week will automatically reappear when the modal closes
}

function handleCreateNoteRequest() {
  // Call the openCreateModal method on the main NotesInterface instance
  if (mainNotesInterface.value) {
    mainNotesInterface.value.openCreateModal()
  }
}

function handleToggleSearchRequest() {
  // Call the toggleSearch method on the main NotesInterface instance
  if (mainNotesInterface.value) {
    mainNotesInterface.value.toggleSearch()
  }
}

function resetUser() {
  userStore.setUser(null)
  hasConfirmedUser.value = false // Reset confirmation flag

  // Reset form data
  setupData.value = {
    dateOfBirth: '',
    lifespan: 80,
    fullName: '',
  }
  highlightedWeeks.value = []
  hoveredWeekInfo.value = null
  isNotesModalOpen.value = false
  selectedWeekForNotes.value = null
  
  // Reset confirmation modal state
  isConfirmationModalOpen.value = false
  existingUserData.value = null
}

// Lifecycle
onMounted(async () => {
  // Load user from storage if available
  const user = userStore.loadUserFromStorage()
  
  // If user exists and has required data, initialize week calculations
  if (user && user.date_of_birth && user.lifespan) {
    try {
      await weekCalculationStore.initializeForUser()
    } catch (error) {
      console.error('Failed to initialize week calculations:', error)
    }
  }
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
  transition:
    border-color 0.3s ease,
    box-shadow 0.3s ease;
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
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
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
  padding: 2rem 1rem;
  width: 100%;
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
    padding: 1rem 0.5rem;
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

/* Week hover tooltip styles */
.week-hover-tooltip {
  position: fixed;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  font-size: 0.9rem;
  min-width: 200px;
  pointer-events: none;
  opacity: 0.95;

  &::before {
    content: '';
    position: absolute;
    top: -8px;
    left: 50%;
    transform: translateX(-50%);
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-bottom: 8px solid white;
  }

  &::after {
    content: '';
    position: absolute;
    top: -9px;
    left: 50%;
    transform: translateX(-50%);
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-bottom: 8px solid #ddd;
  }
}

.week-info {
  h4 {
    margin: 0 0 8px 0;
    color: #333;
    font-size: 1rem;
  }

  p {
    margin: 4px 0;
    color: #666;
    font-size: 0.85rem;
  }

  .week-dates {
    font-weight: 500;
    color: #2563eb;
  }

  .week-stats {
    border-top: 1px solid #eee;
    padding-top: 8px;
    margin-top: 8px;
  }
}

/* Dark mode styles for tooltip */
@media (prefers-color-scheme: dark) {
  .week-hover-tooltip {
    background: #2d3748;
    border-color: #4a5568;
    color: #e2e8f0;

    &::before {
      border-bottom-color: #2d3748;
    }

    &::after {
      border-bottom-color: #4a5568;
    }
  }

  .week-info {
    h4 {
      color: #e2e8f0;
    }

    p {
      color: #a0aec0;
    }

    .week-dates {
      color: #63b3ed;
    }

    .week-stats {
      border-color: #4a5568;
    }
  }
}
</style>
