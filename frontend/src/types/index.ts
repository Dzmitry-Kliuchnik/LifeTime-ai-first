// Global type definitions
export interface ApiResponse<T = unknown> {
  data: T
  message?: string
  success: boolean
}

export interface ApiError {
  error: string
  message: string
  details?: string
}

// Theme types
export type Theme = 'light' | 'dark' | 'auto'

// Week-related types
export enum WeekType {
  PAST = 'past',
  CURRENT = 'current',
  FUTURE = 'future'
}

export interface AgeInfo {
  years: number
  months: number
  days: number
}

// User types (enhanced with week-based functionality)
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

// Note types (enhanced with week-based functionality)
export interface Note {
  id: number
  title: string
  content: string
  user_id: number
  category?: string
  tags?: string[]
  week_number?: number
  is_favorite: boolean
  is_archived: boolean
  word_count?: number
  reading_time?: number
  search_vector?: string
  edit_history?: Record<string, unknown>[]
  created_at: string
  updated_at: string
}

export interface NoteCreate {
  title: string
  content: string
  category?: string
  tags?: string[]
  week_number?: number
  is_favorite?: boolean
  is_archived?: boolean
}

export interface NoteUpdate {
  title?: string
  content?: string
  category?: string
  tags?: string[]
  week_number?: number
  is_favorite?: boolean
  is_archived?: boolean
}

export interface NoteResponse {
  id: number
  title: string
  content: string
  user_id: number
  category?: string
  tags: string[]
  week_number?: number
  is_favorite: boolean
  is_archived: boolean
  word_count: number
  reading_time: number
  created_at: string
  updated_at: string
}

export interface NoteSearchRequest {
  query?: string
  category?: string
  tags?: string[]
  week_number?: number
  is_favorite?: boolean
  is_archived?: boolean
  start_date?: string
  end_date?: string
}

export interface NoteListResponse {
  notes: NoteResponse[]
  total: number
  page: number
  size: number
  has_next: boolean
  has_prev: boolean
}

export interface WeekNotesResponse {
  week_number: number
  week_start_date: string
  week_end_date: string
  notes: NoteResponse[]
  total_notes: number
}

export interface NoteStatistics {
  total_notes: number
  notes_this_week: number
  notes_this_month: number
  favorite_notes: number
  archived_notes: number
  categories: Record<string, number>
  notes_by_week: Record<number, number>
  average_word_count?: number
  total_reading_time?: number
}

// Week Calculation types
export interface WeekCalculationRequest {
  date_of_birth: string
  lifespan_years?: number
  timezone?: string
}

export interface CurrentWeekRequest {
  date_of_birth: string
  timezone?: string
}

export interface WeekSummaryRequest {
  date_of_birth: string
  week_index: number
  timezone?: string
}

export interface TotalWeeksResponse {
  date_of_birth: string
  lifespan_years: number
  total_weeks: number
}

export interface CurrentWeekResponse {
  date_of_birth: string
  timezone: string
  current_week_index: number
  weeks_lived: number
  current_date: string
}

export interface WeekSummaryResponse {
  week_index: number
  week_start: string
  week_end: string
  week_type: WeekType
  age_years: number
  age_months: number
  age_days: number
  days_lived: number
  is_current_week: boolean
}

export interface LifeProgressResponse {
  date_of_birth: string
  timezone: string
  lifespan_years: number
  total_weeks: number
  current_week_index: number
  weeks_lived: number
  progress_percentage: number
  age_info: AgeInfo
  current_date: string
}

export interface TotalWeeksQueryParams {
  date_of_birth: string
  lifespan_years?: number
}

export interface CurrentWeekQueryParams {
  date_of_birth: string
  timezone?: string
}

// Common types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

export interface RouteParams {
  [key: string]: string
}

export interface PaginationParams {
  page?: number
  size?: number
}

export interface DateRange {
  start: string
  end: string
}

export interface TimezoneInfo {
  name: string
  offset: number
  abbreviation: string
}

// Utility types for forms and UI
export interface FormValidation {
  isValid: boolean
  errors: Record<string, string[]>
}

export interface SortOptions {
  field: string
  direction: 'asc' | 'desc'
}

export interface FilterOptions {
  [key: string]: unknown
}