// Week calculation store for managing life week calculations and progress
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  WeekCalculationRequest,
  CurrentWeekRequest,
  WeekSummaryRequest,
  TotalWeeksResponse,
  CurrentWeekResponse,
  WeekSummaryResponse,
  LifeProgressResponse,
  LoadingState
} from '@/types'
import { WeekType } from '@/types'
import { weekCalculationApi, apiUtils } from '@/utils/api'
import { dateUtils } from '@/utils/date'
import { timezoneUtils } from '@/utils/timezone'
import { useUserStore } from './user'

export const useWeekCalculationStore = defineStore('weekCalculation', () => {
  // State
  const totalWeeks = ref<TotalWeeksResponse | null>(null)
  const currentWeek = ref<CurrentWeekResponse | null>(null)
  const weekSummary = ref<WeekSummaryResponse | null>(null)
  const lifeProgress = ref<LifeProgressResponse | null>(null)
  const weekSummaries = ref<Map<number, WeekSummaryResponse>>(new Map())
  const loadingState = ref<LoadingState>('idle')
  const error = ref<string | null>(null)

  // Cache for calculations to avoid repeated API calls
  const calculationCache = ref<Map<string, unknown>>(new Map())

  // Getters
  const currentWeekIndex = computed(() => 
    currentWeek.value?.current_week_index ?? null
  )

  const totalLifetimeWeeks = computed(() => 
    totalWeeks.value?.total_weeks ?? null
  )

  const progressPercentage = computed(() => 
    lifeProgress.value?.progress_percentage ?? null
  )

  const weeksLived = computed(() => 
    currentWeek.value?.weeks_lived ?? null
  )

  const weeksRemaining = computed(() => {
    const total = totalLifetimeWeeks.value
    const lived = weeksLived.value
    return (total && lived) ? Math.max(0, total - lived) : null
  })

  const currentAge = computed(() => 
    lifeProgress.value?.age_info ?? null
  )

  const isLoading = computed(() => loadingState.value === 'loading')
  const hasError = computed(() => loadingState.value === 'error')

  // Helper function to generate cache keys
  const generateCacheKey = (type: string, params: Record<string, unknown>): string => {
    return `${type}:${JSON.stringify(params)}`
  }

  // Actions
  const setLoadingState = (state: LoadingState) => {
    loadingState.value = state
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const clearError = () => {
    error.value = null
  }

  const getDefaultCalculationRequest = (): WeekCalculationRequest | null => {
    const userStore = useUserStore()
    const user = userStore.currentUser
    
    if (!user?.date_of_birth) {
      return null
    }

    return {
      date_of_birth: user.date_of_birth,
      lifespan_years: user.lifespan || 80,
      timezone: userStore.userTimezone
    }
  }

  const calculateTotalWeeks = async (
    request?: WeekCalculationRequest
  ): Promise<TotalWeeksResponse | null> => {
    const requestData = request || getDefaultCalculationRequest()
    if (!requestData) {
      setError('User date of birth is required')
      return null
    }

    const cacheKey = generateCacheKey('totalWeeks', requestData as unknown as Record<string, unknown>)
    const cached = calculationCache.value.get(cacheKey) as TotalWeeksResponse
    if (cached) {
      totalWeeks.value = cached
      return cached
    }

    try {
      setLoadingState('loading')
      clearError()
      
      const response = await weekCalculationApi.calculateTotalWeeks(requestData)
      totalWeeks.value = response
      
      // Cache the result
      calculationCache.value.set(cacheKey, response)
      
      setLoadingState('success')
      return response
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to calculate total weeks: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const calculateCurrentWeek = async (
    request?: CurrentWeekRequest
  ): Promise<CurrentWeekResponse | null> => {
    const userStore = useUserStore()
    const requestData = request || {
      date_of_birth: userStore.currentUser?.date_of_birth || '',
      timezone: userStore.userTimezone
    }

    if (!requestData.date_of_birth) {
      setError('User date of birth is required')
      return null
    }

    const cacheKey = generateCacheKey('currentWeek', requestData as unknown as Record<string, unknown>)
    const cached = calculationCache.value.get(cacheKey) as CurrentWeekResponse
    if (cached) {
      currentWeek.value = cached
      return cached
    }

    try {
      setLoadingState('loading')
      clearError()
      
      const response = await weekCalculationApi.calculateCurrentWeek(requestData)
      currentWeek.value = response
      
      // Cache the result (with shorter TTL since it changes daily)
      calculationCache.value.set(cacheKey, response)
      
      setLoadingState('success')
      return response
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to calculate current week: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const getWeekSummary = async (
    weekIndex: number,
    request?: Omit<WeekSummaryRequest, 'week_index'>
  ): Promise<WeekSummaryResponse | null> => {
    const userStore = useUserStore()
    const requestData: WeekSummaryRequest = {
      date_of_birth: userStore.currentUser?.date_of_birth || '',
      timezone: userStore.userTimezone,
      week_index: weekIndex,
      ...request
    }

    if (!requestData.date_of_birth) {
      setError('User date of birth is required')
      return null
    }

    // Check cache first
    const cached = weekSummaries.value.get(weekIndex)
    if (cached) {
      weekSummary.value = cached
      return cached
    }

    try {
      setLoadingState('loading')
      clearError()
      
      const response = await weekCalculationApi.getWeekSummary(requestData)
      weekSummary.value = response
      
      // Cache the result
      weekSummaries.value.set(weekIndex, response)
      
      setLoadingState('success')
      return response
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to get week summary: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const calculateLifeProgress = async (
    request?: WeekCalculationRequest
  ): Promise<LifeProgressResponse | null> => {
    const requestData = request || getDefaultCalculationRequest()
    if (!requestData) {
      setError('User date of birth is required')
      return null
    }

    const cacheKey = generateCacheKey('lifeProgress', requestData as unknown as Record<string, unknown>)
    const cached = calculationCache.value.get(cacheKey) as LifeProgressResponse
    if (cached) {
      lifeProgress.value = cached
      return cached
    }

    try {
      setLoadingState('loading')
      clearError()
      
      const response = await weekCalculationApi.calculateLifeProgress(requestData)
      lifeProgress.value = response
      
      // Cache the result
      calculationCache.value.set(cacheKey, response)
      
      setLoadingState('success')
      return response
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to calculate life progress: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  // Client-side calculation helpers using date utils
  const calculateWeeksSinceBirthLocal = (
    dateOfBirth: string,
    timezone?: string,
    referenceDate?: Date
  ): number => {
    try {
      const dob = dateUtils.parseDate(dateOfBirth)
      
      if (timezone) {
        return timezoneUtils.calculateWeeksSinceBirthInTimezone(dob, timezone, referenceDate)
      }
      
      return dateUtils.calculateWeeksSinceBirth(dob, referenceDate)
    } catch (err) {
      console.error('Failed to calculate weeks since birth locally:', err)
      return 0
    }
  }

  const getWeekTypeLocal = (
    dateOfBirth: string,
    weekIndex: number,
    timezone?: string,
    referenceDate?: Date
  ): WeekType => {
    try {
      const dob = dateUtils.parseDate(dateOfBirth)
      return dateUtils.getWeekType(dob, weekIndex, referenceDate)
    } catch (err) {
      console.error('Failed to get week type locally:', err)
      return WeekType.PAST
    }
  }

  const getWeekDateRangeLocal = (
    dateOfBirth: string,
    weekIndex: number
  ): { start: Date; end: Date } | null => {
    try {
      const dob = dateUtils.parseDate(dateOfBirth)
      return dateUtils.getWeekDateRange(dob, weekIndex)
    } catch (err) {
      console.error('Failed to get week date range locally:', err)
      return null
    }
  }

  // Batch operations
  const getMultipleWeekSummaries = async (
    weekIndices: number[]
  ): Promise<Map<number, WeekSummaryResponse>> => {
    const results = new Map<number, WeekSummaryResponse>()
    
    // Process in parallel with limited concurrency
    const batchSize = 5
    for (let i = 0; i < weekIndices.length; i += batchSize) {
      const batch = weekIndices.slice(i, i + batchSize)
      const promises = batch.map(weekIndex => getWeekSummary(weekIndex))
      
      const batchResults = await Promise.allSettled(promises)
      batchResults.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value) {
          results.set(batch[index]!, result.value)
        }
      })
    }
    
    return results
  }

  // Initialize calculations for current user
  const initializeForUser = async (): Promise<void> => {
    const userStore = useUserStore()
    if (!userStore.currentUser?.date_of_birth) {
      return
    }

    try {
      // Calculate basic information in parallel
      await Promise.all([
        calculateTotalWeeks(),
        calculateCurrentWeek(),
        calculateLifeProgress()
      ])
    } catch (err) {
      console.error('Failed to initialize week calculations:', err)
    }
  }

  // Refresh calculations (invalidate cache)
  const refresh = async (): Promise<void> => {
    calculationCache.value.clear()
    weekSummaries.value.clear()
    await initializeForUser()
  }

  // Clear all data
  const clearData = () => {
    totalWeeks.value = null
    currentWeek.value = null
    weekSummary.value = null
    lifeProgress.value = null
    weekSummaries.value.clear()
    calculationCache.value.clear()
    error.value = null
    loadingState.value = 'idle'
  }

  // Validate week index against current user's range
  const validateWeekIndex = (weekIndex: number): boolean => {
    const userStore = useUserStore()
    if (!userStore.currentUser?.date_of_birth) {
      return false
    }

    try {
      const dob = dateUtils.parseDate(userStore.currentUser.date_of_birth)
      dateUtils.validateWeekIndex(dob, weekIndex, false) // Don't allow future weeks
      return true
    } catch {
      return false
    }
  }

  // Get week navigation helpers
  const getWeekNavigation = (currentWeekIndex: number) => {
    const total = totalLifetimeWeeks.value || 0
    return {
      canGoPrevious: currentWeekIndex > 0,
      canGoNext: currentWeekIndex < total - 1,
      previousWeek: Math.max(0, currentWeekIndex - 1),
      nextWeek: Math.min(total - 1, currentWeekIndex + 1),
      firstWeek: 0,
      lastWeek: total - 1
    }
  }

  return {
    // State
    totalWeeks,
    currentWeek,
    weekSummary,
    lifeProgress,
    weekSummaries,
    loadingState,
    error,
    
    // Getters
    currentWeekIndex,
    totalLifetimeWeeks,
    progressPercentage,
    weeksLived,
    weeksRemaining,
    currentAge,
    isLoading,
    hasError,
    
    // Actions
    calculateTotalWeeks,
    calculateCurrentWeek,
    getWeekSummary,
    calculateLifeProgress,
    
    // Local calculations
    calculateWeeksSinceBirthLocal,
    getWeekTypeLocal,
    getWeekDateRangeLocal,
    
    // Batch operations
    getMultipleWeekSummaries,
    
    // Utilities
    initializeForUser,
    refresh,
    clearData,
    validateWeekIndex,
    getWeekNavigation,
    clearError,
    setError,
  }
})