// Final minimal store tests (clean reset)
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '../../stores/user'
import { useNotesStore } from '../../stores/notes'
import { useWeekCalculationStore } from '../../stores/week-calculation'

vi.mock('../../utils/api', () => ({
  userApi: { getUser: vi.fn().mockResolvedValue(null) },
  notesApi: { listNotes: vi.fn().mockResolvedValue({ notes: [], total_count: 0 }) },
  weekCalculationApi: {
    getLifeProgress: vi.fn().mockResolvedValue({
      total_weeks: 4160,
      current_week_index: 1500,
      completion_percentage: 36.06,
    }),
  },
  apiUtils: { isApiError: () => false },
}))

beforeEach(() => setActivePinia(createPinia()))

describe('User Store', () => {
  it('default state', () => {
    const s = useUserStore()
    // Store exposes currentUser (not user) initialized to null
    expect(s.currentUser).toBeNull()
  })
})

describe('Notes Store', () => {
  it('default state', () => {
    const s = useNotesStore()
    expect(s.notes).toEqual([])
  })
})

describe('Week Calculation Store', () => {
  it('default state', () => {
    const s = useWeekCalculationStore()
    expect(s.lifeProgress).toBeNull()
  })
})

// EOF
