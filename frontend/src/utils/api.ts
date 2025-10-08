// Enhanced API client for LifeTime AI application
import axios, { type AxiosResponse, type AxiosError } from 'axios'
import type {
  ApiError,
  User,
  UserCreate,
  UserUpdate,
  UserProfile,
  PasswordChange,
  UserStats,
  NoteCreate,
  NoteUpdate,
  NoteResponse,
  NoteSearchRequest,
  NoteListResponse,
  WeekNotesResponse,
  NoteStatistics,
  WeekCalculationRequest,
  CurrentWeekRequest,
  WeekSummaryRequest,
  TotalWeeksResponse,
  CurrentWeekResponse,
  WeekSummaryResponse,
  LifeProgressResponse,
  TotalWeeksQueryParams,
  CurrentWeekQueryParams,
  PaginationParams,
} from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_V1_BASE = '/api/v1'

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
})

// Enhanced error handling
export class ApiClientError extends Error {
  public status?: number
  public code?: string
  public details?: string

  constructor(message: string, status?: number, code?: string, details?: string) {
    super(message)
    this.name = 'ApiClientError'
    this.status = status
    this.code = code
    this.details = details
  }
}

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (_error) => {
    return Promise.reject(new ApiClientError('Request failed', undefined, 'REQUEST_ERROR'))
  },
)

// Response interceptor with enhanced error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      // Dispatch custom event for auth state change
      window.dispatchEvent(new CustomEvent('auth:logout'))
    }

    const apiError = error.response?.data as ApiError
    const status = error.response?.status
    const message = apiError?.message || error.message || 'An error occurred'
    const code = apiError?.error || 'UNKNOWN_ERROR'
    const details = apiError?.details

    return Promise.reject(new ApiClientError(message, status, code, details))
  },
)

// Generic API functions
export async function apiGet<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const response = await api.get<T>(url, { params })
  return response.data
}

export async function apiPost<T>(url: string, data?: unknown): Promise<T> {
  const response = await api.post<T>(url, data)
  return response.data
}

export async function apiPut<T>(url: string, data?: unknown): Promise<T> {
  const response = await api.put<T>(url, data)
  return response.data
}

export async function apiPatch<T>(url: string, data?: unknown): Promise<T> {
  const response = await api.patch<T>(url, data)
  return response.data
}

export async function apiDelete<T>(url: string): Promise<T> {
  const response = await api.delete<T>(url)
  return response.data
}

// User API
export const userApi = {
  // Get user by ID
  getUser: (id: number): Promise<User> => apiGet<User>(`${API_V1_BASE}/users/${id}`),

  // Create new user
  createUser: (userData: UserCreate): Promise<User> =>
    apiPost<User>(`${API_V1_BASE}/users/`, userData),

  // Update user
  updateUser: (id: number, userData: UserUpdate): Promise<User> =>
    apiPut<User>(`${API_V1_BASE}/users/${id}`, userData),

  // Delete user (soft delete)
  deleteUser: (id: number): Promise<{ message: string }> =>
    apiDelete<{ message: string }>(`${API_V1_BASE}/users/${id}`),

  // Get user profile
  getUserProfile: (id: number): Promise<UserProfile> =>
    apiGet<UserProfile>(`${API_V1_BASE}/users/${id}/profile`),

  // Update user profile
  updateUserProfile: (id: number, profileData: UserProfile): Promise<UserProfile> =>
    apiPut<UserProfile>(`${API_V1_BASE}/users/${id}/profile`, profileData),

  // Change password
  changePassword: (id: number, passwordData: PasswordChange): Promise<{ message: string }> =>
    apiPost<{ message: string }>(`${API_V1_BASE}/users/${id}/change-password`, passwordData),

  // Get user statistics (admin only)
  getUserStats: (): Promise<UserStats> => apiGet<UserStats>(`${API_V1_BASE}/users/stats`),
}

// Notes API
export const notesApi = {
  // Create note
  createNote: (userId: number, noteData: NoteCreate): Promise<NoteResponse> =>
    apiPost<NoteResponse>(`${API_V1_BASE}/notes/?user_id=${userId}`, noteData),

  // Get note by ID
  getNote: (noteId: number, userId: number): Promise<NoteResponse> =>
    apiGet<NoteResponse>(`${API_V1_BASE}/notes/${noteId}`, { user_id: userId }),

  // Update note
  updateNote: (noteId: number, userId: number, noteData: NoteUpdate): Promise<NoteResponse> =>
    apiPut<NoteResponse>(`${API_V1_BASE}/notes/${noteId}?user_id=${userId}`, noteData),

  // Delete note
  deleteNote: (noteId: number, userId: number): Promise<{ message: string }> =>
    apiDelete<{ message: string }>(`${API_V1_BASE}/notes/${noteId}?user_id=${userId}`),

  // List notes with pagination and filtering
  listNotes: (
    userId: number,
    pagination?: PaginationParams,
    filters?: NoteSearchRequest,
  ): Promise<NoteListResponse> => {
    const params = { user_id: userId, ...pagination, ...filters }
    return apiGet<NoteListResponse>(`${API_V1_BASE}/notes/`, params)
  },

  // Search notes
  searchNotes: (userId: number, searchData: NoteSearchRequest): Promise<NoteListResponse> =>
    apiPost<NoteListResponse>(`${API_V1_BASE}/notes/search?user_id=${userId}`, searchData),

  // Get notes for specific week
  getWeekNotes: (userId: number, weekNumber: number): Promise<WeekNotesResponse> =>
    apiGet<WeekNotesResponse>(`${API_V1_BASE}/notes/week/${weekNumber}`, { user_id: userId }),

  // Get note statistics
  getNoteStatistics: (userId: number): Promise<NoteStatistics> =>
    apiGet<NoteStatistics>(`${API_V1_BASE}/notes/stats/summary`, { user_id: userId }),

  // Get available categories
  getCategories: (userId: number): Promise<string[]> =>
    apiGet<string[]>(`${API_V1_BASE}/notes/meta/categories`, { user_id: userId }),

  // Get available tags
  getTags: (userId: number): Promise<string[]> =>
    apiGet<string[]>(`${API_V1_BASE}/notes/meta/tags`, { user_id: userId }),
}

// Week Calculation API
export const weekCalculationApi = {
  // Calculate total weeks in lifespan (POST)
  calculateTotalWeeks: (requestData: WeekCalculationRequest): Promise<TotalWeeksResponse> =>
    apiPost<TotalWeeksResponse>(`${API_V1_BASE}/weeks/total-weeks`, requestData),

  // Calculate total weeks in lifespan (GET)
  getTotalWeeks: (params: TotalWeeksQueryParams): Promise<TotalWeeksResponse> =>
    apiGet<TotalWeeksResponse>(
      `${API_V1_BASE}/weeks/total`,
      params as unknown as Record<string, unknown>,
    ),

  // Quick total weeks calculation using URL parameters
  getQuickTotalWeeks: (dob: string, lifespan: number): Promise<TotalWeeksResponse> =>
    apiGet<TotalWeeksResponse>(`${API_V1_BASE}/weeks/total-weeks/${dob}/${lifespan}`),

  // Calculate current week index (POST)
  calculateCurrentWeek: (requestData: CurrentWeekRequest): Promise<CurrentWeekResponse> =>
    apiPost<CurrentWeekResponse>(`${API_V1_BASE}/weeks/current-week`, requestData),

  // Calculate current week index (GET)
  getCurrentWeek: (params: CurrentWeekQueryParams): Promise<CurrentWeekResponse> =>
    apiGet<CurrentWeekResponse>(
      `${API_V1_BASE}/weeks/current`,
      params as unknown as Record<string, unknown>,
    ),

  // Get week summary
  getWeekSummary: (requestData: WeekSummaryRequest): Promise<WeekSummaryResponse> =>
    apiPost<WeekSummaryResponse>(`${API_V1_BASE}/weeks/week-summary`, requestData),

  // Calculate life progress
  calculateLifeProgress: (requestData: WeekCalculationRequest): Promise<LifeProgressResponse> =>
    apiPost<LifeProgressResponse>(`${API_V1_BASE}/weeks/life-progress`, requestData),
}

// Utility functions for common API operations
export const apiUtils = {
  // Check if error is ApiClientError
  isApiError: (error: unknown): error is ApiClientError => error instanceof ApiClientError,

  // Extract error message from various error types
  getErrorMessage: (error: unknown): string => {
    if (error instanceof ApiClientError) {
      return error.message
    }
    if (error instanceof Error) {
      return error.message
    }
    return String(error)
  },

  // Check if error is a specific status code
  isErrorStatus: (error: unknown, status: number): boolean => {
    return error instanceof ApiClientError && error.status === status
  },

  // Check if error is validation error
  isValidationError: (error: unknown): boolean => {
    return (
      error instanceof ApiClientError && (error.status === 422 || error.code === 'VALIDATION_ERROR')
    )
  },

  // Check if error is authorization error
  isAuthError: (error: unknown): boolean => {
    return error instanceof ApiClientError && (error.status === 401 || error.status === 403)
  },

  // Check if error is not found error
  isNotFoundError: (error: unknown): boolean => {
    return error instanceof ApiClientError && error.status === 404
  },
}

// Export the main api instance for custom requests
export default api
