/**
 * Scroll position persistence composable
 * Saves and restores scroll positions across navigation and page reloads
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'

export interface ScrollPersistenceOptions {
  /** Unique key for this scroll container */
  key: string
  /** Storage type to use */
  storage?: 'localStorage' | 'sessionStorage'
  /** Debounce delay for saving scroll position (ms) */
  debounceDelay?: number
  /** Enable debugging logs */
  debug?: boolean
}

export interface ScrollPosition {
  top: number
  left: number
  timestamp: number
}

export function useScrollPersistence(options: ScrollPersistenceOptions) {
  const storageKey = `scroll-position-${options.key}`
  const storage = options.storage === 'sessionStorage' ? sessionStorage : localStorage
  const debounceDelay = options.debounceDelay || 100
  const debug = options.debug || false

  // Current scroll position
  const scrollPosition = ref<ScrollPosition>({ top: 0, left: 0, timestamp: 0 })
  
  // Container element reference
  const containerRef = ref<HTMLElement>()
  
  // Debounce timeout
  let saveTimeout: number | undefined

  // Save scroll position to storage
  const saveScrollPosition = (position: ScrollPosition) => {
    try {
      storage.setItem(storageKey, JSON.stringify(position))
      if (debug) {
        console.log(`Saved scroll position for ${options.key}:`, position)
      }
    } catch (error) {
      if (debug) {
        console.error(`Failed to save scroll position for ${options.key}:`, error)
      }
    }
  }

  // Load scroll position from storage
  const loadScrollPosition = (): ScrollPosition | null => {
    try {
      const saved = storage.getItem(storageKey)
      if (saved) {
        const position = JSON.parse(saved) as ScrollPosition
        if (debug) {
          console.log(`Loaded scroll position for ${options.key}:`, position)
        }
        return position
      }
    } catch (error) {
      if (debug) {
        console.error(`Failed to load scroll position for ${options.key}:`, error)
      }
    }
    return null
  }

  // Handle scroll events with debouncing
  const handleScroll = (event: Event) => {
    const target = event.target as HTMLElement
    const position: ScrollPosition = {
      top: target.scrollTop,
      left: target.scrollLeft,
      timestamp: Date.now()
    }

    scrollPosition.value = position

    // Debounce saving to storage
    if (saveTimeout) {
      clearTimeout(saveTimeout)
    }
    saveTimeout = window.setTimeout(() => {
      saveScrollPosition(position)
    }, debounceDelay)
  }

  // Restore scroll position to container
  const restoreScrollPosition = (position?: ScrollPosition) => {
    if (!containerRef.value) return

    const targetPosition = position || loadScrollPosition()
    if (!targetPosition) return

    // Set scroll position
    containerRef.value.scrollTop = targetPosition.top
    containerRef.value.scrollLeft = targetPosition.left

    // Update reactive position
    scrollPosition.value = targetPosition

    if (debug) {
      console.log(`Restored scroll position for ${options.key}:`, targetPosition)
    }
  }

  // Clear saved scroll position
  const clearScrollPosition = () => {
    try {
      storage.removeItem(storageKey)
      scrollPosition.value = { top: 0, left: 0, timestamp: 0 }
      if (debug) {
        console.log(`Cleared scroll position for ${options.key}`)
      }
    } catch (error) {
      if (debug) {
        console.error(`Failed to clear scroll position for ${options.key}:`, error)
      }
    }
  }

  // Set scroll position programmatically and save it
  const setScrollPosition = (top: number, left: number = 0, behavior: ScrollBehavior = 'auto') => {
    if (!containerRef.value) return

    containerRef.value.scrollTo({ top, left, behavior })

    // Update and save position
    const position: ScrollPosition = { top, left, timestamp: Date.now() }
    scrollPosition.value = position
    saveScrollPosition(position)
  }

  // Initialize scroll persistence
  const initialize = () => {
    if (!containerRef.value) return

    // Add scroll listener
    containerRef.value.addEventListener('scroll', handleScroll, { passive: true })

    // Restore position on next tick to ensure DOM is ready
    setTimeout(() => {
      restoreScrollPosition()
    }, 0)
  }

  // Cleanup
  const cleanup = () => {
    if (saveTimeout) {
      clearTimeout(saveTimeout)
    }
    
    if (containerRef.value) {
      containerRef.value.removeEventListener('scroll', handleScroll)
    }
  }

  // Save current position before unload
  const handleBeforeUnload = () => {
    if (containerRef.value) {
      const position: ScrollPosition = {
        top: containerRef.value.scrollTop,
        left: containerRef.value.scrollLeft,
        timestamp: Date.now()
      }
      saveScrollPosition(position)
    }
  }

  // Lifecycle hooks
  onMounted(() => {
    initialize()
    window.addEventListener('beforeunload', handleBeforeUnload)
  })

  onUnmounted(() => {
    cleanup()
    window.removeEventListener('beforeunload', handleBeforeUnload)
  })

  // Watch for container changes
  watch(containerRef, (newContainer, oldContainer) => {
    if (oldContainer) {
      oldContainer.removeEventListener('scroll', handleScroll)
    }
    if (newContainer) {
      newContainer.addEventListener('scroll', handleScroll, { passive: true })
      setTimeout(() => {
        restoreScrollPosition()
      }, 0)
    }
  })

  return {
    // Template refs
    containerRef,
    
    // State
    scrollPosition,
    
    // Methods
    restoreScrollPosition,
    clearScrollPosition,
    setScrollPosition,
    saveScrollPosition,
    loadScrollPosition
  }
}

// Specialized version for grid scroll persistence
export interface GridScrollPersistenceOptions extends ScrollPersistenceOptions {
  /** Current selected item index for additional context */
  selectedIndex?: number
  /** Total number of items for validation */
  totalItems?: number
}

export function useGridScrollPersistence(options: GridScrollPersistenceOptions) {
  const basePersistence = useScrollPersistence(options)

  // Extended scroll position with grid context
  interface GridScrollPosition extends ScrollPosition {
    selectedIndex?: number
    totalItems?: number
  }

  // Save grid-specific position
  const saveGridPosition = (position: ScrollPosition, selectedIndex?: number, totalItems?: number) => {
    const gridPosition: GridScrollPosition = {
      ...position,
      selectedIndex,
      totalItems
    }

    try {
      const storageKey = `scroll-position-${options.key}`
      const storage = options.storage === 'sessionStorage' ? sessionStorage : localStorage
      storage.setItem(storageKey, JSON.stringify(gridPosition))
      
      if (options.debug) {
        console.log(`Saved grid scroll position for ${options.key}:`, gridPosition)
      }
    } catch (error) {
      if (options.debug) {
        console.error(`Failed to save grid scroll position for ${options.key}:`, error)
      }
    }
  }

  // Load grid-specific position
  const loadGridPosition = (): GridScrollPosition | null => {
    try {
      const storageKey = `scroll-position-${options.key}`
      const storage = options.storage === 'sessionStorage' ? sessionStorage : localStorage
      const saved = storage.getItem(storageKey)
      
      if (saved) {
        const position = JSON.parse(saved) as GridScrollPosition
        
        // Validate that the position is still relevant
        if (options.totalItems && position.totalItems && position.totalItems !== options.totalItems) {
          if (options.debug) {
            console.log(`Grid size changed, ignoring saved position for ${options.key}`)
          }
          return null
        }
        
        if (options.debug) {
          console.log(`Loaded grid scroll position for ${options.key}:`, position)
        }
        return position
      }
    } catch (error) {
      if (options.debug) {
        console.error(`Failed to load grid scroll position for ${options.key}:`, error)
      }
    }
    return null
  }

  // Scroll to specific item in grid
  const scrollToItem = (itemIndex: number, behavior: ScrollBehavior = 'smooth') => {
    // This will be implemented based on the specific grid layout
    // For now, delegate to base implementation
    basePersistence.setScrollPosition(itemIndex * 20, 0, behavior) // Assuming 20px per item
  }

  return {
    ...basePersistence,
    
    // Grid-specific methods
    saveGridPosition,
    loadGridPosition,
    scrollToItem
  }
}