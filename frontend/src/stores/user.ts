// User store for managing user state and authentication
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  User, 
  UserCreate, 
  UserUpdate, 
  UserProfile, 
  PasswordChange, 
  LoadingState 
} from '@/types'
import { userApi, apiUtils } from '@/utils/api'
import { timezoneUtils } from '@/utils/timezone'

export const useUserStore = defineStore('user', () => {
  // State
  const currentUser = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const loadingState = ref<LoadingState>('idle')
  const error = ref<string | null>(null)
  const userProfile = ref<UserProfile | null>(null)

  // Getters
  const hasDateOfBirth = computed(() => 
    currentUser.value?.date_of_birth != null && currentUser.value.date_of_birth !== ''
  )

  const userLifespan = computed(() => 
    currentUser.value?.lifespan || 80
  )

  const userTimezone = computed(() => {
    // Try to get timezone from user profile or detect automatically
    if (userProfile.value && 'timezone' in userProfile.value) {
      return (userProfile.value as any).timezone as string
    }
    return timezoneUtils.detectUserTimezone()
  })

  const isProfileComplete = computed(() => {
    if (!currentUser.value) return false
    return !!(
      currentUser.value.full_name &&
      currentUser.value.date_of_birth &&
      currentUser.value.lifespan
    )
  })

  const userInitials = computed(() => {
    if (!currentUser.value?.full_name) {
      return currentUser.value?.username?.charAt(0).toUpperCase() || 'U'
    }
    const names = currentUser.value.full_name.split(' ')
    return names.map(name => name.charAt(0).toUpperCase()).join('').slice(0, 2)
  })

  const userDisplayName = computed(() => 
    currentUser.value?.full_name || currentUser.value?.username || 'User'
  )

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

  const setUser = (user: User | null) => {
    currentUser.value = user
    isAuthenticated.value = !!user
    
    // Store user info in localStorage for persistence
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('isAuthenticated', 'true')
    } else {
      localStorage.removeItem('user')
      localStorage.removeItem('isAuthenticated')
    }
  }

  const loadUserFromStorage = () => {
    try {
      const storedUser = localStorage.getItem('user')
      const storedAuth = localStorage.getItem('isAuthenticated')
      
      if (storedUser && storedAuth === 'true') {
        const user = JSON.parse(storedUser) as User
        currentUser.value = user
        isAuthenticated.value = true
        return user
      }
    } catch (error) {
      console.warn('Failed to load user from localStorage:', error)
      // Clear potentially corrupted data
      localStorage.removeItem('user')
      localStorage.removeItem('isAuthenticated')
    }
    return null
  }

  const fetchUser = async (userId: number): Promise<User | null> => {
    try {
      setLoadingState('loading')
      clearError()
      
      const user = await userApi.getUser(userId)
      setUser(user)
      
      setLoadingState('success')
      return user
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to fetch user: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const createUser = async (userData: UserCreate): Promise<User | null> => {
    try {
      setLoadingState('loading')
      clearError()
      
      const user = await userApi.createUser(userData)
      setUser(user)
      
      setLoadingState('success')
      return user
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to create user: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const updateUser = async (userData: UserUpdate): Promise<User | null> => {
    if (!currentUser.value) {
      setError('No current user to update')
      return null
    }

    try {
      setLoadingState('loading')
      clearError()
      
      const updatedUser = await userApi.updateUser(currentUser.value.id, userData)
      setUser(updatedUser)
      
      setLoadingState('success')
      return updatedUser
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to update user: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const deleteUser = async (): Promise<boolean> => {
    if (!currentUser.value) {
      setError('No current user to delete')
      return false
    }

    try {
      setLoadingState('loading')
      clearError()
      
      await userApi.deleteUser(currentUser.value.id)
      logout()
      
      setLoadingState('success')
      return true
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to delete user: ${errorMessage}`)
      setLoadingState('error')
      return false
    }
  }

  const fetchUserProfile = async (): Promise<UserProfile | null> => {
    if (!currentUser.value) {
      setError('No current user')
      return null
    }

    try {
      setLoadingState('loading')
      clearError()
      
      const profile = await userApi.getUserProfile(currentUser.value.id)
      userProfile.value = profile
      
      setLoadingState('success')
      return profile
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to fetch user profile: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const updateUserProfile = async (profileData: UserProfile): Promise<UserProfile | null> => {
    if (!currentUser.value) {
      setError('No current user')
      return null
    }

    try {
      setLoadingState('loading')
      clearError()
      
      const updatedProfile = await userApi.updateUserProfile(currentUser.value.id, profileData)
      userProfile.value = updatedProfile
      
      // Also update relevant fields in current user
      if (currentUser.value) {
        currentUser.value = {
          ...currentUser.value,
          date_of_birth: updatedProfile.date_of_birth || currentUser.value.date_of_birth,
          lifespan: updatedProfile.lifespan || currentUser.value.lifespan,
          theme: updatedProfile.theme || currentUser.value.theme,
          font_size: updatedProfile.font_size || currentUser.value.font_size,
        }
        // Update localStorage
        localStorage.setItem('user', JSON.stringify(currentUser.value))
      }
      
      setLoadingState('success')
      return updatedProfile
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to update user profile: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const changePassword = async (passwordData: PasswordChange): Promise<boolean> => {
    if (!currentUser.value) {
      setError('No current user')
      return false
    }

    try {
      setLoadingState('loading')
      clearError()
      
      await userApi.changePassword(currentUser.value.id, passwordData)
      
      setLoadingState('success')
      return true
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to change password: ${errorMessage}`)
      setLoadingState('error')
      return false
    }
  }

  const login = async (username: string, password: string): Promise<boolean> => {
    // This would typically call an authentication endpoint
    // For now, we'll simulate the login process
    try {
      setLoadingState('loading')
      clearError()
      
      // In a real app, you would call an auth endpoint here
      // const response = await authApi.login({ username, password })
      // const { user, token } = response
      
      // For simulation purposes, we'll just set a dummy user
      // You should replace this with actual authentication logic
      
      setLoadingState('success')
      return true
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to login: ${errorMessage}`)
      setLoadingState('error')
      return false
    }
  }

  const logout = () => {
    setUser(null)
    userProfile.value = null
    clearError()
    setLoadingState('idle')
    
    // Clear auth token
    localStorage.removeItem('auth_token')
    
    // Dispatch logout event
    window.dispatchEvent(new CustomEvent('auth:logout'))
  }

  const initialize = async () => {
    // Try to load user from localStorage on app startup
    const storedUser = loadUserFromStorage()
    
    if (storedUser) {
      // Optionally verify the stored user is still valid
      // await fetchUser(storedUser.id)
      
      // Load user profile if user exists
      await fetchUserProfile()
    }
  }

  // Listen for auth logout events (from API interceptor)
  if (typeof window !== 'undefined') {
    window.addEventListener('auth:logout', logout)
  }

  return {
    // State
    currentUser,
    isAuthenticated,
    loadingState,
    error,
    userProfile,
    
    // Getters
    hasDateOfBirth,
    userLifespan,
    userTimezone,
    isProfileComplete,
    userInitials,
    userDisplayName,
    
    // Actions
    setUser,
    loadUserFromStorage,
    fetchUser,
    createUser,
    updateUser,
    deleteUser,
    fetchUserProfile,
    updateUserProfile,
    changePassword,
    login,
    logout,
    initialize,
    clearError,
    setError,
  }
})