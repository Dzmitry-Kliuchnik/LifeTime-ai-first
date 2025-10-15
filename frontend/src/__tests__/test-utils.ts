// Test utilities and mock data for LifeTime AI frontend tests
import { vi } from 'vitest'
import type {
  User,
  UserCreate,
  NoteResponse,
  NoteCreate,
  TotalWeeksResponse,
  CurrentWeekResponse,
  WeekSummaryResponse,
  LifeProgressResponse,
} from '@/types'
import { WeekType } from '@/types'

/**
 * Mock user data
 */
export const mockUser: User = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  full_name: 'Test User',
  bio: 'A test user for development',
  date_of_birth: '1990-01-15',
  lifespan: 80,
  theme: 'light',
  font_size: 14,
  is_active: true,
  is_verified: true,
  is_superuser: false,
  is_deleted: false,
  deleted_at: undefined,
  last_login: '2023-12-01T10:00:00Z',
  email_verified_at: '2023-11-01T09:00:00Z',
  created_at: '2023-11-01T08:00:00Z',
  updated_at: '2023-12-01T10:00:00Z',
}

export const mockUserCreate: UserCreate = {
  username: 'newuser',
  email: 'newuser@example.com',
  password: 'securepassword123',
  full_name: 'New User',
  bio: 'A new user account',
  date_of_birth: '1995-06-20',
  lifespan: 85,
  theme: 'dark',
  font_size: 16,
}

/**
 * Mock note data
 */
export const mockNote: NoteResponse = {
  id: 1,
  title: 'Test Note',
  content: 'This is a test note content with some meaningful text.',
  user_id: 1,
  tags: ['test', 'development'],
  week_number: 1800,
  is_favorite: false,
  is_archived: false,
  word_count: 10,
  reading_time: 1,
  created_at: '2023-12-01T10:00:00Z',
  updated_at: '2023-12-01T10:00:00Z',
}

export const mockNoteCreate: NoteCreate = {
  title: 'New Test Note',
  content: 'This is a new test note being created.',
  tags: ['important', 'meeting'],
  week_number: 1801,
  is_favorite: true,
  is_archived: false,
}

export const mockNotes: NoteResponse[] = [
  mockNote,
  {
    ...mockNote,
    id: 2,
    title: 'Another Note',
    content: 'Different content for variety',
    tags: ['work', 'project'],
    week_number: 1799,
    is_favorite: true,
  },
  {
    ...mockNote,
    id: 3,
    title: 'Archived Note',
    content: 'This note is archived',
    tags: ['old'],
    week_number: 1750,
    is_archived: true,
  },
]

/**
 * Mock week calculation data
 */
export const mockTotalWeeksResponse: TotalWeeksResponse = {
  date_of_birth: '1990-01-15',
  lifespan_years: 80,
  total_weeks: 4174,
}

export const mockCurrentWeekResponse: CurrentWeekResponse = {
  date_of_birth: '1990-01-15',
  timezone: 'UTC',
  current_week_index: 1768,
  weeks_lived: 1769,
  current_date: '2023-12-01',
}

export const mockWeekSummaryResponse: WeekSummaryResponse = {
  week_index: 1768,
  week_start: '2023-11-27',
  week_end: '2023-12-03',
  week_type: WeekType.CURRENT,
  age_years: 33,
  age_months: 10,
  age_days: 17,
  days_lived: 12376,
  is_current_week: true,
}

export const mockLifeProgressResponse: LifeProgressResponse = {
  date_of_birth: '1990-01-15',
  timezone: 'UTC',
  lifespan_years: 80,
  total_weeks: 4174,
  current_week_index: 1768,
  weeks_lived: 1769,
  progress_percentage: 42.4,
  age_info: {
    years: 33,
    months: 10,
    days: 17,
  },
  current_date: '2023-12-01',
}

/**
 * Test date constants
 */
export const testDates = {
  birth: new Date('1990-01-15'),
  current: new Date('2023-12-01'),
  future: new Date('2024-12-01'),
  past: new Date('2020-01-01'),
}

/**
 * Mock API responses
 */
export const mockApiResponses = {
  success: <T>(data: T) => ({ data, success: true, message: 'Success' }),
  error: (message: string) => ({
    error: 'API_ERROR',
    message,
    details: 'Mock error for testing',
  }),
}

/**
 * Mock axios instance for testing
 */
export const createMockAxios = () => {
  return {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    create: vi.fn(() => createMockAxios()),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  }
}

/**
 * Helper to create test dates
 */
export const createTestDate = (year: number, month: number, day: number): Date => {
  return new Date(year, month - 1, day) // month is 0-indexed
}

/**
 * Helper to create week calculation test data
 */
export const createWeekCalculationTestData = (
  dateOfBirth: string,
  lifespan: number = 80,
  timezone: string = 'UTC',
) => {
  return {
    weekCalculationRequest: {
      date_of_birth: dateOfBirth,
      lifespan_years: lifespan,
      timezone,
    },
    currentWeekRequest: {
      date_of_birth: dateOfBirth,
      timezone,
    },
    weekSummaryRequest: {
      date_of_birth: dateOfBirth,
      week_index: 1000,
      timezone,
    },
  }
}

/**
 * Mock localStorage for testing
 */
export const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

/**
 * Mock Intl API for timezone testing
 */
export const mockIntl = {
  DateTimeFormat: vi.fn(() => ({
    resolvedOptions: () => ({ timeZone: 'America/New_York' }),
    formatToParts: () => [{ type: 'timeZoneName', value: 'EST' }],
  })),
}

/**
 * Test utilities for async operations
 */
export const testUtils = {
  // Wait for next tick
  nextTick: () => new Promise((resolve) => setTimeout(resolve, 0)),

  // Wait for a specific amount of time
  wait: (ms: number) => new Promise((resolve) => setTimeout(resolve, ms)),

  // Create a promise that resolves with a value
  resolveWith: <T>(value: T, delay = 0) =>
    new Promise<T>((resolve) => setTimeout(() => resolve(value), delay)),

  // Create a promise that rejects with an error
  rejectWith: (error: Error, delay = 0) =>
    new Promise((_, reject) => setTimeout(() => reject(error), delay)),

  // Create a mock function that tracks calls
  createMockFn: <T extends (...args: any[]) => any>(implementation?: T) => vi.fn(implementation),
}

/**
 * Validation helpers for tests
 */
export const testValidation = {
  // Check if a date string is in ISO format
  isISODate: (dateStr: string): boolean => {
    const isoRegex = /^\d{4}-\d{2}-\d{2}$/
    return isoRegex.test(dateStr)
  },

  // Check if an object has all required properties
  hasRequiredProps: (obj: Record<string, unknown>, props: string[]): boolean => {
    return props.every((prop) => prop in obj && obj[prop] !== undefined)
  },

  // Check if a number is within a range
  isInRange: (value: number, min: number, max: number): boolean => {
    return value >= min && value <= max
  },
}

/**
 * Setup function for tests
 */
export const setupTest = () => {
  // Mock global objects
  Object.defineProperty(window, 'localStorage', {
    value: mockLocalStorage,
    writable: true,
  })

  // Mock Intl API
  Object.defineProperty(global, 'Intl', {
    value: mockIntl,
    writable: true,
  })

  // Reset all mocks before each test
  vi.clearAllMocks()
}

/**
 * Cleanup function for tests
 */
export const cleanupTest = () => {
  vi.clearAllMocks()
  vi.restoreAllMocks()
}
