<template>
  <section
    class="lifetime-grid-container"
    :class="{ 'is-loading': isLoading }"
    :aria-label="`Life visualization grid for ${totalWeeks} weeks`"
    aria-describedby="grid-description"
  >
    <!-- Screen reader description -->
    <div id="grid-description" class="sr-only">
      A virtual scrollable representation of your lifetime in weeks. Each cell represents one week.
      Past weeks are shown in darker colors, current week is highlighted, and future weeks are in
      lighter colors. Use arrow keys to navigate the grid, Enter or Space to select a week, Home to
      go to first week, End to go to last week.
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

    <!-- Performance metrics (debug mode) -->
    <div v-if="showPerformanceMetrics" class="performance-metrics">
      <h3>Performance Metrics</h3>
      <div class="metrics-grid">
        <div>Visible weeks: {{ virtualScrolling.visibleItems.value.length }}</div>
        <div>Cache hits: {{ lazyLoading.metrics.value.cacheHits }}</div>
        <div>Cache hit ratio: {{ (lazyLoading.cacheHitRatio.value * 100).toFixed(1) }}%</div>
        <div>Scroll position: {{ Math.round(virtualScrolling.scrollTop.value) }}px</div>
        <div>
          Total rows rendered:
          {{ virtualScrolling.endRow.value - virtualScrolling.startRow.value + 1 }}
        </div>
      </div>
    </div>

    <!-- Virtual Grid container -->
    <div
      v-if="!isLoading && !error && totalWeeks > 0"
      ref="gridContainerRef"
      class="virtual-grid-container"
      :style="containerStyles"
      role="application"
      aria-label="Interactive virtual lifetime grid - use arrow keys to navigate"
      @keydown="handleKeyNavigation"
      tabindex="0"
    >
      <!-- Virtual scrollable content with total height -->
      <div class="virtual-content" :style="contentStyles">
        <!-- Visible grid rows -->
        <div class="virtual-grid" :style="gridStyles">
          <div
            v-for="weekIndex in virtualScrolling.visibleItems.value"
            :key="`week-${weekIndex}`"
            class="week-cell"
            :class="getWeekClasses(weekIndex)"
            :style="getWeekStyles(weekIndex)"
            :data-week-index="weekIndex"
            :aria-label="getWeekAriaLabel(weekIndex)"
            :aria-selected="selectedWeekIndex === weekIndex"
            :tabindex="selectedWeekIndex === weekIndex ? 0 : -1"
            @click="handleWeekClick(weekIndex)"
            @focus="handleWeekFocus(weekIndex)"
            @mouseenter="handleWeekHover(weekIndex)"
            @mouseleave="handleWeekHoverEnd"
          >
            <!-- Week content indicators -->
            <div
              v-if="getWeekData(weekIndex)?.hasNotes"
              class="notes-indicator"
              aria-hidden="true"
            ></div>
            <div
              v-if="isSpecialWeek(weekIndex)"
              class="special-marker"
              :title="getSpecialDateType(weekIndex)"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Grid controls -->
    <div class="grid-controls">
      <button @click="scrollToCurrentWeek" class="control-button">Go to Current Week</button>
      <button @click="scrollToTop" class="control-button">Go to Start</button>
      <button @click="scrollToBottom" class="control-button">Go to End</button>
      <button @click="togglePerformanceMetrics" class="control-button" v-if="isDevelopment">
        {{ showPerformanceMetrics ? 'Hide' : 'Show' }} Metrics
      </button>
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
import { ref, computed, onMounted, nextTick, watch, onBeforeUnmount } from 'vue'
import { useWeekCalculationStore } from '@/stores/week-calculation'
import { useUserStore } from '@/stores/user'
import { WeekType } from '@/types'
import { useGridVirtualScrolling } from '@/composables/useVirtualScrolling'
import { useWeekDataLazyLoading } from '@/composables/useLazyLoading'
import { useGridScrollPersistence } from '@/composables/useScrollPersistence'

// Props
interface Props {
  highlightedWeeks?: number[]
  showNotes?: boolean
  interactive?: boolean
  maxWidth?: string
  cellSize?: number
  containerHeight?: number
  showPerformanceMetrics?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  highlightedWeeks: () => [],
  showNotes: true,
  interactive: true,
  maxWidth: '100%',
  cellSize: 16,
  containerHeight: 600,
  showPerformanceMetrics: false,
})

// Emits
const emit = defineEmits<{
  weekClick: [weekIndex: number]
  weekHover: [weekIndex: number]
  weekLeave: []
  weekFocus: [weekIndex: number]
  scrollPositionChange: [position: { top: number; left: number }]
}>()

// Constants
const WEEKS_PER_ROW = 52
const CELL_GAP = 1

// Environment detection
const isDevelopment = import.meta.env.MODE === 'development'

// Stores
const weekCalculationStore = useWeekCalculationStore()
const userStore = useUserStore()

// Reactive state
const selectedWeekIndex = ref<number | null>(null)
const hoveredWeekIndex = ref<number | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)
const showPerformanceMetrics = ref(props.showPerformanceMetrics)

// Template refs
const gridContainerRef = ref<HTMLElement>()

// Computed properties
const totalWeeks = computed(() => weekCalculationStore.totalLifetimeWeeks || 0)
const currentWeekIndex = computed(() => weekCalculationStore.currentWeekIndex || 0)

// Responsive design
const responsiveConfig = computed(() => {
  // This would typically use a composable or media queries
  if (window.innerWidth < 480) {
    return { columns: 13, cellSize: props.cellSize * 0.7 }
  } else if (window.innerWidth < 768) {
    return { columns: 26, cellSize: props.cellSize * 0.8 }
  }
  return { columns: WEEKS_PER_ROW, cellSize: props.cellSize }
})

// Virtual scrolling setup
const virtualScrolling = useGridVirtualScrolling({
  totalItems: totalWeeks.value,
  itemHeight: responsiveConfig.value.cellSize + CELL_GAP,
  columns: responsiveConfig.value.columns,
  cellWidth: responsiveConfig.value.cellSize,
  containerHeight: props.containerHeight,
  gap: CELL_GAP,
  overscan: 2,
})

// Lazy loading setup for week data
const lazyLoading = useWeekDataLazyLoading({
  loadWeekData: async (startWeek: number, endWeek: number) => {
    // Simulate loading week data from API
    const weekData = []
    for (let i = startWeek; i <= endWeek; i++) {
      weekData.push({
        weekIndex: i,
        hasNotes: false, // This would come from the notes API
        noteCount: 0,
        specialDates: getSpecialDatesForWeek(i),
      })
    }
    return weekData
  },
  prefetchCount: 20,
  cacheSize: Math.min(2000, totalWeeks.value),
  debug: isDevelopment,
})

// Scroll persistence
const scrollPersistence = useGridScrollPersistence({
  key: `lifetime-grid-${userStore.currentUser?.id || 'default'}`,
  storage: 'localStorage',
  selectedIndex: selectedWeekIndex.value || undefined,
  totalItems: totalWeeks.value,
  debug: isDevelopment,
})

// Connect the scroll container
watch(gridContainerRef, (container) => {
  if (container) {
    virtualScrolling.containerRef.value = container
    scrollPersistence.containerRef.value = container
  }
})

// Grid styling
const containerStyles = computed(() => ({
  '--cell-size': `${responsiveConfig.value.cellSize}px`,
  '--cell-gap': `${CELL_GAP}px`,
  '--columns': responsiveConfig.value.columns,
  '--max-width': props.maxWidth,
  height: `${props.containerHeight}px`,
}))

const contentStyles = computed(() => ({
  height: `${virtualScrolling.totalHeight}px`,
}))

const gridStyles = computed(() => ({
  transform: `translateY(${virtualScrolling.offsetY}px)`,
  display: 'grid',
  gridTemplateColumns: `repeat(${responsiveConfig.value.columns}, ${responsiveConfig.value.cellSize}px)`,
  gap: `${CELL_GAP}px`,
  padding: `${CELL_GAP}px`,
}))

// Week data access

const getWeekData = (weekIndex: number) => {
  // Access cache directly for synchronous access in templates
  const cache = lazyLoading.cache.value as Map<number, any>
  const entry = cache.get(weekIndex)
  return entry?.data || null
}

// Week classification
const getWeekType = (weekIndex: number): WeekType => {
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

const isSpecialWeek = (weekIndex: number): boolean => {
  return isBirthdayWeek(weekIndex) || isYearStartWeek(weekIndex)
}

const isBirthdayWeek = (weekIndex: number): boolean => {
  if (!userStore.currentUser?.date_of_birth) return false

  // Simplified calculation - in real implementation, this would be more precise
  const weekInYear = weekIndex % 52
  const birthDate = new Date(userStore.currentUser.date_of_birth)
  const birthWeekInYear = Math.floor(
    (birthDate.getTime() - new Date(birthDate.getFullYear(), 0, 1).getTime()) /
      (7 * 24 * 60 * 60 * 1000),
  )

  return weekInYear === birthWeekInYear
}

const isYearStartWeek = (weekIndex: number): boolean => {
  const weekInYear = weekIndex % 52
  return weekInYear === 0 // Only the first week of the year
}

const getSpecialDatesForWeek = (weekIndex: number): string[] => {
  const dates: string[] = []
  if (isBirthdayWeek(weekIndex)) dates.push('birthday')
  if (isYearStartWeek(weekIndex)) dates.push('year-start')
  return dates
}

const getSpecialDateType = (weekIndex: number): string => {
  const dates = getSpecialDatesForWeek(weekIndex)
  return dates.join(', ')
}

// Styling functions
const getWeekClasses = (weekIndex: number) => {
  const weekType = getWeekType(weekIndex)
  const weekData = getWeekData(weekIndex)

  return {
    [`week-${weekType}`]: true,
    'has-notes': weekData?.hasNotes || false,
    'is-birthday': isBirthdayWeek(weekIndex),
    'is-year-start': isYearStartWeek(weekIndex),
    'is-highlighted': props.highlightedWeeks.includes(weekIndex),
    'is-current': weekIndex === currentWeekIndex.value,
    'is-selected': selectedWeekIndex.value === weekIndex,
    'is-hovered': hoveredWeekIndex.value === weekIndex,
  }
}

const getWeekStyles = (weekIndex: number) => {
  const styles: Record<string, string> = {}

  // Position in virtual grid is handled by CSS Grid
  // Add any specific styling based on week properties

  if (selectedWeekIndex.value === weekIndex) {
    styles.transform = 'scale(1.15)'
    styles.zIndex = '20'
  } else if (hoveredWeekIndex.value === weekIndex) {
    styles.transform = 'scale(1.1)'
    styles.zIndex = '15'
  }

  return styles
}

// Accessibility
const getWeekAriaLabel = (weekIndex: number): string => {
  const weekNumber = weekIndex + 1
  const year = Math.floor(weekIndex / 52) + 1
  const weekInYear = (weekIndex % 52) + 1
  const weekType = getWeekType(weekIndex)

  let label = `Week ${weekNumber}, Year ${year} of life, Week ${weekInYear} of year`

  switch (weekType) {
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

  const specialDates = getSpecialDatesForWeek(weekIndex)
  if (specialDates.length > 0) {
    label += `, Special: ${specialDates.join(', ')}`
  }

  const weekData = getWeekData(weekIndex)
  if (weekData?.hasNotes) {
    label += ', contains notes'
  }

  if (props.highlightedWeeks.includes(weekIndex)) {
    label += ', highlighted week'
  }

  if (selectedWeekIndex.value === weekIndex) {
    label += ', currently selected'
  }

  return label
}

// Event handlers
const handleWeekClick = (weekIndex: number) => {
  if (!props.interactive) return

  selectedWeekIndex.value = weekIndex
  emit('weekClick', weekIndex)
}

const handleWeekFocus = (weekIndex: number) => {
  if (!props.interactive) return

  selectedWeekIndex.value = weekIndex
  announceWeekChange(weekIndex)
  emit('weekFocus', weekIndex)
}

const handleWeekHover = (weekIndex: number) => {
  hoveredWeekIndex.value = weekIndex
  emit('weekHover', weekIndex)
}

const handleWeekHoverEnd = () => {
  hoveredWeekIndex.value = null
  emit('weekLeave')
}

const announceWeekChange = (weekIndex: number) => {
  if (!props.interactive) return

  const announcement = getWeekAriaLabel(weekIndex)
  const liveRegion = document.getElementById('week-announcements')
  if (liveRegion) {
    liveRegion.textContent = announcement
    setTimeout(() => {
      liveRegion.textContent = ''
    }, 1000)
  }
}

// Navigation methods
const scrollToCurrentWeek = () => {
  if (currentWeekIndex.value !== null) {
    virtualScrolling.scrollToIndex(currentWeekIndex.value)
    selectedWeekIndex.value = currentWeekIndex.value
  }
}

const scrollToTop = () => {
  virtualScrolling.scrollToIndex(0)
  selectedWeekIndex.value = 0
}

const scrollToBottom = () => {
  const lastIndex = totalWeeks.value - 1
  virtualScrolling.scrollToIndex(lastIndex)
  selectedWeekIndex.value = lastIndex
}

const togglePerformanceMetrics = () => {
  showPerformanceMetrics.value = !showPerformanceMetrics.value
}

// Keyboard navigation
const handleKeyNavigation = (event: KeyboardEvent) => {
  if (!props.interactive || selectedWeekIndex.value === null) return

  const currentIndex = selectedWeekIndex.value
  let newIndex = currentIndex
  const columns = responsiveConfig.value.columns

  switch (event.key) {
    case 'ArrowRight':
    case 'l':
      newIndex = Math.min(currentIndex + 1, totalWeeks.value - 1)
      break
    case 'ArrowLeft':
    case 'h':
      newIndex = Math.max(currentIndex - 1, 0)
      break
    case 'ArrowDown':
    case 'j':
      newIndex = Math.min(currentIndex + columns, totalWeeks.value - 1)
      break
    case 'ArrowUp':
    case 'k':
      newIndex = Math.max(currentIndex - columns, 0)
      break
    case 'Home':
    case '0':
      newIndex = 0
      break
    case 'End':
    case '$':
      newIndex = totalWeeks.value - 1
      break
    case 'PageDown':
      newIndex = Math.min(currentIndex + columns * 10, totalWeeks.value - 1)
      break
    case 'PageUp':
      newIndex = Math.max(currentIndex - columns * 10, 0)
      break
    case 'c':
      if (currentWeekIndex.value !== null) {
        newIndex = currentWeekIndex.value
      }
      break
    case 'Enter':
    case ' ':
      handleWeekClick(currentIndex)
      return
    case 'Escape':
      selectedWeekIndex.value = null
      return
    default:
      return
  }

  if (newIndex !== currentIndex) {
    event.preventDefault()
    selectedWeekIndex.value = newIndex
    virtualScrolling.ensureItemVisible(newIndex)

    nextTick(() => {
      const newCell = document.querySelector(`[data-week-index="${newIndex}"]`) as HTMLElement
      if (newCell) {
        newCell.focus()
        announceWeekChange(newIndex)
      }
    })
  }
}

const handleRetry = () => {
  error.value = null
  loadGridData()
}

// Data loading
const loadGridData = async () => {
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

// Watch for virtual scrolling changes and load data
watch(
  () => virtualScrolling.visibleItems.value,
  async (visibleItems) => {
    if (visibleItems.length > 0) {
      await lazyLoading.loadVisibleWeeks(visibleItems)
    }
  },
  { immediate: true },
)

// Watch for scroll position changes
watch(
  () => virtualScrolling.scrollTop.value,
  (scrollTop) => {
    emit('scrollPositionChange', {
      top: scrollTop,
      left: 0,
    })
  },
)

// Lifecycle
onMounted(async () => {
  await loadGridData()

  // Set initial selection to current week
  if (currentWeekIndex.value !== null) {
    selectedWeekIndex.value = currentWeekIndex.value
    virtualScrolling.ensureItemVisible(currentWeekIndex.value)
  }
})

// Update virtual scrolling when total weeks change
watch(totalWeeks, (newTotal) => {
  virtualScrolling.updateTotalItems(newTotal)
  lazyLoading.updateCacheSize(Math.min(2000, newTotal))
})

// Responsive updates
const updateResponsiveConfig = () => {
  const config = responsiveConfig.value
  virtualScrolling.updateColumns(config.columns)
  virtualScrolling.updateItemHeight(config.cellSize + CELL_GAP)
  virtualScrolling.updateCellWidth(config.cellSize)
}

// Watch for window resize
let resizeTimeout: number
const handleResize = () => {
  clearTimeout(resizeTimeout)
  resizeTimeout = window.setTimeout(updateResponsiveConfig, 100)
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  clearTimeout(resizeTimeout)
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
  font-family:
    system-ui,
    -apple-system,
    sans-serif;
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
  border: 2px solid var(--color-border, #e5e7eb);
  border-top: 2px solid var(--color-primary, #3b82f6);
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
  color: var(--color-error, #ef4444);
}

.retry-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: var(--color-primary, #3b82f6);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.retry-button:hover {
  background: var(--color-primary-dark, #2563eb);
}

.performance-metrics {
  background: var(--color-bg-secondary, #f8fafc);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  font-family: monospace;
  font-size: 0.75rem;
}

.performance-metrics h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
}

.virtual-grid-container {
  width: 100%;
  overflow: auto;
  position: relative;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
  background: var(--color-bg, #ffffff);
  outline: none;
}

.virtual-grid-container:focus {
  outline: 2px solid var(--color-focus, #3b82f6);
  outline-offset: 2px;
}

.virtual-content {
  position: relative;
  width: 100%;
}

.virtual-grid {
  position: absolute;
  width: 100%;
}

.week-cell {
  background: var(--color-week-default, #f3f4f6);
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.15s ease;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--cell-size);
  height: var(--cell-size);
}

.week-cell:hover {
  transform: scale(1.1);
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.week-cell:focus {
  outline: 2px solid var(--color-focus, #3b82f6);
  outline-offset: 1px;
  z-index: 15;
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

.week-cell.is-birthday.is-year-start {
  border: 2px solid var(--color-birthday, #ef4444) !important;
  box-shadow: inset 0 0 0 1px var(--color-year-start, #10b981);
}

.week-cell.is-highlighted {
  outline: 2px solid var(--color-highlight, #3b82f6);
  outline-offset: 1px;
}

.week-cell.is-selected {
  transform: scale(1.15);
  z-index: 20;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Content indicators */
.notes-indicator {
  position: absolute;
  top: 1px;
  right: 1px;
  width: 3px;
  height: 3px;
  background: var(--color-notes-indicator, #6366f1);
  border-radius: 50%;
}

.special-marker {
  position: absolute;
  bottom: 1px;
  left: 1px;
  width: 2px;
  height: 2px;
  background: var(--color-special-marker, #f59e0b);
  border-radius: 1px;
}

/* Grid controls */
.grid-controls {
  display: flex;
  gap: 0.5rem;
  margin: 1rem 0;
  flex-wrap: wrap;
}

.control-button {
  padding: 0.5rem 1rem;
  background: var(--color-bg-secondary, #f8fafc);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.15s ease;
}

.control-button:hover {
  background: var(--color-bg-secondary-hover, #e2e8f0);
  border-color: var(--color-border-hover, #cbd5e1);
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

/* Loading state */
.is-loading .virtual-grid-container {
  opacity: 0.5;
  pointer-events: none;
}

/* CSS custom properties for theming */
:root {
  --color-week-past: #8b5cf6;
  --color-week-current: #f59e0b;
  --color-week-current-border: #d97706;
  --color-week-future: #e5e7eb;
  --color-birthday: #ef4444;
  --color-year-start: #10b981;
  --color-highlight: #3b82f6;
  --color-focus: #2563eb;
  --color-notes-indicator: #6366f1;
  --color-special-marker: #f59e0b;
  --color-bg: #ffffff;
  --color-bg-secondary: #f8fafc;
  --color-bg-secondary-hover: #e2e8f0;
  --color-border: #e5e7eb;
  --color-border-hover: #cbd5e1;
  --color-legend-background: #f9fafb;
  --color-primary: #3b82f6;
  --color-primary-dark: #2563eb;
  --color-error: #ef4444;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .grid-controls {
    justify-content: center;
  }

  .control-button {
    font-size: 0.8rem;
    padding: 0.4rem 0.8rem;
  }

  .performance-metrics {
    font-size: 0.7rem;
  }
}

@media (max-width: 480px) {
  .lifetime-grid-container {
    padding: 0.5rem;
  }

  .grid-legend {
    flex-direction: column;
    gap: 0.5rem;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
