/**
 * Lazy loading composable with intelligent caching and prefetching
 * Optimized for the LifetimeGrid to load week data on-demand
 */
import { ref, computed } from 'vue'

export interface LazyLoadingOptions<T> {
  /** Function to load data for a range of items */
  loadData: (startIndex: number, endIndex: number) => Promise<T[]>
  /** Number of items to prefetch outside visible range */
  prefetchCount?: number
  /** Maximum number of items to keep in cache */
  cacheSize?: number
  /** Enable debugging logs */
  debug?: boolean
}

export interface CacheEntry<T> {
  data: T
  timestamp: number
  accessCount: number
  lastAccessed: number
}

export interface LoadingState {
  isLoading: boolean
  loadingRanges: { start: number; end: number }[]
  error: string | null
}

export function useLazyLoading<T>(options: LazyLoadingOptions<T>) {
  const prefetchCount = ref(options.prefetchCount || 10)
  const cacheSize = ref(options.cacheSize || 1000)
  const debug = ref(options.debug || false)

  // Cache for loaded data - use any to avoid ref type issues
  const cache = ref<Map<number, any>>(new Map())
  const loadingState = ref<LoadingState>({
    isLoading: false,
    loadingRanges: [],
    error: null
  })

  // Track currently loading ranges to prevent duplicate requests
  const loadingRanges = ref<Set<string>>(new Set())
  
  // Performance metrics
  const metrics = ref({
    cacheHits: 0,
    cacheMisses: 0,
    loadsTriggered: 0,
    itemsLoaded: 0,
    prefetchHits: 0
  })

  // Get cache hit ratio for debugging
  const cacheHitRatio = computed(() => {
    const total = metrics.value.cacheHits + metrics.value.cacheMisses
    return total > 0 ? metrics.value.cacheHits / total : 0
  })

  // Generate a key for a loading range
  const getRangeKey = (start: number, end: number) => `${start}-${end}`

  // Check if data is available in cache
  const isDataCached = (index: number): boolean => {
    return cache.value.has(index)
  }

  // Get data from cache
  const getCachedData = (index: number): T | null => {
    const entry = cache.value.get(index)
    if (entry) {
      entry.lastAccessed = Date.now()
      entry.accessCount++
      metrics.value.cacheHits++
      return entry.data
    }
    metrics.value.cacheMisses++
    return null
  }

  // Add data to cache with LRU eviction
  const setCachedData = (index: number, data: T) => {
    // Check if we need to evict items
    if (cache.value.size >= cacheSize.value) {
      evictLeastRecentlyUsed()
    }

    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      accessCount: 1,
      lastAccessed: Date.now()
    }

    cache.value.set(index, entry)

    if (debug.value) {
      console.log(`Cached item ${index}, cache size: ${cache.value.size}`)
    }
  }

  // Evict least recently used items from cache
  const evictLeastRecentlyUsed = () => {
    if (cache.value.size === 0) return

    // Find the entry with the oldest lastAccessed time
    let oldestIndex = -1
    let oldestTime = Infinity

    for (const [index, entry] of cache.value.entries()) {
      if (entry.lastAccessed < oldestTime) {
        oldestTime = entry.lastAccessed
        oldestIndex = index
      }
    }

    if (oldestIndex !== -1) {
      cache.value.delete(oldestIndex)
      if (debug.value) {
        console.log(`Evicted item ${oldestIndex} from cache`)
      }
    }
  }

  // Get data for a specific index, loading if necessary
  const getData = async (index: number): Promise<T | null> => {
    // Check cache first
    const cached = getCachedData(index)
    if (cached) {
      return cached
    }

    // Load the data
    await loadRange(index, index)
    // Get the data directly from cache without incrementing hit counter
    const entry = cache.value.get(index)
    if (entry) {
      entry.lastAccessed = Date.now()
      entry.accessCount++
      return entry.data
    }
    return null
  }

  // Load data for a range of indices
  const loadRange = async (startIndex: number, endIndex: number): Promise<void> => {
    const rangeKey = getRangeKey(startIndex, endIndex)
    
    // Check if this range is already being loaded
    if (loadingRanges.value.has(rangeKey)) {
      if (debug.value) {
        console.log(`Range ${rangeKey} is already loading`)
      }
      return
    }

    // Filter to only load uncached items
    const uncachedIndices: number[] = []
    for (let i = startIndex; i <= endIndex; i++) {
      if (!isDataCached(i)) {
        uncachedIndices.push(i)
      }
    }

    if (uncachedIndices.length === 0) {
      if (debug.value) {
        console.log(`All items in range ${rangeKey} are already cached`)
      }
      return
    }

    // Mark range as loading
    loadingRanges.value.add(rangeKey)
    loadingState.value.isLoading = true
    loadingState.value.loadingRanges.push({ start: startIndex, end: endIndex })
    loadingState.value.error = null

    try {
      metrics.value.loadsTriggered++
      
      if (debug.value) {
        console.log(`Loading range ${rangeKey}, uncached items: ${uncachedIndices.length}`)
      }

      // Load the data
      const data = await options.loadData(startIndex, endIndex)
      
      // Cache the loaded data
      data.forEach((item, offset) => {
        const index = startIndex + offset
        setCachedData(index, item)
      })

      metrics.value.itemsLoaded += data.length

      if (debug.value) {
        console.log(`Loaded ${data.length} items for range ${rangeKey}`)
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load data'
      loadingState.value.error = errorMessage
      
      if (debug.value) {
        console.error(`Failed to load range ${rangeKey}:`, error)
      }
    } finally {
      // Clean up loading state
      loadingRanges.value.delete(rangeKey)
      loadingState.value.loadingRanges = loadingState.value.loadingRanges.filter(
        range => getRangeKey(range.start, range.end) !== rangeKey
      )
      loadingState.value.isLoading = loadingState.value.loadingRanges.length > 0
    }
  }

  // Load visible items with prefetching
  const loadVisibleItems = async (visibleIndices: number[]): Promise<void> => {
    if (visibleIndices.length === 0) return

    const minIndex = Math.min(...visibleIndices)
    const maxIndex = Math.max(...visibleIndices)

    // Calculate prefetch range
    const prefetchStart = Math.max(0, minIndex - prefetchCount.value)
    const prefetchEnd = maxIndex + prefetchCount.value

    // Load the entire range including prefetch
    await loadRange(prefetchStart, prefetchEnd)

    // Track prefetch effectiveness
    for (let i = prefetchStart; i < minIndex; i++) {
      if (isDataCached(i)) {
        metrics.value.prefetchHits++
      }
    }
    for (let i = maxIndex + 1; i <= prefetchEnd; i++) {
      if (isDataCached(i)) {
        metrics.value.prefetchHits++
      }
    }
  }

  // Get multiple items from cache or load them
  const getMultipleData = async (indices: number[]): Promise<(T | null)[]> => {
    const results: (T | null)[] = new Array(indices.length)
    const uncachedIndices: number[] = []

    // First pass: get cached items
    indices.forEach((index, i) => {
      const cached = getCachedData(index)
      if (cached) {
        results[i] = cached
      } else {
        uncachedIndices.push(index)
      }
    })

    // Load uncached items if any
    if (uncachedIndices.length > 0) {
      const minIndex = Math.min(...uncachedIndices)
      const maxIndex = Math.max(...uncachedIndices)
      await loadRange(minIndex, maxIndex)

      // Second pass: get the newly loaded items
      indices.forEach((index, i) => {
        if (!results[i]) {
          results[i] = getCachedData(index)  
        }
      })
    }

    return results
  }

  // Clear cache
  const clearCache = () => {
    cache.value.clear()
    if (debug.value) {
      console.log('Cache cleared')
    }
  }

  // Get cache statistics
  const getCacheStats = () => ({
    size: cache.value.size,
    maxSize: cacheSize.value,
    hitRatio: cacheHitRatio.value,
    metrics: { ...metrics.value }
  })

  // Preload specific items
  const preloadItems = async (indices: number[]): Promise<void> => {
    const uncachedIndices = indices.filter(index => !isDataCached(index))
    
    if (uncachedIndices.length === 0) return

    const minIndex = Math.min(...uncachedIndices)
    const maxIndex = Math.max(...uncachedIndices)
    
    await loadRange(minIndex, maxIndex)
  }

  // Update cache size
  const updateCacheSize = (newSize: number) => {
    cacheSize.value = newSize
    
    // Evict items if cache is now too large
    while (cache.value.size > cacheSize.value) {
      evictLeastRecentlyUsed()
    }
  }

  // Update prefetch count
  const updatePrefetchCount = (newCount: number) => {
    prefetchCount.value = newCount
  }

  return {
    // State
    loadingState,
    cacheHitRatio,
    
    // Methods
    getData,
    getMultipleData,
    loadRange,
    loadVisibleItems,
    preloadItems,
    isDataCached,
    clearCache,
    getCacheStats,
    updateCacheSize,
    updatePrefetchCount,
    
    // Cache access
    cache: computed(() => cache.value),
    metrics: computed(() => metrics.value)
  }
}

// Specialized version for the LifetimeGrid
export interface WeekData {
  weekIndex: number
  hasNotes: boolean
  noteCount?: number
  specialDates?: string[]
  // Add other week-specific data as needed
}

export function useWeekDataLazyLoading(options: {
  loadWeekData: (startWeek: number, endWeek: number) => Promise<WeekData[]>
  prefetchCount?: number
  cacheSize?: number
  debug?: boolean
}) {
  const lazyLoading = useLazyLoading<WeekData>({
    loadData: options.loadWeekData,
    prefetchCount: options.prefetchCount,
    cacheSize: options.cacheSize,
    debug: options.debug
  })

  // Week-specific methods
  const getWeekData = async (weekIndex: number): Promise<WeekData | null> => {
    return lazyLoading.getData(weekIndex)
  }

  const loadWeeksInRange = async (startWeek: number, endWeek: number): Promise<void> => {
    return lazyLoading.loadRange(startWeek, endWeek)
  }

  const loadVisibleWeeks = async (visibleWeekIndices: number[]): Promise<void> => {
    return lazyLoading.loadVisibleItems(visibleWeekIndices)
  }

  const preloadWeeks = async (weekIndices: number[]): Promise<void> => {
    return lazyLoading.preloadItems(weekIndices)
  }

  return {
    ...lazyLoading,
    getWeekData,
    loadWeeksInRange,
    loadVisibleWeeks,
    preloadWeeks
  }
}