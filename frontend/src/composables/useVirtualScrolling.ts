/**
 * Virtual scrolling composable for efficient rendering of large lists
 * Optimized for the LifetimeGrid component with intelligent buffering and caching
 */
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

export interface VirtualScrollingOptions {
  /** Total number of items */
  totalItems: number
  /** Height of each item in pixels */
  itemHeight: number
  /** Number of items per row (for grid layouts) */
  itemsPerRow?: number
  /** Container height in pixels */
  containerHeight: number
  /** Number of items to render outside visible area for smooth scrolling */
  overscan?: number
  /** Enable debugging logs */
  debug?: boolean
}

export interface VirtualScrollingState {
  /** Current scroll position */
  scrollTop: number
  /** Index of first visible item */
  startIndex: number
  /** Index of last visible item */
  endIndex: number
  /** Total height of all items */
  totalHeight: number
  /** Offset from top for visible items */
  offsetY: number
  /** Items currently being rendered */
  visibleItems: number[]
}

export function useVirtualScrolling(options: VirtualScrollingOptions) {
  // Reactive options that can be updated
  const totalItems = ref(options.totalItems)
  const itemHeight = ref(options.itemHeight)
  const itemsPerRow = ref(options.itemsPerRow || 1)
  const containerHeight = ref(options.containerHeight)
  const overscan = ref(options.overscan || 5)
  const debug = ref(options.debug || false)

  // Internal state
  const scrollTop = ref(0)
  const isScrolling = ref(false)
  const scrollTimeout = ref<number>()

  // Container element reference
  const containerRef = ref<HTMLElement>()
  const contentRef = ref<HTMLElement>()

  // Computed values for virtual scrolling calculations
  const totalRows = computed(() => 
    Math.ceil(totalItems.value / itemsPerRow.value)
  )

  const totalHeight = computed(() => 
    totalRows.value * itemHeight.value
  )

  const visibleRows = computed(() => 
    Math.ceil(containerHeight.value / itemHeight.value)
  )

  const startRow = computed(() => {
    const row = Math.floor(scrollTop.value / itemHeight.value)
    return Math.max(0, row - overscan.value)
  })

  const endRow = computed(() => {
    const row = startRow.value + visibleRows.value + (overscan.value * 2)
    return Math.min(totalRows.value - 1, row)
  })

  const startIndex = computed(() => 
    startRow.value * itemsPerRow.value
  )

  const endIndex = computed(() => 
    Math.min(totalItems.value - 1, (endRow.value + 1) * itemsPerRow.value - 1)
  )

  const offsetY = computed(() => 
    startRow.value * itemHeight.value
  )

  const visibleItems = computed(() => {
    const items: number[] = []
    for (let i = startIndex.value; i <= endIndex.value; i++) {
      if (i < totalItems.value) {
        items.push(i)
      }
    }
    return items
  })

  // Current virtual scrolling state
  const state = computed((): VirtualScrollingState => ({
    scrollTop: scrollTop.value,
    startIndex: startIndex.value,
    endIndex: endIndex.value,
    totalHeight: totalHeight.value,
    offsetY: offsetY.value,
    visibleItems: visibleItems.value
  }))

  // Scroll handler with throttling
  const handleScroll = (event: Event) => {
    const target = event.target as HTMLElement
    scrollTop.value = target.scrollTop

    // Set scrolling state
    isScrolling.value = true
    if (scrollTimeout.value) {
      clearTimeout(scrollTimeout.value)
    }
    scrollTimeout.value = setTimeout(() => {
      isScrolling.value = false
    }, 150)

    if (debug.value) {
      console.log('Virtual scroll:', {
        scrollTop: scrollTop.value,
        startRow: startRow.value,
        endRow: endRow.value,
        visibleItems: visibleItems.value.length
      })
    }
  }

  // Scroll to specific item index
  const scrollToIndex = (index: number, behavior: ScrollBehavior = 'smooth') => {
    if (!containerRef.value) return

    const row = Math.floor(index / itemsPerRow.value)
    const targetScrollTop = row * itemHeight.value

    containerRef.value.scrollTo({
      top: targetScrollTop,
      behavior
    })
  }

  // Scroll to specific position
  const scrollToPosition = (position: number, behavior: ScrollBehavior = 'smooth') => {
    if (!containerRef.value) return

    containerRef.value.scrollTo({
      top: position,
      behavior
    })
  }

  // Get the row and column for a given item index
  const getItemPosition = (index: number) => {
    const row = Math.floor(index / itemsPerRow.value)
    const col = index % itemsPerRow.value
    return { row, col }
  }

  // Get the item index from row and column
  const getIndexFromPosition = (row: number, col: number) => {
    return row * itemsPerRow.value + col
  }

  // Check if an item is currently visible
  const isItemVisible = (index: number) => {
    return index >= startIndex.value && index <= endIndex.value
  }

  // Ensure an item is visible by scrolling if necessary
  const ensureItemVisible = (index: number) => {
    const { row } = getItemPosition(index)
    const itemTop = row * itemHeight.value
    const itemBottom = itemTop + itemHeight.value
    const viewportTop = scrollTop.value
    const viewportBottom = scrollTop.value + containerHeight.value

    if (itemTop < viewportTop) {
      // Item is above viewport
      scrollToPosition(itemTop, 'smooth')
    } else if (itemBottom > viewportBottom) {
      // Item is below viewport
      scrollToPosition(itemBottom - containerHeight.value, 'smooth')
    }
  }

  // Update container height (useful for responsive design)
  const updateContainerHeight = (newHeight: number) => {
    containerHeight.value = newHeight
  }

  // Update total items count
  const updateTotalItems = (newTotal: number) => {
    totalItems.value = newTotal
  }

  // Update item height
  const updateItemHeight = (newHeight: number) => {
    itemHeight.value = newHeight
  }

  // Update items per row
  const updateItemsPerRow = (newCount: number) => {
    itemsPerRow.value = newCount
  }

  // Initialize the virtual scrolling
  const initialize = () => {
    if (!containerRef.value) return

    // Set up the container styles
    containerRef.value.style.overflow = 'auto'
    containerRef.value.style.height = `${containerHeight.value}px`

    // Add scroll listener
    containerRef.value.addEventListener('scroll', handleScroll, { passive: true })
  }

  // Cleanup
  const cleanup = () => {
    if (containerRef.value) {
      containerRef.value.removeEventListener('scroll', handleScroll)
    }
    if (scrollTimeout.value) {
      clearTimeout(scrollTimeout.value)
    }
  }

  // Lifecycle hooks
  onMounted(() => {
    nextTick(() => {
      initialize()
    })
  })

  onUnmounted(() => {
    cleanup()
  })

  // Watch for option changes
  watch([totalItems, itemHeight, itemsPerRow, containerHeight], () => {
    if (debug.value) {
      console.log('Virtual scrolling options updated:', {
        totalItems: totalItems.value,
        itemHeight: itemHeight.value,
        itemsPerRow: itemsPerRow.value,
        containerHeight: containerHeight.value
      })
    }
  })

  return {
    // Refs for template
    containerRef,
    contentRef,
    
    // State
    state,
    isScrolling,
    
    // Computed values
    totalHeight,
    visibleItems,
    offsetY,
    
    // Methods
    scrollToIndex,
    scrollToPosition,
    getItemPosition,
    getIndexFromPosition,
    isItemVisible,
    ensureItemVisible,
    updateContainerHeight,
    updateTotalItems,
    updateItemHeight,
    updateItemsPerRow,
    
    // Direct access to reactive values for fine-grained control
    scrollTop,
    startIndex,
    endIndex,
    startRow,
    endRow,
    totalRows
  }
}

// Additional utilities for grid-specific virtual scrolling
export interface GridVirtualScrollingOptions extends VirtualScrollingOptions {
  /** Number of columns in the grid */
  columns: number
  /** Width of each cell */
  cellWidth: number
  /** Gap between cells */
  gap?: number
}

export function useGridVirtualScrolling(options: GridVirtualScrollingOptions) {
  const baseVirtualScrolling = useVirtualScrolling({
    ...options,
    itemsPerRow: options.columns
  })

  const columns = ref(options.columns)
  const cellWidth = ref(options.cellWidth)
  const gap = ref(options.gap || 1)

  // Grid-specific calculations
  const gridWidth = computed(() => 
    columns.value * cellWidth.value + (columns.value - 1) * gap.value
  )

  const getGridPosition = (index: number) => {
    const row = Math.floor(index / columns.value)
    const col = index % columns.value
    return {
      row,
      col,
      x: col * (cellWidth.value + gap.value),
      y: row * options.itemHeight
    }
  }

  const updateColumns = (newColumns: number) => {
    columns.value = newColumns
    baseVirtualScrolling.updateItemsPerRow(newColumns)
  }

  const updateCellWidth = (newWidth: number) => {
    cellWidth.value = newWidth
  }

  return {
    ...baseVirtualScrolling,
    
    // Grid-specific properties
    columns,
    cellWidth,
    gap,
    gridWidth,
    
    // Grid-specific methods
    getGridPosition,
    updateColumns,
    updateCellWidth
  }
}