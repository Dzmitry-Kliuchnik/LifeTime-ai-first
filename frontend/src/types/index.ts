// Global type definitions
export interface ApiResponse<T = unknown> {
  data: T
  message?: string
  success: boolean
}

export interface User {
  id: number
  username: string
  email: string
  created_at: string
  updated_at: string
}

export interface Note {
  id: number
  title: string
  content: string
  user_id: number
  created_at: string
  updated_at: string
}

// Common types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

export interface RouteParams {
  [key: string]: string
}