/**
 * Responsive design composable for the virtualized grid
 * Handles dynamic sizing and layout adjustments based on viewport
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'

export interface ResponsiveBreakpoints {
  xs: number // Extra small devices
  sm: number // Small devices
  md: number // Medium devices
  lg: number // Large devices
  xl: number // Extra large devices
}

export interface ResponsiveGridConfig {
  columns: number
  cellSize: number
  gap: number
  containerHeight: number
}

export interface ResponsiveOptions {
  baseConfig: ResponsiveGridConfig
  breakpoints?: Partial<ResponsiveBreakpoints>
  debounceDelay?: number
  debug?: boolean
}

const DEFAULT_BREAKPOINTS: ResponsiveBreakpoints = {
  xs: 0,
  sm: 480,
  md: 768,
  lg: 1024,
  xl: 1200,
}

export function useResponsiveGrid(options: ResponsiveOptions) {
  const breakpoints = { ...DEFAULT_BREAKPOINTS, ...options.breakpoints }
  const debounceDelay = options.debounceDelay || 100
  const debug = options.debug || false

  // Current window dimensions
  const windowWidth = ref(0)
  const windowHeight = ref(0)

  // Debounce timeout
  let resizeTimeout: number

  // Current breakpoint
  const currentBreakpoint = computed(() => {
    const width = windowWidth.value

    if (width >= breakpoints.xl) return 'xl'
    if (width >= breakpoints.lg) return 'lg'
    if (width >= breakpoints.md) return 'md'
    if (width >= breakpoints.sm) return 'sm'
    return 'xs'
  })

  // Responsive grid configuration
  const gridConfig = computed((): ResponsiveGridConfig => {
    const breakpoint = currentBreakpoint.value
    const baseConfig = options.baseConfig

    switch (breakpoint) {
      case 'xs':
        return {
          columns: Math.max(10, Math.min(15, Math.floor(windowWidth.value / 25))),
          cellSize: Math.max(8, Math.min(12, baseConfig.cellSize * 0.6)),
          gap: 1,
          containerHeight: Math.min(400, windowHeight.value * 0.6),
        }

      case 'sm':
        return {
          columns: Math.max(20, Math.min(30, Math.floor(windowWidth.value / 20))),
          cellSize: Math.max(10, Math.min(14, baseConfig.cellSize * 0.75)),
          gap: 1,
          containerHeight: Math.min(500, windowHeight.value * 0.7),
        }

      case 'md':
        return {
          columns: Math.max(30, Math.min(42, Math.floor(windowWidth.value / 18))),
          cellSize: Math.max(12, Math.min(16, baseConfig.cellSize * 0.9)),
          gap: 1,
          containerHeight: Math.min(600, windowHeight.value * 0.75),
        }

      case 'lg':
        return {
          columns: Math.min(52, Math.floor(windowWidth.value / 16)),
          cellSize: baseConfig.cellSize,
          gap: baseConfig.gap,
          containerHeight: Math.min(700, windowHeight.value * 0.8),
        }

      case 'xl':
      default:
        return {
          columns: 52, // Full year view
          cellSize: Math.max(baseConfig.cellSize, Math.min(20, Math.floor(windowWidth.value / 60))),
          gap: baseConfig.gap,
          containerHeight: Math.min(800, windowHeight.value * 0.85),
        }
    }
  })

  // Grid dimensions
  const gridWidth = computed(
    () =>
      gridConfig.value.columns * gridConfig.value.cellSize +
      (gridConfig.value.columns - 1) * gridConfig.value.gap,
  )

  const maxGridWidth = computed(
    () => Math.min(gridWidth.value, windowWidth.value - 40), // 40px for padding
  )

  // Check if current configuration fits in viewport
  const fitsInViewport = computed(() => gridWidth.value <= windowWidth.value - 40)

  // Responsive utilities
  const isMobile = computed(
    () => currentBreakpoint.value === 'xs' || currentBreakpoint.value === 'sm',
  )

  const isTablet = computed(() => currentBreakpoint.value === 'md')

  const isDesktop = computed(
    () => currentBreakpoint.value === 'lg' || currentBreakpoint.value === 'xl',
  )

  // Calculate optimal cell size for current viewport
  const calculateOptimalCellSize = (targetColumns: number = 52): number => {
    const availableWidth = windowWidth.value - 40 // Account for padding
    const gapSpace = (targetColumns - 1) * gridConfig.value.gap
    const cellSpace = availableWidth - gapSpace
    return Math.max(8, Math.floor(cellSpace / targetColumns))
  }

  // Calculate optimal number of columns for current viewport
  const calculateOptimalColumns = (
    targetCellSize: number = options.baseConfig.cellSize,
  ): number => {
    const availableWidth = windowWidth.value - 40
    const cellWithGap = targetCellSize + gridConfig.value.gap
    return Math.max(10, Math.floor(availableWidth / cellWithGap))
  }

  // Update window dimensions
  const updateDimensions = () => {
    windowWidth.value = window.innerWidth
    windowHeight.value = window.innerHeight

    if (debug) {
      console.log('Responsive grid dimensions updated:', {
        windowWidth: windowWidth.value,
        windowHeight: windowHeight.value,
        breakpoint: currentBreakpoint.value,
        gridConfig: gridConfig.value,
      })
    }
  }

  // Debounced resize handler
  const handleResize = () => {
    clearTimeout(resizeTimeout)
    resizeTimeout = window.setTimeout(() => {
      updateDimensions()
    }, debounceDelay)
  }

  // Get CSS custom properties for the current configuration
  const getCSSProperties = () => ({
    '--grid-columns': gridConfig.value.columns.toString(),
    '--grid-cell-size': `${gridConfig.value.cellSize}px`,
    '--grid-gap': `${gridConfig.value.gap}px`,
    '--grid-width': `${gridWidth.value}px`,
    '--grid-max-width': `${maxGridWidth.value}px`,
    '--grid-container-height': `${gridConfig.value.containerHeight}px`,
    '--grid-breakpoint': currentBreakpoint.value,
  })

  // Media query helpers
  const createMediaQuery = (breakpoint: keyof ResponsiveBreakpoints) => {
    return window.matchMedia(`(min-width: ${breakpoints[breakpoint]}px)`)
  }

  const matchesMediaQuery = (breakpoint: keyof ResponsiveBreakpoints) => {
    return createMediaQuery(breakpoint).matches
  }

  // Orientation handling
  const isLandscape = computed(() => windowWidth.value > windowHeight.value)
  const isPortrait = computed(() => windowWidth.value <= windowHeight.value)

  // Device type detection
  const isTouchDevice = computed(() => 'ontouchstart' in window || navigator.maxTouchPoints > 0)

  // Performance-oriented configurations
  const getPerformanceConfig = () => {
    const config = gridConfig.value

    // Reduce complexity on mobile devices
    if (isMobile.value) {
      return {
        ...config,
        overscan: 1, // Reduce overscan on mobile
        prefetchCount: 5, // Reduce prefetch on mobile
        cacheSize: 500, // Smaller cache on mobile
      }
    }

    // Standard config for desktop
    return {
      ...config,
      overscan: 3,
      prefetchCount: 15,
      cacheSize: 1500,
    }
  }

  // Initialize
  const initialize = () => {
    updateDimensions()
    window.addEventListener('resize', handleResize)
    window.addEventListener('orientationchange', handleResize)
  }

  // Cleanup
  const cleanup = () => {
    window.removeEventListener('resize', handleResize)
    window.removeEventListener('orientationchange', handleResize)
    clearTimeout(resizeTimeout)
  }

  // Lifecycle
  onMounted(() => {
    initialize()
  })

  onUnmounted(() => {
    cleanup()
  })

  return {
    // Dimensions
    windowWidth,
    windowHeight,

    // Breakpoint information
    currentBreakpoint,

    // Grid configuration
    gridConfig,
    gridWidth,
    maxGridWidth,
    fitsInViewport,

    // Device type helpers
    isMobile,
    isTablet,
    isDesktop,
    isTouchDevice,
    isLandscape,
    isPortrait,

    // Utility methods
    calculateOptimalCellSize,
    calculateOptimalColumns,
    getCSSProperties,
    getPerformanceConfig,
    matchesMediaQuery,
    createMediaQuery,

    // Manual control
    updateDimensions,
  }
}

// Specialized hook for lifetime grid responsive behavior
export function useLifetimeGridResponsive(baseCellSize: number = 12) {
  const responsiveGrid = useResponsiveGrid({
    baseConfig: {
      columns: 52,
      cellSize: baseCellSize,
      gap: 1,
      containerHeight: 600,
    },
    debounceDelay: 150,
    debug: false,
  })

  // Lifetime-specific responsive rules
  const lifetimeGridConfig = computed(() => {
    const base = responsiveGrid.gridConfig.value
    const breakpoint = responsiveGrid.currentBreakpoint.value

    // Lifetime grid specific adjustments
    switch (breakpoint) {
      case 'xs':
        // On very small screens, show 2-3 months per row
        return {
          ...base,
          columns: Math.min(13, base.columns), // ~1 quarter
          cellSize: Math.max(base.cellSize, 10),
          containerHeight: Math.min(300, base.containerHeight),
        }

      case 'sm':
        // On small screens, show 6 months per row
        return {
          ...base,
          columns: Math.min(26, base.columns), // ~6 months
          cellSize: Math.max(base.cellSize, 12),
        }

      default:
        return base
    }
  })

  // Years displayed per row
  const yearsPerRow = computed(() => lifetimeGridConfig.value.columns / 52)

  // Weeks visible in viewport
  const weeksInViewport = computed(() => {
    const config = lifetimeGridConfig.value
    const rowsInViewport = Math.floor(config.containerHeight / (config.cellSize + config.gap))
    return rowsInViewport * config.columns
  })

  return {
    ...responsiveGrid,

    // Override with lifetime-specific config
    gridConfig: lifetimeGridConfig,

    // Lifetime-specific computed values
    yearsPerRow,
    weeksInViewport,
  }
}
