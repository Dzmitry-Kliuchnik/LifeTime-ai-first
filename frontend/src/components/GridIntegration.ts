/**
 * Integration utility for migrating from regular LifetimeGrid to VirtualizedLifetimeGrid
 * Provides backward compatibility and feature flags
 */
import { computed, ref } from 'vue'
import type { Component } from 'vue'
import LifetimeGrid from './LifetimeGrid.vue'
import VirtualizedLifetimeGrid from './VirtualizedLifetimeGrid.vue'

// Extend Navigator interface for performance detection
declare global {
  interface Navigator {
    deviceMemory?: number
    connection?: {
      effectiveType?: string
    }
  }
}

export interface GridIntegrationOptions {
  /** Enable virtualization (can be controlled by feature flag) */
  useVirtualization?: boolean
  /** Minimum number of weeks to enable virtualization */
  virtualizationThreshold?: number
  /** Performance mode: 'auto', 'performance', 'compatibility' */
  performanceMode?: 'auto' | 'performance' | 'compatibility'
  /** Enable debug mode */
  debug?: boolean
}

export interface GridFeatures {
  virtualScrolling: boolean
  lazyLoading: boolean
  scrollPersistence: boolean
  responsiveDesign: boolean
  performanceMetrics: boolean
}

/**
 * Composable for managing grid component selection and feature flags
 */
export function useGridIntegration(totalWeeks: number, options: GridIntegrationOptions = {}) {
  const {
    useVirtualization = true,
    virtualizationThreshold = 1000,
    performanceMode = 'auto',
    debug = false,
  } = options

  // Performance detection
  const isLowEndDevice = computed(() => {
    // Simple heuristic for low-end device detection
    if (typeof navigator !== 'undefined') {
      return (
        navigator.hardwareConcurrency <= 2 ||
        (navigator.deviceMemory && navigator.deviceMemory <= 2) ||
        navigator.connection?.effectiveType === 'slow-2g' ||
        navigator.connection?.effectiveType === '2g'
      )
    }
    return false
  })

  // Auto-detect if virtualization should be used
  const shouldUseVirtualization = computed(() => {
    if (performanceMode === 'compatibility') return false
    if (performanceMode === 'performance') return true

    // Auto mode: use virtualization based on various factors
    if (!useVirtualization) return false
    if (totalWeeks < virtualizationThreshold) return false
    if (isLowEndDevice.value && totalWeeks < virtualizationThreshold * 2) return false

    return true
  })

  // Grid component selection
  const GridComponent = computed((): Component => {
    return shouldUseVirtualization.value ? VirtualizedLifetimeGrid : LifetimeGrid
  })

  // Feature availability
  const features = computed(
    (): GridFeatures => ({
      virtualScrolling: shouldUseVirtualization.value,
      lazyLoading: shouldUseVirtualization.value,
      scrollPersistence: shouldUseVirtualization.value,
      responsiveDesign: true, // Both components support this
      performanceMetrics: shouldUseVirtualization.value && debug,
    }),
  )

  // Component props mapping
  const getComponentProps = (originalProps: Record<string, any>) => {
    const baseProps = { ...originalProps }

    if (shouldUseVirtualization.value) {
      // Add virtualization-specific props
      return {
        ...baseProps,
        showPerformanceMetrics: debug && features.value.performanceMetrics,
        containerHeight: baseProps.containerHeight || 600,
      }
    }

    // Return original props for regular grid
    return baseProps
  }

  // Migration helper
  const migrationInfo = computed(() => ({
    isVirtualized: shouldUseVirtualization.value,
    reason: shouldUseVirtualization.value
      ? `Using virtualized grid (${totalWeeks} weeks > ${virtualizationThreshold} threshold)`
      : `Using regular grid (${totalWeeks} weeks <= ${virtualizationThreshold} threshold)`,
    performanceMode: performanceMode,
    isLowEndDevice: isLowEndDevice.value,
    features: features.value,
  }))

  return {
    GridComponent,
    features,
    shouldUseVirtualization,
    getComponentProps,
    migrationInfo,
    isLowEndDevice,
  }
}

/**
 * Performance monitoring hook for grid components
 */
export function useGridPerformanceMonitoring() {
  const metrics = ref({
    renderTime: 0,
    scrollLatency: 0,
    memoryUsage: 0,
    cacheHitRatio: 0,
    visibleItems: 0,
    totalItems: 0,
  })

  const isMonitoring = ref(false)

  const startMonitoring = () => {
    isMonitoring.value = true

    // Performance observer for render timing
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach((entry) => {
          if (entry.name.includes('grid-render')) {
            metrics.value.renderTime = entry.duration
          }
        })
      })

      observer.observe({ entryTypes: ['measure'] })
    }

    // Memory monitoring
    if ((performance as any).memory) {
      const updateMemory = () => {
        if (isMonitoring.value) {
          metrics.value.memoryUsage = (performance as any).memory.usedJSHeapSize
          setTimeout(updateMemory, 5000) // Update every 5 seconds
        }
      }
      updateMemory()
    }
  }

  const stopMonitoring = () => {
    isMonitoring.value = false
  }

  const recordMetric = (name: keyof typeof metrics.value, value: number) => {
    if (isMonitoring.value) {
      metrics.value[name] = value
    }
  }

  const getPerformanceReport = () => ({
    ...metrics.value,
    timestamp: Date.now(),
    isMonitoring: isMonitoring.value,
  })

  return {
    metrics,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    recordMetric,
    getPerformanceReport,
  }
}

/**
 * Feature flag management for grid virtualization
 */
export class GridFeatureFlags {
  private flags: Map<string, boolean> = new Map()
  private listeners: Map<string, ((enabled: boolean) => void)[]> = new Map()

  constructor(initialFlags: Record<string, boolean> = {}) {
    Object.entries(initialFlags).forEach(([key, value]) => {
      this.flags.set(key, value)
    })
  }

  setFlag(name: string, enabled: boolean): void {
    const wasEnabled = this.flags.get(name)
    this.flags.set(name, enabled)

    // Notify listeners if value changed
    if (wasEnabled !== enabled) {
      const flagListeners = this.listeners.get(name) || []
      flagListeners.forEach((listener) => listener(enabled))
    }
  }

  getFlag(name: string, defaultValue: boolean = false): boolean {
    return this.flags.get(name) ?? defaultValue
  }

  onFlagChange(name: string, listener: (enabled: boolean) => void): () => void {
    if (!this.listeners.has(name)) {
      this.listeners.set(name, [])
    }
    this.listeners.get(name)!.push(listener)

    // Return unsubscribe function
    return () => {
      const flagListeners = this.listeners.get(name) || []
      const index = flagListeners.indexOf(listener)
      if (index > -1) {
        flagListeners.splice(index, 1)
      }
    }
  }

  getAllFlags(): Record<string, boolean> {
    return Object.fromEntries(this.flags.entries())
  }

  // Predefined feature flags for grid virtualization
  static readonly FLAGS = {
    ENABLE_VIRTUALIZATION: 'grid.enableVirtualization',
    ENABLE_LAZY_LOADING: 'grid.enableLazyLoading',
    ENABLE_SCROLL_PERSISTENCE: 'grid.enableScrollPersistence',
    ENABLE_PERFORMANCE_METRICS: 'grid.enablePerformanceMetrics',
    ENABLE_RESPONSIVE_DESIGN: 'grid.enableResponsiveDesign',
    ENABLE_PREFETCHING: 'grid.enablePrefetching',
  } as const
}

// Global feature flags instance
export const gridFeatureFlags = new GridFeatureFlags({
  [GridFeatureFlags.FLAGS.ENABLE_VIRTUALIZATION]: true,
  [GridFeatureFlags.FLAGS.ENABLE_LAZY_LOADING]: true,
  [GridFeatureFlags.FLAGS.ENABLE_SCROLL_PERSISTENCE]: true,
  [GridFeatureFlags.FLAGS.ENABLE_PERFORMANCE_METRICS]: false,
  [GridFeatureFlags.FLAGS.ENABLE_RESPONSIVE_DESIGN]: true,
  [GridFeatureFlags.FLAGS.ENABLE_PREFETCHING]: true,
})

/**
 * A/B testing utilities for grid virtualization
 */
export class GridABTesting {
  private variant: 'control' | 'virtualized'
  private userId: string
  private metrics: Map<string, number> = new Map()

  constructor(userId: string, forceVariant?: 'control' | 'virtualized') {
    this.userId = userId

    if (forceVariant) {
      this.variant = forceVariant
    } else {
      // Simple hash-based assignment
      const hash = this.hashString(userId)
      this.variant = hash % 2 === 0 ? 'control' : 'virtualized'
    }
  }

  private hashString(str: string): number {
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i)
      hash = (hash << 5) - hash + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return Math.abs(hash)
  }

  getVariant(): 'control' | 'virtualized' {
    return this.variant
  }

  shouldUseVirtualization(): boolean {
    return this.variant === 'virtualized'
  }

  recordMetric(name: string, value: number): void {
    this.metrics.set(name, value)
  }

  getExperimentData() {
    return {
      userId: this.userId,
      variant: this.variant,
      metrics: Object.fromEntries(this.metrics.entries()),
      timestamp: Date.now(),
    }
  }
}

/**
 * Migration guide component for developers
 */
export const GridMigrationGuide = {
  getCompatibilityInfo: (currentProps: Record<string, any>) => {
    const compatibleProps = ['highlightedWeeks', 'showNotes', 'interactive', 'maxWidth', 'cellSize']

    const newProps = ['containerHeight', 'showPerformanceMetrics']

    const deprecatedProps: string[] = []

    return {
      compatibleProps: compatibleProps.filter((prop) => prop in currentProps),
      newProps: newProps.filter((prop) => !(prop in currentProps)),
      deprecatedProps,
      migrationRequired: deprecatedProps.length > 0,
    }
  },

  getMigrationSteps: () => [
    {
      step: 1,
      title: 'Install dependencies',
      description: 'No additional dependencies required for virtualization',
      code: '// Virtualization composables are included in the project',
    },
    {
      step: 2,
      title: 'Replace component import',
      description: 'Use the integration utility to automatically select the right component',
      code: `
import { useGridIntegration } from '@/components/GridIntegration'

// In your component:
const { GridComponent, getComponentProps } = useGridIntegration(totalWeeks)

// In template:
<component :is="GridComponent" v-bind="getComponentProps(props)" />
      `.trim(),
    },
    {
      step: 3,
      title: 'Optional: Add performance monitoring',
      description: 'Enable performance metrics to monitor the impact',
      code: `
import { useGridPerformanceMonitoring } from '@/components/GridIntegration'

const { startMonitoring, getPerformanceReport } = useGridPerformanceMonitoring()
startMonitoring()
      `.trim(),
    },
  ],
}
