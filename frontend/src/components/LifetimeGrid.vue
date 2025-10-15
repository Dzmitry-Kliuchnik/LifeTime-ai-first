<template>
  <section
    ref="containerRef"
    class="lifetime-grid-container"
    :class="{ 'is-loading': isLoading }"
    :aria-label="`Life visualization grid for ${totalWeeks} weeks`"
    aria-describedby="grid-description"
  >
    <!-- Screen reader description -->
    <div id="grid-description" class="sr-only">
      A visual representation of your lifetime in weeks. Each cell represents one week. Past weeks
      are shown in darker colors, current week is highlighted, and future weeks are in lighter
      colors. Use arrow keys to navigate the grid, Enter or Space to select a week, Home to go to
      first week, End to go to last week.
    </div>

    <!-- Live region for screen reader announcements -->
    <div id="week-announcements" class="sr-only" aria-live="polite" aria-atomic="true"></div>

    <!-- Loading state -->
    <div v-if="isLoading" class="loading-overlay" aria-live="polite">
      <div class="loading-spinner"></div>
      <span>Loading life visualization...</span>
    </div>

    <!-- Error state -->
    <div v-if="error" class="error-state" role="alert">
      <p>{{ error }}</p>
      <button @click="handleRetry" class="retry-button">Retry</button>
    </div>

    <!-- Grid content -->
    <div
      v-if="!isLoading && !error && gridWeeks.length > 0"
      class="lifetime-grid"
      :style="gridStyles"
      :aria-rowcount="totalRows"
      :aria-colcount="WEEKS_PER_ROW"
      role="application"
      aria-label="Interactive lifetime grid - use arrow keys to navigate"
      @keydown="handleKeyNavigation"
    >
      <div
        v-for="(week, index) in gridWeeks"
        :key="`week-${index}`"
        class="week-cell"
        :class="getWeekClasses(week, index)"
        :style="getWeekStyles(week, index)"
        :data-week-index="index"
        :data-week-type="week.type"
        :aria-label="getWeekAriaLabel(week, index)"
        :aria-selected="selectedWeekIndex === index"
        :tabindex="selectedWeekIndex === index ? 0 : -1"
        @click="handleWeekClick(index)"
        @focus="handleWeekFocus(index)"
        @mouseenter="handleWeekHover(index)"
        @mouseleave="handleWeekHoverEnd"
      >
        <!-- Week content (notes indicator, special markers, etc.) -->
        <div v-if="week.hasNotes" class="notes-indicator" aria-hidden="true"></div>
        <div v-if="week.isSpecialDate" class="special-marker" :title="week.specialDateType"></div>
      </div>
    </div>

    <!-- Grid legend -->
    <section class="grid-legend" aria-label="Grid legend">
      <div class="legend-item">
        <div class="legend-color past-week"></div>
        <span>Past weeks</span>
      </div>
      <div class="legend-item">
        <div class="legend-color current-week"></div>
        <span>Current week</span>
      </div>
      <div class="legend-item">
        <div class="legend-color future-week"></div>
        <span>Future weeks</span>
      </div>
      <div class="legend-item">
        <div class="legend-color birthday-marker"></div>
        <span>Birthday</span>
      </div>
      <div class="legend-item">
        <div class="legend-color year-start-marker"></div>
        <span>Year start</span>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useWeekCalculationStore } from '@/stores/week-calculation'
import { useUserStore } from '@/stores/user'
import { WeekType } from '@/types'

// Props
interface Props {
  highlightedWeeks?: number[]
  showNotes?: boolean
  interactive?: boolean
  maxWidth?: string
  cellSize?: number
  hideSelectedWeek?: number | null // Week index to hide selection for
}

const props = withDefaults(defineProps<Props>(), {
  highlightedWeeks: () => [],
  showNotes: true,
  interactive: true,
  maxWidth: '100%',
  cellSize: 12,
  hideSelectedWeek: null,
})

// Emits
const emit = defineEmits<{
  weekClick: [weekIndex: number, weekData: GridWeek]
  weekHover: [weekIndex: number, weekData: GridWeek]
  weekLeave: []
  weekFocus: [weekIndex: number, weekData: GridWeek]
}>()

// Constants
const WEEKS_PER_ROW = 52

// Stores
const weekCalculationStore = useWeekCalculationStore()
const userStore = useUserStore()

// Reactive state
const selectedWeekIndex = ref<number | null>(null)
const hoveredWeekIndex = ref<number | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)
const containerRef = ref<HTMLElement | null>(null)
const forceUpdate = ref(0)

// Grid week interface
interface GridWeek {
  type: WeekType
  weekNumber: number
  hasNotes: boolean
  isSpecialDate: boolean
  specialDateType?: string
  isBirthday: boolean
  isYearStart: boolean
  isHighlighted: boolean
  borderPriority: number
}

// Computed properties
const totalWeeks = computed(() => weekCalculationStore.totalLifetimeWeeks || 0)
const currentWeekIndex = computed(() => weekCalculationStore.currentWeekIndex || 0)

const totalRows = computed(() => Math.ceil(totalWeeks.value / WEEKS_PER_ROW))

// Calculate dynamic cell size for full-width mode
const dynamicCellSize = computed(() => {
  // Force reactivity update by accessing the value
  const _forceUpdate = forceUpdate.value

  if (props.maxWidth !== 'none' || !containerRef.value) {
    return props.cellSize
  }

  // Get container width and calculate optimal cell size
  const containerWidth = containerRef.value.clientWidth
  const gapSpace = (WEEKS_PER_ROW - 1) * 1 // 1px gaps between cells
  const padding = 2 // 1px padding on each side
  const availableWidth = containerWidth - gapSpace - padding
  const optimalCellSize = Math.floor(availableWidth / WEEKS_PER_ROW)

  // Responsive minimum cell sizes based on screen width
  let minCellSize = 6
  if (containerWidth < 480) {
    minCellSize = 4
  } else if (containerWidth < 768) {
    minCellSize = 5
  }

  const maxCellSize = 24 // Maximum cell size to prevent cells from becoming too large on very wide screens

  return Math.max(minCellSize, Math.min(maxCellSize, optimalCellSize))
})

const gridStyles = computed(() => ({
  '--weeks-per-row': WEEKS_PER_ROW,
  '--cell-size': `${dynamicCellSize.value}px`,
  '--max-width': props.maxWidth,
  '--total-rows': totalRows.value,
}))

// Generate grid weeks data
const gridWeeks = computed((): GridWeek[] => {
  if (!totalWeeks.value || !userStore.hasDateOfBirth) {
    return []
  }

  const weeks: GridWeek[] = []

  for (let i = 0; i < totalWeeks.value; i++) {
    const weekType = getWeekType(i)
    const isYearStart = isYearStartWeek(i)
    const isBirthday = isBirthdayWeek(i)
    const isHighlighted = props.highlightedWeeks.includes(i)

    weeks.push({
      type: weekType,
      weekNumber: i,
      hasNotes: false, // Note: Notes integration will be added in future iteration
      isSpecialDate: isYearStart || isBirthday,
      specialDateType: getSpecialDateType(isYearStart, isBirthday),
      isBirthday,
      isYearStart,
      isHighlighted,
      borderPriority: getBorderPriority(isYearStart, isBirthday, isHighlighted, i),
    })
  }

  return weeks
})

// Week type calculation
function getWeekType(weekIndex: number): WeekType {
  const current = currentWeekIndex.value
  if (current === null) return WeekType.FUTURE

  if (weekIndex < current) {
    return WeekType.PAST
  } else if (weekIndex === current) {
    return WeekType.CURRENT
  } else {
    return WeekType.FUTURE
  }
}

// Special date detection with improved accuracy
function isYearStartWeek(weekIndex: number): boolean {
  if (!userStore.currentUser?.date_of_birth) return false

  // Calculate which week corresponds to January 1st of each year
  const birthDate = new Date(userStore.currentUser.date_of_birth)
  const birthYear = birthDate.getFullYear()

  // For each potential year, check if this week index falls on New Year's week
  const weeksPerYear = 52.1775 // More accurate weeks per year
  const estimatedYear = Math.floor(weekIndex / weeksPerYear)

  for (let yearOffset = estimatedYear - 1; yearOffset <= estimatedYear + 1; yearOffset++) {
    const targetYear = birthYear + yearOffset
    const newYearDate = new Date(targetYear, 0, 1) // January 1st
    const daysDiff = Math.floor(
      (newYearDate.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24),
    )
    const newYearWeek = Math.floor(daysDiff / 7)

    if (newYearWeek === weekIndex) {
      return true
    }
  }

  return false
}

function isBirthdayWeek(weekIndex: number): boolean {
  if (!userStore.currentUser?.date_of_birth) return false

  const birthDate = new Date(userStore.currentUser.date_of_birth)
  const weeksPerYear = 52.1775

  // Calculate which year this week falls in
  const estimatedYear = Math.floor(weekIndex / weeksPerYear)

  // Check a range of years around the estimated year
  for (let yearOffset = estimatedYear - 1; yearOffset <= estimatedYear + 1; yearOffset++) {
    if (yearOffset < 0) continue

    const birthdayThisYear = new Date(birthDate)
    birthdayThisYear.setFullYear(birthDate.getFullYear() + yearOffset)

    const daysDiff = Math.floor(
      (birthdayThisYear.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24),
    )
    const birthdayWeek = Math.floor(daysDiff / 7)

    // Check if this week is exactly the birthday week
    if (birthdayWeek === weekIndex) {
      return true
    }
  }

  return false
}

function getSpecialDateType(isYearStart: boolean, isBirthday: boolean): string | undefined {
  if (isBirthday && isYearStart) return 'Birthday & New Year'
  if (isBirthday) return 'Birthday'
  if (isYearStart) return 'New Year'
  return undefined
}

// Enhanced special date detection
interface SpecialDate {
  type: 'birthday' | 'yearStart' | 'milestone' | 'quarter' | 'decade'
  priority: number
  label: string
}

function getSpecialDates(weekIndex: number): SpecialDate[] {
  const specialDates: SpecialDate[] = []

  if (isBirthdayWeek(weekIndex)) {
    const age = Math.floor(weekIndex / 52.1775)
    const isDecade = age > 0 && age % 10 === 0
    const isMilestone = age > 0 && (age % 25 === 0 || age % 50 === 0)

    specialDates.push({
      type: 'birthday',
      priority: getPriorityForBirthday(age, isMilestone, isDecade),
      label: `${age}${getOrdinalSuffix(age)} Birthday`,
    })

    if (isDecade && age % 50 !== 0 && age % 25 !== 0) {
      specialDates.push({
        type: 'decade',
        priority: 8,
        label: `${age}s Begin`,
      })
    }
  }

  if (isYearStartWeek(weekIndex)) {
    const year = Math.floor(weekIndex / 52.1775) + 1
    specialDates.push({
      type: 'yearStart',
      priority: 5,
      label: `Year ${year} Begins`,
    })
  }

  // Quarter-life markers (approximately every 13 weeks)
  if (weekIndex > 0 && weekIndex % 13 === 0) {
    const quarter = Math.floor(weekIndex / 13)
    specialDates.push({
      type: 'quarter',
      priority: 2,
      label: `Quarter ${quarter}`,
    })
  }

  return specialDates
}

function getPriorityForBirthday(age: number, isMilestone: boolean, isDecade: boolean): number {
  if (isMilestone) return 20
  if (isDecade) return 15
  return 10
}

function getOrdinalSuffix(num: number): string {
  const lastDigit = num % 10
  const lastTwoDigits = num % 100

  if (lastTwoDigits >= 11 && lastTwoDigits <= 13) {
    return 'th'
  }

  switch (lastDigit) {
    case 1:
      return 'st'
    case 2:
      return 'nd'
    case 3:
      return 'rd'
    default:
      return 'th'
  }
}

// Border priority for conflict resolution
function getBorderPriority(
  isYearStart: boolean,
  isBirthday: boolean,
  isHighlighted: boolean,
  weekIndex: number,
): number {
  let priority = 0

  // User highlights have highest priority
  if (isHighlighted) priority += 100

  // Get all special dates for this week
  const specialDates = getSpecialDates(weekIndex)
  const maxSpecialPriority = specialDates.reduce((max, date) => Math.max(max, date.priority), 0)
  priority += maxSpecialPriority

  // Legacy support for existing boolean flags
  if (isBirthday && !specialDates.some((d) => d.type === 'birthday')) {
    priority += 10
  }
  if (isYearStart && !specialDates.some((d) => d.type === 'yearStart')) {
    priority += 5
  }

  return priority
}

// Enhanced border application with conflict resolution
function getBorderStyles(week: GridWeek, index: number): Record<string, string> {
  const styles: Record<string, string> = {}
  const specialDates = getSpecialDates(index)

  if (specialDates.length === 0 && !week.isHighlighted) {
    return styles
  }

  // Sort special dates by priority (highest first)
  const sortedDates = [...specialDates].sort((a, b) => b.priority - a.priority)

  if (week.isHighlighted) {
    // Highlighted weeks get outline, special dates get border
    styles.outline = `3px solid ${getThemeColorVar('highlight')}`
    styles.outlineOffset = '2px'

    if (sortedDates.length > 0) {
      const primaryDate = sortedDates[0]!
      styles.border = `2px solid ${getThemeColorVar(getBorderColor(primaryDate.type))}`

      // Add inner shadow for secondary special dates
      if (sortedDates.length > 1) {
        const secondaryDate = sortedDates[1]!
        styles.boxShadow = `inset 0 0 0 1px ${getThemeColorVar(getBorderColor(secondaryDate.type))}`
      }
    }
  } else if (sortedDates.length > 0) {
    const primaryDate = sortedDates[0]!
    styles.border = `2px solid ${getThemeColorVar(getBorderColor(primaryDate.type))}`

    // Handle multiple special dates with gradient or dual borders
    if (sortedDates.length > 1) {
      const secondaryDate = sortedDates[1]!
      if (sortedDates.length === 2) {
        // Dual border: primary on outside, secondary as inner shadow
        styles.boxShadow = `inset 0 0 0 1px ${getThemeColorVar(getBorderColor(secondaryDate.type))}`
      } else {
        // Multiple dates: create gradient border
        const colors = sortedDates
          .slice(0, 3)
          .map((date) => getThemeColorVar(getBorderColor(date.type)))
        styles.borderImage = `linear-gradient(45deg, ${colors.join(', ')}) 1`
      }
    }
  }

  return styles
}

function getBorderColor(dateType: string): string {
  switch (dateType) {
    case 'birthday':
      return 'birthday'
    case 'yearStart':
      return 'year-start'
    case 'milestone':
      return 'milestone'
    case 'decade':
      return 'decade'
    case 'quarter':
      return 'quarter'
    default:
      return 'special-date'
  }
}

// Color and theme support
const currentTheme = computed(() => userStore.currentUser?.theme || 'auto')

function getThemeColorVar(colorName: string): string {
  const theme = currentTheme.value
  if (theme === 'dark') {
    return `var(--color-${colorName}-dark, var(--color-${colorName}))`
  } else if (theme === 'light') {
    return `var(--color-${colorName}-light, var(--color-${colorName}))`
  }
  return `var(--color-${colorName})`
}

// Styling functions
function getWeekClasses(week: GridWeek, index: number) {
  const isSelectedButNotHidden =
    selectedWeekIndex.value === index && props.hideSelectedWeek !== index

  return {
    [`week-${week.type}`]: true,
    'has-notes': week.hasNotes,
    'is-birthday': week.isBirthday,
    'is-year-start': week.isYearStart,
    'is-highlighted': week.isHighlighted,
    'is-current': index === currentWeekIndex.value,
    'is-selected': isSelectedButNotHidden,
    'is-hovered': hoveredWeekIndex.value === index,
    [`border-priority-${week.borderPriority}`]: week.borderPriority > 0,
    [`theme-${currentTheme.value}`]: true,
  }
}

function getWeekStyles(week: GridWeek, index: number) {
  const styles: Record<string, string> = {}

  // Base background color based on week type
  const opacity = getWeekOpacity(week, index)
  styles.opacity = opacity.toString()

  // Apply enhanced border system
  const borderStyles = getBorderStyles(week, index)
  Object.assign(styles, borderStyles)

  // Animation and transition effects
  if (selectedWeekIndex.value === index) {
    styles.transform = 'scale(1.15)'
    styles.zIndex = '20'
  } else if (hoveredWeekIndex.value === index) {
    styles.transform = 'scale(1.1)'
    styles.zIndex = '15'
  }

  return styles
}

function getWeekOpacity(week: GridWeek, index: number): number {
  // Base opacity based on week type
  let baseOpacity = 1

  switch (week.type) {
    case WeekType.PAST:
      baseOpacity = 0.8
      break
    case WeekType.CURRENT:
      // Current week is always fully opaque
      break
    case WeekType.FUTURE:
      baseOpacity = 0.4
      break
  }

  // Increase opacity for special dates
  if (week.isSpecialDate) {
    baseOpacity = Math.min(1, baseOpacity + 0.2)
  }

  // Increase opacity for notes
  if (week.hasNotes) {
    baseOpacity = Math.min(1, baseOpacity + 0.1)
  }

  // Highlighted weeks are always fully opaque
  if (week.isHighlighted) {
    return 1
  }

  // Selected weeks have increased opacity for emphasis
  if (selectedWeekIndex.value === index) {
    return 0.0
  }

  return baseOpacity
}

// Accessibility and interaction
function getWeekAriaLabel(week: GridWeek, index: number): string {
  const weekNumber = index + 1
  const year = Math.floor(index / 52) + 1
  const weekInYear = (index % 52) + 1
  const specialDates = getSpecialDates(index)

  let label = `Week ${weekNumber}, Year ${year} of life, Week ${weekInYear} of year`

  // Add week type with more descriptive language
  switch (week.type) {
    case WeekType.PAST:
      label += ', completed week'
      break
    case WeekType.CURRENT:
      label += ', current week'
      break
    case WeekType.FUTURE:
      label += ', upcoming week'
      break
  }

  // Add special dates information
  if (specialDates.length > 0) {
    const descriptions = specialDates.map((date) => date.label).join(', ')
    label += `, Special: ${descriptions}`
  }

  // Add notes information
  if (week.hasNotes) {
    label += ', contains notes'
  }

  // Add highlighting status
  if (week.isHighlighted) {
    label += ', highlighted week'
  }

  // Add selection status
  if (selectedWeekIndex.value === index) {
    label += ', currently selected'
  }

  return label
}

// Enhanced accessibility announcements
function announceWeekChange(weekIndex: number, weekData: GridWeek) {
  if (!props.interactive) return

  const announcement = getWeekAriaLabel(weekData, weekIndex)

  // Create live region announcement
  const liveRegion = document.getElementById('week-announcements')
  if (liveRegion) {
    liveRegion.textContent = announcement

    // Clear after a delay to prepare for next announcement
    setTimeout(() => {
      liveRegion.textContent = ''
    }, 1000)
  }
}

function handleWeekClick(index: number) {
  if (!props.interactive) return

  const weekData = gridWeeks.value[index]
  if (!weekData) return

  selectedWeekIndex.value = index
  emit('weekClick', index, weekData)
}

function handleWeekFocus(index: number) {
  const weekData = gridWeeks.value[index]
  if (!weekData) return

  selectedWeekIndex.value = index
  announceWeekChange(index, weekData)
  emit('weekFocus', index, weekData)
}

function handleWeekHover(index: number) {
  const weekData = gridWeeks.value[index]
  if (!weekData) return

  hoveredWeekIndex.value = index
  emit('weekHover', index, weekData)
}

function handleWeekHoverEnd() {
  hoveredWeekIndex.value = null
  emit('weekLeave')
}

// Enhanced keyboard navigation
function handleKeyNavigation(event: KeyboardEvent) {
  if (!props.interactive || selectedWeekIndex.value === null) return

  const currentIndex = selectedWeekIndex.value
  let newIndex = currentIndex

  switch (event.key) {
    case 'ArrowRight':
    case 'l': // Vim-style navigation
      newIndex = Math.min(currentIndex + 1, totalWeeks.value - 1)
      break
    case 'ArrowLeft':
    case 'h': // Vim-style navigation
      newIndex = Math.max(currentIndex - 1, 0)
      break
    case 'ArrowDown':
    case 'j': // Vim-style navigation
      newIndex = Math.min(currentIndex + WEEKS_PER_ROW, totalWeeks.value - 1)
      break
    case 'ArrowUp':
    case 'k': // Vim-style navigation
      newIndex = Math.max(currentIndex - WEEKS_PER_ROW, 0)
      break
    case 'Home':
    case '0': // Go to first week
      newIndex = 0
      break
    case 'End':
    case '$': // Go to last week
      newIndex = totalWeeks.value - 1
      break
    case 'PageDown':
      // Jump 10 rows down
      newIndex = Math.min(currentIndex + WEEKS_PER_ROW * 10, totalWeeks.value - 1)
      break
    case 'PageUp':
      // Jump 10 rows up
      newIndex = Math.max(currentIndex - WEEKS_PER_ROW * 10, 0)
      break
    case 'c':
      // Jump to current week
      if (currentWeekIndex.value !== null) {
        newIndex = currentWeekIndex.value
      }
      break
    case 'b':
      // Jump to next birthday week
      newIndex = findNextBirthdayWeek(currentIndex)
      break
    case 'y':
      // Jump to next year start
      newIndex = findNextYearStartWeek(currentIndex)
      break
    case 'Enter':
    case ' ':
      handleWeekClick(currentIndex)
      return
    case 'Escape':
      // Clear selection
      selectedWeekIndex.value = null
      return
    default:
      return
  }

  if (newIndex !== currentIndex) {
    event.preventDefault()
    selectedWeekIndex.value = newIndex

    // Focus the new cell and announce the change
    nextTick(() => {
      const newCell = document.querySelector(`[data-week-index="${newIndex}"]`) as HTMLElement
      if (newCell) {
        newCell.focus()
        const weekData = gridWeeks.value[newIndex]
        if (weekData) {
          announceWeekChange(newIndex, weekData)
        }
      }
    })
  }
}

// Helper functions for navigation shortcuts
function findNextBirthdayWeek(fromIndex: number): number {
  for (let i = fromIndex + 1; i < totalWeeks.value; i++) {
    if (isBirthdayWeek(i)) {
      return i
    }
  }
  return fromIndex // No birthday week found, stay at current position
}

function findNextYearStartWeek(fromIndex: number): number {
  for (let i = fromIndex + 1; i < totalWeeks.value; i++) {
    if (isYearStartWeek(i)) {
      return i
    }
  }
  return fromIndex // No year start week found, stay at current position
}

function handleRetry() {
  error.value = null
  loadGridData()
}

// Data loading
async function loadGridData() {
  if (!userStore.isProfileComplete) {
    error.value = 'Complete user profile is required to display the life grid'
    return
  }

  if (!userStore.hasDateOfBirth) {
    error.value = 'Date of birth is required to display the life grid'
    return
  }

  // Additional validation for the specific data we're about to send
  const currentUser = userStore.currentUser
  if (!currentUser?.date_of_birth?.trim() || !currentUser.lifespan || currentUser.lifespan <= 0) {
    error.value = 'Valid user data is required to display the life grid'
    return
  }

  isLoading.value = true
  error.value = null

  try {
    await weekCalculationStore.calculateLifeProgress({
      date_of_birth: currentUser.date_of_birth,
      lifespan_years: userStore.userLifespan,
      timezone: userStore.userTimezone,
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load grid data'
  } finally {
    isLoading.value = false
  }
}

// Resize observer for responsive cell sizing
let resizeObserver: ResizeObserver | null = null

// Watch for user profile completion to trigger data loading
watch(
  () => userStore.isProfileComplete,
  (isComplete) => {
    if (isComplete) {
      loadGridData()
    }
  },
  { immediate: true },
)

// Lifecycle
onMounted(() => {
  // Only load data if profile is already complete
  if (userStore.isProfileComplete) {
    loadGridData()
  }

  // Set initial selection to current week
  if (currentWeekIndex.value !== null) {
    selectedWeekIndex.value = currentWeekIndex.value
  }

  // Set up resize observer for dynamic cell sizing
  if (containerRef.value && props.maxWidth === 'none') {
    resizeObserver = new ResizeObserver(() => {
      forceUpdate.value += 1
    })
    resizeObserver.observe(containerRef.value)
  }
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})

// Watch for user changes
watch(() => userStore.currentUser?.date_of_birth, loadGridData)
watch(() => userStore.userLifespan, loadGridData)
</script>

<style scoped>
.lifetime-grid-container {
  width: 100%;
  max-width: var(--max-width);
  margin: 0 auto;
  position: relative;
}

.lifetime-grid-container[style*='--max-width: none'] {
  max-width: none;
  margin: 0;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--color-border);
  border-top: 2px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-error);
}

.retry-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-button:hover {
  background: var(--color-primary-dark);
}

.lifetime-grid {
  display: grid;
  grid-template-columns: repeat(var(--weeks-per-row), var(--cell-size));
  grid-auto-rows: var(--cell-size);
  gap: 1px;
  background: var(--color-grid-background, #f5f5f5);
  padding: 1px;
  border-radius: 4px;
  outline: none;
}

.week-cell {
  background: var(--color-week-default);
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.week-cell:focus {
  outline: 2px solid var(--color-focus);
  outline-offset: 1px;
  z-index: 1;
}

/* Week type colors */
.week-past {
  background: var(--color-week-past, #8b5cf6);
}

.week-current {
  background: var(--color-week-current, #f59e0b);
  box-shadow: 0 0 0 2px var(--color-week-current-border, #d97706);
}

.week-future {
  background: var(--color-week-future, #e5e7eb);
}

/* Special date styling */
.week-cell.is-birthday {
  border: 2px solid var(--color-birthday, #ef4444) !important;
}

.week-cell.is-year-start {
  border: 2px solid var(--color-year-start, #10b981) !important;
}

/* Conflict resolution for overlapping borders */
.week-cell.is-birthday.is-year-start {
  border: 2px solid var(--color-birthday, #ef4444) !important;
  box-shadow: inset 0 0 0 1px var(--color-year-start, #10b981);
}

/* Highlighted weeks */
.week-cell.is-highlighted {
  outline: 2px solid var(--color-highlight, #3b82f6);
  outline-offset: 1px;
}

/* Hover and selection states */
.week-cell:hover:not(.is-selected) {
  transform: scale(1.1);
  z-index: 2;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.week-cell.is-selected {
  transform: scale(1.15);
  z-index: 3;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Notes indicator */
.notes-indicator {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 4px;
  height: 4px;
  background: var(--color-notes-indicator, #6366f1);
  border-radius: 50%;
  pointer-events: none;
}

/* Special marker */
.special-marker {
  position: absolute;
  bottom: 2px;
  left: 2px;
  width: 3px;
  height: 3px;
  background: var(--color-special-marker, #f59e0b);
  border-radius: 1px;
  pointer-events: none;
}

/* Grid legend */
.grid-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem;
  background: var(--color-legend-background, #f9fafb);
  border-radius: 4px;
  font-size: 0.875rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 2px;
  border: 1px solid var(--color-border, #d1d5db);
}

.legend-color.past-week {
  background: var(--color-week-past, #8b5cf6);
}

.legend-color.current-week {
  background: var(--color-week-current, #f59e0b);
}

.legend-color.future-week {
  background: var(--color-week-future, #e5e7eb);
}

.legend-color.birthday-marker {
  background: var(--color-birthday, #ef4444);
}

.legend-color.year-start-marker {
  background: var(--color-year-start, #10b981);
}

/* Responsive design */
@media (max-width: 768px) {
  /* For fixed max-width grids, reduce cell size */
  .lifetime-grid-container:not([style*='--max-width: none']) .lifetime-grid {
    grid-template-columns: repeat(var(--weeks-per-row), calc(var(--cell-size) * 0.8));
    grid-auto-rows: calc(var(--cell-size) * 0.8);
  }
}

@media (max-width: 480px) {
  .lifetime-grid-container:not([style*='--max-width: none']) .lifetime-grid {
    grid-template-columns: repeat(var(--weeks-per-row), calc(var(--cell-size) * 0.6));
    grid-auto-rows: calc(var(--cell-size) * 0.7);
  }
}

/* Loading state */
.is-loading .lifetime-grid {
  opacity: 0.5;
  pointer-events: none;
}

/* CSS custom properties for theming */
:root {
  /* Week state colors */
  --color-week-past: #8b5cf6;
  --color-week-current: #f59e0b;
  --color-week-current-border: #d97706;
  --color-week-future: #e5e7eb;

  /* Special date colors */
  --color-birthday: #ef4444;
  --color-year-start: #10b981;
  --color-milestone: #ec4899;
  --color-decade: #8b5cf6;
  --color-quarter: #6b7280;
  --color-special-date: #f97316;

  /* Interactive colors */
  --color-highlight: #3b82f6;
  --color-focus: #2563eb;
  --color-selection: #1d4ed8;
  --color-hover: #3730a3;

  /* UI colors */
  --color-notes-indicator: #6366f1;
  --color-special-marker: #f59e0b;
  --color-grid-background: #f5f5f5;
  --color-legend-background: #f9fafb;
  --color-border: #d1d5db;
  --color-primary: #3b82f6;
  --color-primary-dark: #2563eb;
  --color-error: #ef4444;
  --color-text: #1f2937;
  --color-text-muted: #6b7280;
}

/* Light theme explicit overrides */
[data-theme='light'] {
  --color-week-past: #8b5cf6;
  --color-week-future: #e5e7eb;
  --color-grid-background: #f5f5f5;
  --color-legend-background: #f9fafb;
  --color-text: #1f2937;
}

/* Dark theme support */
[data-theme='dark'] {
  /* Week state colors - dark theme */
  --color-week-past: #7c3aed;
  --color-week-future: #374151;

  /* Special date colors - dark theme */
  --color-birthday: #f87171;
  --color-year-start: #34d399;
  --color-milestone: #f472b6;
  --color-decade: #a78bfa;
  --color-quarter: #9ca3af;

  /* Interactive colors - dark theme */
  --color-highlight: #60a5fa;
  --color-focus: #3b82f6;
  --color-selection: #2563eb;
  --color-hover: #6366f1;

  /* UI colors - dark theme */
  --color-notes-indicator: #818cf8;
  --color-grid-background: #1f2937;
  --color-legend-background: #374151;
  --color-border: #4b5563;
  --color-text: #f9fafb;
  --color-text-muted: #d1d5db;
}

@media (prefers-color-scheme: dark) {
  :root {
    /* Week state colors - dark theme */
    --color-week-past: #7c3aed;
    --color-week-future: #374151;

    /* Special date colors - dark theme */
    --color-birthday: #f87171;
    --color-year-start: #34d399;
    --color-milestone: #f472b6;
    --color-decade: #a78bfa;
    --color-quarter: #9ca3af;

    /* Interactive colors - dark theme */
    --color-highlight: #60a5fa;
    --color-focus: #3b82f6;
    --color-selection: #2563eb;
    --color-hover: #6366f1;

    /* UI colors - dark theme */
    --color-notes-indicator: #818cf8;
    --color-grid-background: #1f2937;
    --color-legend-background: #374151;
    --color-border: #4b5563;
    --color-text: #f9fafb;
    --color-text-muted: #d1d5db;
  }
}
</style>
