/**
 * Unit tests for virtual scrolling composables
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { useVirtualScrolling, useGridVirtualScrolling } from '@/composables/useVirtualScrolling'
import { useLazyLoading } from '@/composables/useLazyLoading'
import { useScrollPersistence } from '@/composables/useScrollPersistence'
import { useResponsiveGrid } from '@/composables/useResponsiveGrid'

// Mock DOM APIs
const mockScrollTo = vi.fn()
const mockAddEventListener = vi.fn()
const mockRemoveEventListener = vi.fn()

Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
  value: mockScrollTo,
  writable: true
})

Object.defineProperty(HTMLElement.prototype, 'addEventListener', {
  value: mockAddEventListener,
  writable: true
})

Object.defineProperty(HTMLElement.prototype, 'removeEventListener', {
  value: mockRemoveEventListener,
  writable: true
})

describe('useVirtualScrolling', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should calculate visible items correctly', () => {
    const virtualScrolling = useVirtualScrolling({
      totalItems: 1000,
      itemHeight: 20,
      containerHeight: 400,
      overscan: 2
    })

    expect(virtualScrolling.totalHeight.value).toBe(20000) // 1000 * 20
    expect(virtualScrolling.visibleItems.value.length).toBeGreaterThan(0)
    expect(virtualScrolling.startIndex.value).toBe(0)
  })

  it('should update visible range when scrolling', async () => {
    const virtualScrolling = useVirtualScrolling({
      totalItems: 1000,
      itemHeight: 20,
      containerHeight: 400,
      overscan: 2
    })

    // Simulate scroll position change
    virtualScrolling.scrollTop.value = 400 // Scroll down 400px
    await nextTick()

    expect(virtualScrolling.startIndex.value).toBeGreaterThan(0)
  })

  it('should handle scroll to index', () => {
    const virtualScrolling = useVirtualScrolling({
      totalItems: 1000,
      itemHeight: 20,
      containerHeight: 400
    })

    // Mock container element
    const mockContainer = {
      scrollTo: mockScrollTo
    }
    virtualScrolling.containerRef.value = mockContainer as any

    virtualScrolling.scrollToIndex(100, 'smooth')

    expect(mockScrollTo).toHaveBeenCalledWith({
      top: 2000, // 100 * 20
      behavior: 'smooth'
    })
  })

  it('should ensure item visibility', () => {
    const virtualScrolling = useVirtualScrolling({
      totalItems: 1000,
      itemHeight: 20,
      containerHeight: 400
    })

    virtualScrolling.containerRef.value = { scrollTo: mockScrollTo } as any

    // Item is below viewport
    virtualScrolling.scrollTop.value = 0
    virtualScrolling.ensureItemVisible(50)

    expect(mockScrollTo).toHaveBeenCalled()
  })

  it('should update configuration dynamically', () => {
    const virtualScrolling = useVirtualScrolling({
      totalItems: 1000,
      itemHeight: 20,
      containerHeight: 400
    })

    const initialHeight = virtualScrolling.totalHeight.value

    virtualScrolling.updateTotalItems(500)
    expect(virtualScrolling.totalHeight.value).toBe(initialHeight / 2)

    virtualScrolling.updateItemHeight(40)
    expect(virtualScrolling.totalHeight.value).toBe(500 * 40)
  })
})

describe('useGridVirtualScrolling', () => {
  it('should calculate grid positions correctly', () => {
    const gridScrolling = useGridVirtualScrolling({
      totalItems: 2600, // 50 years * 52 weeks
      itemHeight: 12,
      columns: 52,
      cellWidth: 12,
      containerHeight: 600,
      gap: 1
    })

    // Test specific grid positions
    const pos0 = gridScrolling.getGridPosition(0)
    expect(pos0).toEqual({ row: 0, col: 0, x: 0, y: 0 })

    const pos52 = gridScrolling.getGridPosition(52) // Start of second row
    expect(pos52.row).toBe(1)
    expect(pos52.col).toBe(0)
    expect(pos52.y).toBe(12)

    const pos53 = gridScrolling.getGridPosition(53) // Second item of second row
    expect(pos53.row).toBe(1)
    expect(pos53.col).toBe(1)
    expect(pos53.x).toBe(13) // cellWidth + gap
  })

  it('should calculate grid width correctly', () => {
    const gridScrolling = useGridVirtualScrolling({
      totalItems: 1000,
      itemHeight: 10,
      columns: 50,
      cellWidth: 15,
      containerHeight: 500,
      gap: 2
    })

    // Expected width: 50 cells * 15px + 49 gaps * 2px = 750 + 98 = 848
    expect(gridScrolling.gridWidth.value).toBe(848)
  })

  it('should update grid configuration', () => {
    const gridScrolling = useGridVirtualScrolling({
      totalItems: 1000,
      itemHeight: 10,
      columns: 50,
      cellWidth: 15,
      containerHeight: 500,
      gap: 2
    })

    const initialWidth = gridScrolling.gridWidth.value

    gridScrolling.updateColumns(25)
    expect(gridScrolling.gridWidth.value).toBeLessThan(initialWidth)

    gridScrolling.updateCellWidth(20)
    expect(gridScrolling.gridWidth.value).toBeGreaterThan(initialWidth / 2)
  })
})

describe('useLazyLoading', () => {
  it('should load data on demand', async () => {
    const mockLoadData = vi.fn().mockImplementation(async (start, end) => {
      const items = []
      for (let i = start; i <= end; i++) {
        items.push({ id: i, value: `item-${i}` })
      }
      return items
    })

    const lazyLoading = useLazyLoading({
      loadData: mockLoadData,
      cacheSize: 100,
      prefetchCount: 5
    })

    // Load a single item
    const item = await lazyLoading.getData(10)
    expect(item).toBeTruthy()
    expect(mockLoadData).toHaveBeenCalledWith(10, 10)

    // Verify caching
    expect(lazyLoading.isDataCached(10)).toBe(true)

    // Load cached item (should not trigger new load)
    mockLoadData.mockClear()
    await lazyLoading.getData(10)
    expect(mockLoadData).not.toHaveBeenCalled()
  })

  it('should load ranges efficiently', async () => {
    const mockLoadData = vi.fn().mockResolvedValue([
      { id: 1 }, { id: 2 }, { id: 3 }
    ])

    const lazyLoading = useLazyLoading({
      loadData: mockLoadData,
      cacheSize: 50
    })

    await lazyLoading.loadRange(1, 3)
    expect(mockLoadData).toHaveBeenCalledWith(1, 3)

    // Verify all items are cached
    expect(lazyLoading.isDataCached(1)).toBe(true)
    expect(lazyLoading.isDataCached(2)).toBe(true)
    expect(lazyLoading.isDataCached(3)).toBe(true)
  })

  it('should handle prefetching', async () => {
    const mockLoadData = vi.fn().mockImplementation(async (start, end) => {
      const items = []
      for (let i = start; i <= end; i++) {
        items.push({ id: i })
      }
      return items
    })

    const lazyLoading = useLazyLoading({
      loadData: mockLoadData,
      prefetchCount: 5
    })

    await lazyLoading.loadVisibleItems([10, 11, 12])

    // Should load visible items plus prefetch buffer
    expect(mockLoadData).toHaveBeenCalledWith(5, 17) // 10-5 to 12+5
  })

  it('should manage cache size with LRU eviction', async () => {
    const mockLoadData = vi.fn().mockImplementation(async (start, end) => {
      return [{ id: start }]
    })

    const lazyLoading = useLazyLoading({
      loadData: mockLoadData,
      cacheSize: 3 // Very small cache
    })

    // Fill cache beyond capacity
    await lazyLoading.getData(1)
    await lazyLoading.getData(2)
    await lazyLoading.getData(3)
    await lazyLoading.getData(4) // Should evict item 1

    const stats = lazyLoading.getCacheStats()
    expect(stats.size).toBe(3)
    expect(lazyLoading.isDataCached(1)).toBe(false) // Should be evicted
    expect(lazyLoading.isDataCached(4)).toBe(true)
  })

  it('should track performance metrics', async () => {
    const mockLoadData = vi.fn().mockResolvedValue([{ id: 1 }])

    const lazyLoading = useLazyLoading({
      loadData: mockLoadData
    })

    await lazyLoading.getData(1)
    await lazyLoading.getData(1) // Cache hit

    const stats = lazyLoading.getCacheStats()
    expect(stats.metrics.cacheHits).toBe(1)
    expect(stats.metrics.cacheMisses).toBe(1)
    expect(stats.hitRatio).toBe(0.5)
  })

  it('should handle loading errors gracefully', async () => {
    const mockLoadData = vi.fn().mockRejectedValue(new Error('Network error'))

    const lazyLoading = useLazyLoading({
      loadData: mockLoadData
    })

    const result = await lazyLoading.getData(1)
    expect(result).toBeNull()
    expect(lazyLoading.loadingState.value.error).toBe('Network error')
  })
})

describe('useScrollPersistence', () => {
  let mockStorage: Map<string, string>

  beforeEach(() => {
    mockStorage = new Map()
    
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn((key) => mockStorage.get(key) || null),
        setItem: vi.fn((key, value) => mockStorage.set(key, value)),
        removeItem: vi.fn((key) => mockStorage.delete(key))
      },
      writable: true
    })
  })

  it('should save and restore scroll position', async () => {
    const scrollPersistence = useScrollPersistence({
      key: 'test-grid',
      debounceDelay: 10
    })

    const testPosition = { top: 500, left: 0, timestamp: Date.now() }
    scrollPersistence.saveScrollPosition(testPosition)

    const restored = scrollPersistence.loadScrollPosition()
    expect(restored).toEqual(testPosition)
  })

  it('should handle missing storage gracefully', () => {
    const scrollPersistence = useScrollPersistence({
      key: 'test-grid'
    })

    const restored = scrollPersistence.loadScrollPosition()
    expect(restored).toBeNull()
  })

  it('should clear saved position', () => {
    const scrollPersistence = useScrollPersistence({
      key: 'test-grid'
    })

    scrollPersistence.saveScrollPosition({ top: 100, left: 0, timestamp: Date.now() })
    expect(scrollPersistence.loadScrollPosition()).toBeTruthy()

    scrollPersistence.clearScrollPosition()
    expect(scrollPersistence.loadScrollPosition()).toBeNull()
  })

  it('should set scroll position programmatically', () => {
    const scrollPersistence = useScrollPersistence({
      key: 'test-grid'
    })

    const mockContainer = { scrollTo: mockScrollTo }
    scrollPersistence.containerRef.value = mockContainer as any

    scrollPersistence.setScrollPosition(200, 0, 'smooth')

    expect(mockScrollTo).toHaveBeenCalledWith({
      top: 200,
      left: 0,
      behavior: 'smooth'
    })
  })
})

describe('useResponsiveGrid', () => {
  beforeEach(() => {
    // Mock window dimensions
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024
    })
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 768
    })
  })

  it('should detect correct breakpoints', () => {
    const responsive = useResponsiveGrid({
      baseConfig: {
        columns: 52,
        cellSize: 12,
        gap: 1,
        containerHeight: 600
      }
    })

    // Large desktop
    responsive.windowWidth.value = 1200
    expect(responsive.currentBreakpoint.value).toBe('xl')

    // Tablet
    responsive.windowWidth.value = 800
    expect(responsive.currentBreakpoint.value).toBe('md')

    // Mobile
    responsive.windowWidth.value = 400
    expect(responsive.currentBreakpoint.value).toBe('xs')
  })

  it('should adapt grid configuration to breakpoints', () => {
    const responsive = useResponsiveGrid({
      baseConfig: {
        columns: 52,
        cellSize: 12,
        gap: 1,
        containerHeight: 600
      }
    })

    // Desktop configuration
    responsive.windowWidth.value = 1200
    responsive.windowHeight.value = 800
    const desktopConfig = responsive.gridConfig.value
    expect(desktopConfig.columns).toBe(52)

    // Mobile configuration
    responsive.windowWidth.value = 400
    responsive.windowHeight.value = 600
    const mobileConfig = responsive.gridConfig.value
    expect(mobileConfig.columns).toBeLessThan(52)
    expect(mobileConfig.cellSize).toBeLessThan(desktopConfig.cellSize)
  })

  it('should calculate optimal configurations', () => {
    const responsive = useResponsiveGrid({
      baseConfig: {
        columns: 52,
        cellSize: 12,
        gap: 1,
        containerHeight: 600
      }
    })

    responsive.windowWidth.value = 800

    const optimalCellSize = responsive.calculateOptimalCellSize(40)
    expect(optimalCellSize).toBeGreaterThan(0)

    const optimalColumns = responsive.calculateOptimalColumns(15)
    expect(optimalColumns).toBeGreaterThan(0)
    expect(optimalColumns).toBeLessThan(60) // Reasonable upper limit
  })

  it('should provide CSS custom properties', () => {
    const responsive = useResponsiveGrid({
      baseConfig: {
        columns: 52,
        cellSize: 12,
        gap: 1,
        containerHeight: 600
      }
    })

    const cssProps = responsive.getCSSProperties()

    expect(cssProps).toHaveProperty('--grid-columns')
    expect(cssProps).toHaveProperty('--grid-cell-size')
    expect(cssProps).toHaveProperty('--grid-gap')
    expect(cssProps['--grid-columns']).toBe('52')
    expect(cssProps['--grid-cell-size']).toBe('12px')
  })

  it('should detect device capabilities', () => {
    const responsive = useResponsiveGrid({
      baseConfig: {
        columns: 52,
        cellSize: 12,
        gap: 1,
        containerHeight: 600
      }
    })

    responsive.windowWidth.value = 400
    expect(responsive.isMobile.value).toBe(true)
    expect(responsive.isDesktop.value).toBe(false)

    responsive.windowWidth.value = 1200
    expect(responsive.isMobile.value).toBe(false)
    expect(responsive.isDesktop.value).toBe(true)
  })
})