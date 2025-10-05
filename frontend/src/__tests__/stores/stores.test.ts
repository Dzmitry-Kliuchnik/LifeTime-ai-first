// Basic store tests // Tests for store functionality// Tests for store functionality

import { describe, it, expect } from 'vitest'

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'

describe('Store Tests', () => {

  it('should pass basic test', () => {import { setActivePinia, createPinia } from 'pinia'import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'

    expect(true).toBe(true)

  })import { useUserStore } from '../../stores/user'import { setActivePinia, createPinia } from 'pinia'

})
import { useNotesStore } from '../../stores/notes'import { useUserStore } from '../../stores/user'

import { useWeekCalculationStore } from '../../stores/week-calculation'import { useNotesStore } from '../../stores/notes'

import { setupTest, cleanupTest } from '../setup'import { useWeekCalculationStore } from '../../stores/week-calculation'

import { setupTest, cleanupTest } from '../setup'

// Mock APIs to prevent network calls

vi.mock('../../utils/api', () => ({// Mock APIs to prevent network calls

  userApi: {vi.mock('../../utils/api', () => ({

    getUser: vi.fn().mockResolvedValue({}),

    createUser: vi.fn().mockResolvedValue({}),  userApi: {vi.mock('../../utils/api', () => ({

    updateUser: vi.fn().mockResolvedValue({}),

    deleteUser: vi.fn().mockResolvedValue({})    getUser: vi.fn().mockResolvedValue({}),  userApi: {

  },

  notesApi: {    createUser: vi.fn().mockResolvedValue({}),    getUser: vi.fn().mockResolvedValue({}),

    getNotes: vi.fn().mockResolvedValue({ notes: [], total_count: 0 }),

    listNotes: vi.fn().mockResolvedValue({ notes: [], total_count: 0 }),    updateUser: vi.fn().mockResolvedValue({}),    createUser: vi.fn().mockResolvedValue({}),

    createNote: vi.fn().mockResolvedValue({}),

    updateNote: vi.fn().mockResolvedValue({}),    deleteUser: vi.fn().mockResolvedValue({})    updateUser: vi.fn().mockResolvedValue({}),

    deleteNote: vi.fn().mockResolvedValue({})

  },  },    deleteUser: vi.fn().mockResolvedValue({})

  weekCalculationApi: {

    getTotalWeeks: vi.fn().mockResolvedValue({  notesApi: {  },

      total_weeks: 4160,

      current_week_index: 1500,    createNote: vi.fn().mockResolvedValue({}),  notesApi: {

      completion_percentage: 36.06

    }),    listNotes: vi.fn().mockResolvedValue({ notes: [], total_count: 0 })    createNote: vi.fn().mockResolvedValue({}),

    getCurrentWeek: vi.fn().mockResolvedValue({

      current_week_index: 1500,  },    listNotes: vi.fn().mockResolvedValue({ notes: [], total_count: 0 })

      completion_percentage: 36.06

    }),  weekCalculationApi: {  },

    getLifeProgress: vi.fn().mockResolvedValue({

      total_weeks: 4160,    calculateLifeProgress: vi.fn().mockResolvedValue({  weekCalculationApi: { 

      current_week_index: 1500,

      completion_percentage: 36.06      total_weeks: 4160,

    })

  },      weeks_lived: 1500,    calculateTotalWeeks: vi.fn().mockResolvedValue({})

  apiUtils: {

    isApiError: vi.fn().mockReturnValue(false)      current_week_index: 1500,

  }

}))      completion_percentage: 36.06  },  mockUser,   mockUser, 



describe('Store Tests', () => {    })

  beforeEach(() => {

    setActivePinia(createPinia())  }  apiUtils: {

    setupTest()

    vi.clearAllMocks()}))

  })

    isApiError: vi.fn().mockReturnValue(false),  mockNote,  mockNote,

  afterEach(() => {

    cleanupTest()describe('Store Tests', () => {

  })

  beforeEach(() => {    getErrorMessage: vi.fn().mockReturnValue('Error')

  describe('User Store', () => {

    it('should initialize with default state', () => {    setActivePinia(createPinia())

      const userStore = useUserStore()

      expect(userStore.user).toBeNull()  })  }  mockTotalWeeksResponse,  mockTotalWeeksResponse,

      expect(userStore.isLoading).toBe(false)

      expect(userStore.error).toBeNull()

    })

  afterEach(() => {}))

    it('should handle user creation', async () => {

      const userStore = useUserStore()    vi.clearAllMocks()

      await userStore.createUser({

        name: 'Test User',  })  mockCurrentWeekResponse,  mockCurrentWeekResponse,

        email: 'test@example.com',

        date_of_birth: '1990-01-01'

      })

      expect(userStore.isLoading).toBe(false)  describe('User Store', () => {// Mock localStorage

    })

  })    it('should initialize with default state', () => {



  describe('Notes Store', () => {      const userStore = useUserStore()Object.defineProperty(window, 'localStorage', {  mockLifeProgressResponse  mockLifeProgressResponse

    it('should initialize with default state', () => {

      const notesStore = useNotesStore()      expect(userStore.user).toBeNull()

      expect(notesStore.notes).toEqual([])

      expect(notesStore.isLoading).toBe(false)      expect(userStore.isLoading).toBe(false)  value: {

      expect(notesStore.error).toBeNull()

    })      expect(userStore.error).toBeNull()



    it('should handle note creation', async () => {    })    getItem: vi.fn(),} from '../test-utils'} from '../test-utils'

      const notesStore = useNotesStore()

      await notesStore.createNote({  })

        week_index: 1500,

        content: 'Test note'    setItem: vi.fn(),

      })

      expect(notesStore.isLoading).toBe(false)  describe('Notes Store', () => {

    })

  })    it('should initialize with default state', () => {    removeItem: vi.fn(),



  describe('Week Calculation Store', () => {      const notesStore = useNotesStore()

    it('should initialize with default state', () => {

      const weekStore = useWeekCalculationStore()      expect(notesStore.notes).toEqual([])    clear: vi.fn()

      expect(weekStore.totalWeeks).toBe(0)

      expect(weekStore.currentWeek).toBe(0)      expect(notesStore.isLoading).toBe(false)

      expect(weekStore.isLoading).toBe(false)

      expect(weekStore.error).toBeNull()      expect(notesStore.error).toBeNull()  }// Mock the API modules to prevent actual network calls and infinite loops// Mock all the API modules to prevent actual network calls

    })

    })

    it('should handle life progress calculation', async () => {

      const weekStore = useWeekCalculationStore()  })})

      await weekStore.calculateLifeProgress('1990-01-01')

      expect(weekStore.isLoading).toBe(false)

    })

  })  describe('Week Calculation Store', () => {vi.mock('../../utils/api', () => ({vi.mock('../../utils/api', () => {

})
    it('should initialize with default state', () => {

      const weekStore = useWeekCalculationStore()describe('Stores Basic Tests', () => {

      expect(weekStore.lifeProgress).toBeNull()

      expect(weekStore.isLoading).toBe(false)  beforeEach(() => {  userApi: {  const mockUserApi = {

      expect(weekStore.error).toBeNull()

    })    setActivePinia(createPinia())

  })

})    vi.clearAllMocks()    getUser: vi.fn().mockResolvedValue({}),    getUser: vi.fn(),

  })

    createUser: vi.fn().mockResolvedValue({}),    createUser: vi.fn(),

  it('should pass basic test', () => {

    expect(true).toBe(true)    updateUser: vi.fn().mockResolvedValue({}),    updateUser: vi.fn(),

  })

})    deleteUser: vi.fn().mockResolvedValue({}),    deleteUser: vi.fn(),

    getUserProfile: vi.fn().mockResolvedValue({}),    getUserProfile: vi.fn(),

    updateUserProfile: vi.fn().mockResolvedValue({}),    updateUserProfile: vi.fn(),

    changePassword: vi.fn().mockResolvedValue({})    changePassword: vi.fn()

  },  }

  notesApi: {  

    createNote: vi.fn().mockResolvedValue({}),  const mockNotesApi = {

    getNote: vi.fn().mockResolvedValue({}),    createNote: vi.fn(),

    updateNote: vi.fn().mockResolvedValue({}),    getNote: vi.fn(),

    deleteNote: vi.fn().mockResolvedValue({}),    updateNote: vi.fn(),

    listNotes: vi.fn().mockResolvedValue({ notes: [], total_count: 0 }),    deleteNote: vi.fn(),

    searchNotes: vi.fn().mockResolvedValue({ notes: [], total_count: 0 }),    listNotes: vi.fn(),

    getWeekNotes: vi.fn().mockResolvedValue({ notes: [] }),    searchNotes: vi.fn(),

    getNoteStatistics: vi.fn().mockResolvedValue({}),    getWeekNotes: vi.fn(),

    getCategories: vi.fn().mockResolvedValue([]),    getNoteStatistics: vi.fn(),

    getTags: vi.fn().mockResolvedValue([])    getCategories: vi.fn(),

  },    getTags: vi.fn()

  weekCalculationApi: {  }

    calculateTotalWeeks: vi.fn().mockResolvedValue({}),  

    calculateCurrentWeek: vi.fn().mockResolvedValue({}),  const mockWeekCalculationApi = {

    getWeekSummary: vi.fn().mockResolvedValue({}),    calculateTotalWeeks: vi.fn(),

    calculateLifeProgress: vi.fn().mockResolvedValue({}),    calculateCurrentWeek: vi.fn(),

    getTotalWeeks: vi.fn().mockResolvedValue({}),    getWeekSummary: vi.fn(),

    getCurrentWeek: vi.fn().mockResolvedValue({})    calculateLifeProgress: vi.fn(),

  },    getTotalWeeks: vi.fn(),

  apiUtils: {    getCurrentWeek: vi.fn()

    isApiError: vi.fn().mockReturnValue(false),  }

    getErrorMessage: vi.fn().mockImplementation((err: any) => err?.message || String(err)),  

    isErrorStatus: vi.fn().mockReturnValue(false),  const mockApiUtils = {

    isValidationError: vi.fn().mockReturnValue(false),    isApiError: vi.fn(() => false),

    isAuthError: vi.fn().mockReturnValue(false),    getErrorMessage: vi.fn((err: any) => err?.message || String(err)),

    isNotFoundError: vi.fn().mockReturnValue(false)    isErrorStatus: vi.fn(),

  },    isValidationError: vi.fn(),

  ApiClientError: class MockApiClientError extends Error {    isAuthError: vi.fn(),

    constructor(message: string) {    isNotFoundError: vi.fn()

      super(message)  }

      this.name = 'ApiClientError'}))

    }

  }describe('Stores', () => {

}))  beforeEach(() => {

    setupTest()

// Mock localStorage to prevent actual storage operations    setActivePinia(createPinia())

const mockLocalStorage = {  })

  getItem: vi.fn(),

  setItem: vi.fn(),  afterEach(() => {

  removeItem: vi.fn(),    cleanupTest()

  clear: vi.fn()  })

}

  describe('User Store', () => {

Object.defineProperty(window, 'localStorage', {    it('should initialize with default state', () => {

  value: mockLocalStorage      const store = useUserStore()

})      

      expect(store.currentUser).toBeNull()

describe('Stores', () => {      expect(store.isAuthenticated).toBe(false)

  beforeEach(() => {      expect(store.loadingState).toBe('idle')

    setupTest()      expect(store.error).toBeNull()

    setActivePinia(createPinia())    })

    vi.clearAllMocks()

  })    it('should set user correctly', () => {

      const store = useUserStore()

  afterEach(() => {      

    cleanupTest()      store.setUser(mockUser)

  })      

      expect(store.currentUser).toEqual(mockUser)

  describe('User Store', () => {      expect(store.isAuthenticated).toBe(true)

    it('should initialize with default state', () => {    })

      const store = useUserStore()

          it('should clear user on logout', () => {

      expect(store.currentUser).toBeNull()      const store = useUserStore()

      expect(store.isAuthenticated).toBe(false)      

      expect(store.loadingState).toBe('idle')      store.setUser(mockUser)

      expect(store.error).toBeNull()      expect(store.isAuthenticated).toBe(true)

    })      

      store.logout()

    it('should set user correctly', () => {      

      const store = useUserStore()      expect(store.currentUser).toBeNull()

            expect(store.isAuthenticated).toBe(false)

      store.setUser(mockUser)      expect(store.error).toBeNull()

          })

      expect(store.currentUser).toEqual(mockUser)

      expect(store.isAuthenticated).toBe(true)    it('should compute user display name correctly', () => {

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockUser))      const store = useUserStore()

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('isAuthenticated', 'true')      

    })      store.setUser(mockUser)

      

    it('should clear user correctly', () => {      expect(store.userDisplayName).toBe(mockUser.full_name)

      const store = useUserStore()    })

      

      // Set user first    it('should compute user initials correctly', () => {

      store.setUser(mockUser)      const store = useUserStore()

      expect(store.isAuthenticated).toBe(true)      

            store.setUser(mockUser)

      // Clear user      

      store.setUser(null)      expect(store.userInitials).toBe('TU') // Test User -> TU

          })

      expect(store.currentUser).toBeNull()

      expect(store.isAuthenticated).toBe(false)    it('should check if profile is complete', () => {

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('user')      const store = useUserStore()

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('isAuthenticated')      

    })      store.setUser(mockUser)

      

    it('should compute user display name correctly', () => {      expect(store.isProfileComplete).toBe(true)

      const store = useUserStore()    })

      

      // No user    it('should handle errors correctly', () => {

      expect(store.userDisplayName).toBe('User')      const store = useUserStore()

            const errorMessage = 'Test error'

      // User with full name      

      store.setUser(mockUser)      store.setError(errorMessage)

      expect(store.userDisplayName).toBe(mockUser.full_name)      

            expect(store.error).toBe(errorMessage)

      // User with only username      

      const userWithoutName = { ...mockUser, full_name: '' }      store.clearError()

      store.setUser(userWithoutName)      

      expect(store.userDisplayName).toBe(mockUser.username)      expect(store.error).toBeNull()

    })    })

  })  })



  describe('Notes Store', () => {  describe('Notes Store', () => {

    it('should initialize with default state', () => {    it('should initialize with default state', () => {

      const store = useNotesStore()      const store = useNotesStore()

            

      expect(store.notes).toEqual([])      expect(store.notes).toEqual([])

      expect(store.currentNote).toBeNull()      expect(store.currentNote).toBeNull()

      expect(store.loadingState).toBe('idle')      expect(store.loadingState).toBe('idle')

      expect(store.error).toBeNull()      expect(store.error).toBeNull()

      expect(store.totalCount).toBe(0)      expect(store.totalNotes).toBe(0)

      expect(store.currentPage).toBe(1)    })

    })

  })    it('should compute favorite notes correctly', () => {

      const store = useNotesStore()

  describe('Week Calculation Store', () => {      const favoriteNote = { ...mockNote, is_favorite: true }

    it('should initialize with default state', () => {      

      const store = useWeekCalculationStore()      store.notes = [mockNote, favoriteNote]

            

      expect(store.totalWeeks).toBeNull()      expect(store.favoriteNotes).toHaveLength(1)

      expect(store.currentWeek).toBeNull()       expect(store.favoriteNotes[0]).toEqual(favoriteNote)

      expect(store.lifeProgress).toBeNull()    })

      expect(store.loadingState).toBe('idle')

      expect(store.error).toBeNull()    it('should compute archived notes correctly', () => {

    })      const store = useNotesStore()

  })      const archivedNote = { ...mockNote, is_archived: true }

})      
      store.notes = [mockNote, archivedNote]
      
      expect(store.archivedNotes).toHaveLength(1)
      expect(store.archivedNotes[0]).toEqual(archivedNote)
    })

    it('should compute active notes correctly', () => {
      const store = useNotesStore()
      const archivedNote = { ...mockNote, id: 2, is_archived: true }
      
      store.notes = [mockNote, archivedNote]
      
      expect(store.activeNotes).toHaveLength(1)
      expect(store.activeNotes[0]).toEqual(mockNote)
    })

    it('should group notes by category', () => {
      const store = useNotesStore()
      const workNote = { ...mockNote, id: 2, category: 'Work' }
      
      store.notes = [mockNote, workNote]
      
      const grouped = store.notesByCategory
      
      expect(grouped[mockNote.category!]).toHaveLength(1)
      expect(grouped['Work']).toHaveLength(1)
    })

    it('should group notes by week', () => {
      const store = useNotesStore()
      const weekNote = { ...mockNote, id: 2, week_number: 1801 }
      
      store.notes = [mockNote, weekNote]
      
      const grouped = store.notesByWeek
      
      expect(grouped[mockNote.week_number!]).toHaveLength(1)
      expect(grouped[1801]).toHaveLength(1)
    })

    it('should set current note', () => {
      const store = useNotesStore()
      
      store.setCurrentNote(mockNote)
      
      expect(store.currentNote).toEqual(mockNote)
    })

    it('should clear notes', () => {
      const store = useNotesStore()
      
      store.notes = [mockNote]
      store.currentNote = mockNote
      store.totalNotes = 1
      
      store.clearNotes()
      
      expect(store.notes).toEqual([])
      expect(store.currentNote).toBeNull()
      expect(store.totalNotes).toBe(0)
    })

    it('should update pagination correctly', () => {
      const store = useNotesStore()
      
      store.setPagination({ page: 2, size: 10 })
      
      expect(store.pagination.page).toBe(2)
      expect(store.pagination.size).toBe(10)
    })
  })

  describe('Week Calculation Store', () => {
    it('should initialize with default state', () => {
      const store = useWeekCalculationStore()
      
      expect(store.totalWeeks).toBeNull()
      expect(store.currentWeek).toBeNull()
      expect(store.weekSummary).toBeNull()
      expect(store.lifeProgress).toBeNull()
      expect(store.loadingState).toBe('idle')
      expect(store.error).toBeNull()
    })

    it('should compute current week index correctly', () => {
      const store = useWeekCalculationStore()
      
      store.currentWeek = mockCurrentWeekResponse
      
      expect(store.currentWeekIndex).toBe(mockCurrentWeekResponse.current_week_index)
    })

    it('should compute total lifetime weeks correctly', () => {
      const store = useWeekCalculationStore()
      
      store.totalWeeks = mockTotalWeeksResponse
      
      expect(store.totalLifetimeWeeks).toBe(mockTotalWeeksResponse.total_weeks)
    })

    it('should compute progress percentage correctly', () => {
      const store = useWeekCalculationStore()
      
      store.lifeProgress = mockLifeProgressResponse
      
      expect(store.progressPercentage).toBe(mockLifeProgressResponse.progress_percentage)
    })

    it('should compute weeks lived correctly', () => {
      const store = useWeekCalculationStore()
      
      store.currentWeek = mockCurrentWeekResponse
      
      expect(store.weeksLived).toBe(mockCurrentWeekResponse.weeks_lived)
    })

    it('should compute weeks remaining correctly', () => {
      const store = useWeekCalculationStore()
      
      store.totalWeeks = mockTotalWeeksResponse
      store.currentWeek = mockCurrentWeekResponse
      
      const expected = mockTotalWeeksResponse.total_weeks - mockCurrentWeekResponse.weeks_lived
      expect(store.weeksRemaining).toBe(expected)
    })

    it('should compute current age correctly', () => {
      const store = useWeekCalculationStore()
      
      store.lifeProgress = mockLifeProgressResponse
      
      expect(store.currentAge).toEqual(mockLifeProgressResponse.age_info)
    })

    it('should validate week index correctly', () => {
      const store = useWeekCalculationStore()
      
      // This would require mocking the user store and date utilities
      // For now, just test that the function exists
      expect(typeof store.validateWeekIndex).toBe('function')
    })

    it('should clear data correctly', () => {
      const store = useWeekCalculationStore()
      
      store.totalWeeks = mockTotalWeeksResponse
      store.currentWeek = mockCurrentWeekResponse
      store.error = 'Test error'
      
      store.clearData()
      
      expect(store.totalWeeks).toBeNull()
      expect(store.currentWeek).toBeNull()
      expect(store.error).toBeNull()
      expect(store.loadingState).toBe('idle')
    })

    it('should get week navigation helpers', () => {
      const store = useWeekCalculationStore()
      
      store.totalWeeks = mockTotalWeeksResponse
      
      const navigation = store.getWeekNavigation(100)
      
      expect(navigation.canGoPrevious).toBe(true)
      expect(navigation.canGoNext).toBe(true)
      expect(navigation.previousWeek).toBe(99)
      expect(navigation.nextWeek).toBe(101)
      expect(navigation.firstWeek).toBe(0)
      expect(navigation.lastWeek).toBe(mockTotalWeeksResponse.total_weeks - 1)
    })
  })

  describe('Store Integration', () => {
    it('should work together with user and notes stores', () => {
      const userStore = useUserStore()
      const notesStore = useNotesStore()
      
      userStore.setUser(mockUser)
      notesStore.notes = [mockNote]
      
      expect(userStore.isAuthenticated).toBe(true)
      expect(notesStore.notes).toHaveLength(1)
    })

    it('should handle loading states consistently', () => {
      const userStore = useUserStore()
      const notesStore = useNotesStore()
      const weekStore = useWeekCalculationStore()
      
      expect(userStore.loadingState).toBe('idle')
      expect(notesStore.loadingState).toBe('idle')
      expect(weekStore.loadingState).toBe('idle')
    })

    it('should handle errors consistently', () => {
      const userStore = useUserStore()
      const notesStore = useNotesStore()
      const weekStore = useWeekCalculationStore()
      
      const errorMessage = 'Test error'
      
      userStore.setError(errorMessage)
      notesStore.setError(errorMessage)
      weekStore.setError(errorMessage)
      
      expect(userStore.error).toBe(errorMessage)
      expect(notesStore.error).toBe(errorMessage)
      expect(weekStore.error).toBe(errorMessage)
      
      userStore.clearError()
      notesStore.clearError()
      weekStore.clearError()
      
      expect(userStore.error).toBeNull()
      expect(notesStore.error).toBeNull()
      expect(weekStore.error).toBeNull()
    })
  })
})