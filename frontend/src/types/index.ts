// Global type definitions
export interface ApiResponse<T = unknown> {
  data: T
  message?: string
  success: boolean
}

// Theme types
export type Theme = 'light' | 'dark' | 'auto'

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  bio?: string
  date_of_birth?: string
  lifespan?: number
  theme?: Theme
  font_size?: number
  is_active: boolean
  is_verified: boolean
  is_superuser: boolean
  is_deleted?: boolean
  deleted_at?: string
  last_login?: string
  email_verified_at?: string
  created_at: string
  updated_at: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
  full_name?: string
  bio?: string
  date_of_birth?: string
  lifespan?: number
  theme?: Theme
  font_size?: number
}

export interface UserUpdate {
  username?: string
  email?: string
  full_name?: string
  bio?: string
  date_of_birth?: string
  lifespan?: number
  theme?: Theme
  font_size?: number
  is_active?: boolean
}

export interface UserProfile {
  date_of_birth?: string
  lifespan?: number
  theme?: Theme
  font_size?: number
}

export interface UserSummary {
  id: number
  username: string
  email: string
  full_name?: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface PasswordChange {
  current_password: string
  new_password: string
  confirm_password: string
}

export interface UserStats {
  total_users: number
  active_users: number
  inactive_users: number
  deleted_users: number
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