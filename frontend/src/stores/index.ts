// Main store exports for easy importing
export { useUserStore } from './user'
export { useNotesStore } from './notes'
export { useWeekCalculationStore } from './week-calculation'

// Re-export common types that stores use
export type {
  User,
  UserCreate,
  UserUpdate,
  UserProfile,
  NoteResponse,
  NoteCreate,
  NoteUpdate,
  NoteListResponse,
  WeekCalculationRequest,
  CurrentWeekRequest,
  TotalWeeksResponse,
  CurrentWeekResponse,
  LifeProgressResponse,
  LoadingState,
} from '@/types'
