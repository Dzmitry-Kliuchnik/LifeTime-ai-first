// API-specific type definitions and utilities
export interface RequestConfig {
  timeout?: number
  retries?: number
  retryDelay?: number
}

export interface PaginatedRequest {
  page?: number
  size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface SearchFilters {
  q?: string
  tags?: string[]
  date_from?: string
  date_to?: string
  is_favorite?: boolean
  is_archived?: boolean
}

export interface ApiEndpoints {
  users: string
  notes: string
  weeks: string
}

export const API_ENDPOINTS: ApiEndpoints = {
  users: '/api/v1/users',
  notes: '/api/v1/notes',
  weeks: '/api/v1/weeks',
}

export const DEFAULT_PAGINATION = {
  page: 1,
  size: 20,
} as const

export const API_TIMEOUTS = {
  default: 10000,
  upload: 30000,
  download: 60000,
} as const
