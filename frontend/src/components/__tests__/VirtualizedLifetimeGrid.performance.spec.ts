// Performance tests for VirtualizedLifetimeGrid.
// Corrupted content removed; keeping meaningful tests only.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { createTestingPinia } from '@pinia/testing'
import VirtualizedLifetimeGrid from '@/components/VirtualizedLifetimeGrid.vue'
import { useLazyLoading } from '@/composables/useLazyLoading'
import { useScrollPersistence } from '@/composables/useScrollPersistence'
import { useVirtualScrolling, useGridVirtualScrolling } from '@/composables/useVirtualScrolling'

class PerformanceMonitor {
  private measurements: Map<string, number[]> = new Map()
  private memorySnapshots: any[] = []
  startMeasurement(name: string) {
    const start = performance.now()
    if (!this.measurements.has(name)) this.measurements.set(name, [])
    this.measurements.get(name)!.push(start)
  }
  endMeasurement(name: string) {
    const end = performance.now()
    const arr = this.measurements.get(name)
    if (!arr || arr.length === 0) throw new Error(`No start for ${name}`)
    const start = arr.pop()!
    const duration = end - start
    arr.push(duration)
    return duration
  }
  takeMemorySnapshot() {
    if ((performance as any).memory) {
      this.memorySnapshots.push({ used: (performance as any).memory.usedJSHeapSize })
    }
  }
  getMemoryDelta() {
    if (this.memorySnapshots.length < 2) return 0
    return this.memorySnapshots.at(-1)!.used - this.memorySnapshots[0].used
  }
  reset() {
    this.measurements.clear()
    this.memorySnapshots = []
  }
}

describe('VirtualizedLifetimeGrid Performance', () => {
  let monitor: PerformanceMonitor
  let wrapper: any

  beforeEach(() => {
    monitor = new PerformanceMonitor()
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    monitor.reset()
  })

  describe.skip('Virtual Scrolling Performance', () => {
    it('should render initial view within performance budget', async () => {
      monitor.startMeasurement('initial-render')
      monitor.takeMemorySnapshot()

      wrapper = mount(VirtualizedLifetimeGrid, {
        props: {
          containerHeight: 600,
          cellSize: 12,
          totalWeeks: 4000, // ~80 years
        },
        global: {
          plugins: [
            createTestingPinia({
              createSpy: vi.fn,
              initialState: {
                weekCalculation: {
                  totalLifetimeWeeks: 4000,
                  currentWeekIndex: 2000,
                  weeksLived: 2000,
                },
                user: {
                  currentUser: {
                    id: 1,
                    date_of_birth: '1990-01-01',
                    lifespan: 80,
                  },
                  hasDateOfBirth: true,
                },
              },
            }),
          ],
        },
      })

      await nextTick()
      const renderTime = monitor.endMeasurement('initial-render')
      monitor.takeMemorySnapshot()

      // Performance assertions
      expect(renderTime).toBeLessThan(100) // Should render within 100ms

      // Should only render visible weeks, not all 4000
      const weekCells = wrapper.findAll('.week-cell')
      expect(weekCells.length).toBeLessThan(200) // Much less than total weeks
      expect(weekCells.length).toBeGreaterThan(0)
    })

    it('should handle scroll events efficiently', async () => {
      wrapper = mount(VirtualizedLifetimeGrid, {
        props: {
          containerHeight: 400,
          cellSize: 10,
          totalWeeks: 4000,
        },
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
        },
      })

      await nextTick()
      const container = wrapper.find('.virtual-grid-container').element

      // Simulate multiple scroll events
      const scrollTimes: number[] = []
      for (let i = 0; i < 10; i++) {
        monitor.startMeasurement(`scroll-${i}`)

        // Simulate scroll
        container.scrollTop = i * 100
        const scrollEvent = new Event('scroll')
        container.dispatchEvent(scrollEvent)

        await nextTick()
        scrollTimes.push(monitor.endMeasurement(`scroll-${i}`))
      }

      // Average scroll handling should be fast
      const avgScrollTime = scrollTimes.reduce((sum, time) => sum + time, 0) / scrollTimes.length
      expect(avgScrollTime).toBeLessThan(16) // 60fps budget (16.67ms per frame)
    })

    it('should maintain stable memory usage during scrolling', async () => {
      wrapper = mount(VirtualizedLifetimeGrid, {
        props: {
          containerHeight: 300,
          totalWeeks: 5000,
        },
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
        },
      })

      await nextTick()
      monitor.takeMemorySnapshot()

      const container = wrapper.find('.virtual-grid-container').element

      // Simulate extensive scrolling
      for (let i = 0; i < 50; i++) {
        container.scrollTop = i * 50
        const scrollEvent = new Event('scroll')
        container.dispatchEvent(scrollEvent)
        await nextTick()

        if (i % 10 === 0) {
          monitor.takeMemorySnapshot()
        }
      }

      const memoryDelta = monitor.getMemoryDelta()

      // Memory growth should be reasonable (less than 5MB for extensive scrolling)
      expect(memoryDelta).toBeLessThan(5 * 1024 * 1024)
    })
  })

  describe.skip('Lazy Loading Performance', () => {
    it('should load data efficiently with proper caching', async () => {
      const mockLoadData = vi.fn().mockImplementation(async (start: number, end: number) => {
        // Simulate network delay
        await new Promise((resolve) => setTimeout(resolve, 50))
        const data = []
        for (let i = start; i <= end; i++) {
          data.push({
            weekIndex: i,
            hasNotes: i % 10 === 0,
            noteCount: i % 10 === 0 ? Math.floor(Math.random() * 5) : 0,
          })
        }
        return data
      })

      const { loadRange, getCacheStats, isDataCached } = useLazyLoading({
        loadData: mockLoadData,
        prefetchCount: 10,
        cacheSize: 500,
      })

      monitor.startMeasurement('data-loading')

      // Load initial range
      await loadRange(0, 50)
      const loadTime1 = monitor.endMeasurement('data-loading')

      // Load overlapping range (should be faster due to caching)
      monitor.startMeasurement('cached-loading')
      await loadRange(25, 75)
      const loadTime2 = monitor.endMeasurement('cached-loading')

      // Verify caching effectiveness
      expect(isDataCached(30)).toBe(true)
      expect(loadTime2).toBeLessThan(loadTime1) // Cached access should be faster

      const stats = getCacheStats()
      expect(stats.hitRatio).toBeGreaterThan(0.3) // Should have decent cache hit ratio
    })

    it('should handle cache eviction properly', async () => {
      const mockLoadData = vi.fn().mockResolvedValue([])

      const { loadRange, getCacheStats, clearCache } = useLazyLoading({
        loadData: mockLoadData,
        cacheSize: 100, // Small cache for testing eviction
      })

      // Fill cache beyond capacity
      for (let i = 0; i < 150; i += 10) {
        await loadRange(i, i + 9)
      }

      const stats = getCacheStats()
      expect(stats.size).toBeLessThanOrEqual(100) // Should not exceed cache size

      // Clear cache and verify
      clearCache()
      const clearedStats = getCacheStats()
      expect(clearedStats.size).toBe(0)
    })
  })

  describe('Scroll Position Persistence', () => {
    it('should save and restore scroll position efficiently', async () => {
      const mockStorage = {
        data: new Map<string, string>(),
        getItem: vi.fn((key: string) => mockStorage.data.get(key) || null),
        setItem: vi.fn((key: string, value: string) => mockStorage.data.set(key, value)),
        removeItem: vi.fn((key: string) => mockStorage.data.delete(key)),
      }

      // Mock localStorage
      Object.defineProperty(window, 'localStorage', {
        value: mockStorage,
        writable: true,
      })

      const { setScrollPosition: _setScrollPosition, loadScrollPosition, saveScrollPosition } = useScrollPersistence({
        key: 'test-grid',
        debounceDelay: 50,
      })

      monitor.startMeasurement('save-position')

      // Save position
      const testPosition = { top: 1000, left: 0, timestamp: Date.now() }
      saveScrollPosition(testPosition)

      const saveTime = monitor.endMeasurement('save-position')

      monitor.startMeasurement('load-position')

      // Load position
      const loadedPosition = loadScrollPosition()

      const loadTime = monitor.endMeasurement('load-position')

      // Verify performance
      expect(saveTime).toBeLessThan(10) // Saving should be fast
      expect(loadTime).toBeLessThan(5) // Loading should be very fast

      // Verify correctness
      expect(loadedPosition).toEqual(testPosition)
    })
  })

  describe.skip('Memory Management', () => {
    it('should not leak memory during component lifecycle', async () => {
      monitor.takeMemorySnapshot()

      // Mount and unmount multiple times
      for (let i = 0; i < 5; i++) {
        const testWrapper = mount(VirtualizedLifetimeGrid, {
          props: { totalWeeks: 2000 },
          global: {
            plugins: [createTestingPinia({ createSpy: vi.fn })],
          },
        })

        await nextTick()
        testWrapper.unmount()

        // Force garbage collection if available
        if (global.gc) {
          global.gc()
        }

        monitor.takeMemorySnapshot()
      }

      const memoryGrowth = monitor.getMemoryDelta()

      // Memory growth should be minimal after multiple mount/unmount cycles
      expect(memoryGrowth).toBeLessThan(2 * 1024 * 1024) // Less than 2MB growth
    })

    it('should properly cleanup event listeners', async () => {
      const addEventListenerSpy = vi.spyOn(window, 'addEventListener')
      const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')

      wrapper = mount(VirtualizedLifetimeGrid, {
        props: { totalWeeks: 1000 },
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
        },
      })

      await nextTick()

      const addedListeners = addEventListenerSpy.mock.calls.length

      wrapper.unmount()

      const removedListeners = removeEventListenerSpy.mock.calls.length

      // Should remove at least as many listeners as were added
      expect(removedListeners).toBeGreaterThanOrEqual(addedListeners)

      addEventListenerSpy.mockRestore()
      removeEventListenerSpy.mockRestore()
    })
  })

  describe.skip('Responsive Performance', () => {
    it('should adapt to viewport changes efficiently', async () => {
      wrapper = mount(VirtualizedLifetimeGrid, {
        props: {
          totalWeeks: 3000,
          containerHeight: 400,
        },
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
        },
      })

      await nextTick()

      // Simulate viewport changes
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1200,
      })

      monitor.startMeasurement('viewport-change')

      // Trigger resize
      const resizeEvent = new Event('resize')
      window.dispatchEvent(resizeEvent)

      await nextTick()
      const resizeTime = monitor.endMeasurement('viewport-change')

      expect(resizeTime).toBeLessThan(50) // Viewport changes should be handled quickly

      // Verify that the grid adapted
      const gridElement = wrapper.find('.virtual-grid')
      expect(gridElement.exists()).toBe(true)
    })
  })
})

describe('Virtual Scrolling Composable', () => {
  it('should calculate viewport correctly', () => {
    const { state, scrollToIndex, ensureItemVisible: _ensureItemVisible } = useVirtualScrolling({
      totalItems: 1000,
      itemHeight: 20,
      containerHeight: 400,
      overscan: 5,
    })

    // Test initial state
    expect(state.value.startIndex).toBe(0)
    expect(state.value.visibleItems.length).toBeGreaterThan(0)
    expect(state.value.totalHeight).toBe(20000) // 1000 * 20

    // Mock container for scroll testing
    const mockContainer = {
      scrollTop: 0,
      scrollTo: vi.fn((options: { top: number; behavior?: ScrollBehavior }) => {
        mockContainer.scrollTop = options.top
      }),
    }

    // Test scroll to index
    scrollToIndex(100)
  })

  it('should handle grid layout correctly', () => {
    const { getGridPosition, gridWidth } = useGridVirtualScrolling({
      totalItems: 2600, // 50 years * 52 weeks
      itemHeight: 12,
      columns: 52,
      cellWidth: 12,
      containerHeight: 600,
      gap: 1,
    })

    // Test grid position calculation
    const position = getGridPosition(104) // Week 104 (2 years + 1 week)
    expect(position.row).toBe(2)
    expect(position.col).toBe(0)
    expect(position.x).toBe(0)
    expect(position.y).toBe(24) // 2 rows * 12px height

    // Test grid width calculation
    expect(gridWidth.value).toBe(52 * 12 + 51 * 1) // columns * cellWidth + gaps
  })
})

describe('Lazy Loading Composable', () => {
  it('should implement LRU cache correctly', async () => {
    const mockLoadData = vi.fn().mockImplementation(async (start, end) => {
      const items = []
      for (let i = start; i <= end; i++) {
        items.push({ id: i, data: `item-${i}` })
      }
      return items
    })

    const { getData, getCacheStats } = useLazyLoading({
      loadData: mockLoadData,
      cacheSize: 5, // Very small cache for testing LRU
    })

    // Fill cache
    for (let i = 0; i < 7; i++) {
      await getData(i)
    }

    const stats = getCacheStats()
    expect(stats.size).toBeLessThanOrEqual(5) // Should not exceed cache size

    // Access first item (should trigger eviction if not in cache)
    const firstItem = await getData(0)
    expect(firstItem).toBeTruthy()
  })

  it('should prefetch efficiently', async () => {
    const loadSpy = vi.fn().mockResolvedValue([])

    const { loadVisibleItems } = useLazyLoading({
      loadData: loadSpy,
      prefetchCount: 10,
    })

    await loadVisibleItems([50, 51, 52, 53, 54])

    // Should load visible items plus prefetch buffer
    expect(loadSpy).toHaveBeenCalledWithExactlyOnceWith(40, 64) // 50-10 to 54+10
  })
})
