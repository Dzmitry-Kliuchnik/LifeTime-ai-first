import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import NotesList from '../NotesList.vue'
import type { NoteResponse } from '@/types'

// Mock the stores
vi.mock('@/stores/notes', () => ({
  useNotesStore: () => ({
    archiveNote: vi.fn(),
    favoriteNote: vi.fn(),
    unfavoriteNote: vi.fn(),
  }),
}))

vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    currentUser: { id: 1 },
  }),
}))

vi.mock('@/stores/weekCalculation', () => ({
  useWeekCalculationStore: () => ({
    currentWeek: { current_week_index: 42 },
  }),
}))

// Helper function to create mock notes
const createMockNote = (id: number, title: string): NoteResponse => ({
  id,
  title,
  content: `Content for note ${id}`,
  user_id: 1,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  is_archived: false,
  is_favorite: false,
  tags: [],
  word_count: 50,
  reading_time: 1,
})

describe('NotesList Pagination', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  it('should not show pagination when there are 5 or fewer notes', async () => {
    const notes = Array.from({ length: 5 }, (_, i) => createMockNote(i + 1, `Note ${i + 1}`))

    const wrapper = mount(NotesList, {
      props: {
        notes,
        totalNotes: 5,
      },
    })

    // Should not show pagination section
    expect(wrapper.find('.pagination-section').exists()).toBe(false)

    // Should display all 5 notes
    expect(wrapper.findAll('.note-item-wrapper')).toHaveLength(5)
  })

  it('should show pagination when there are more than 5 notes', async () => {
    const notes = Array.from({ length: 12 }, (_, i) => createMockNote(i + 1, `Note ${i + 1}`))

    const wrapper = mount(NotesList, {
      props: {
        notes,
        totalNotes: 12,
      },
    })

    // Should show pagination section
    expect(wrapper.find('.pagination-section').exists()).toBe(true)

    // Should display only first 5 notes on page 1
    expect(wrapper.findAll('.note-item-wrapper')).toHaveLength(5)

    // Should show correct pagination info
    expect(wrapper.find('.pagination-text').text()).toContain('Page 1 of 3')
  })

  it('should navigate to next page correctly', async () => {
    const notes = Array.from({ length: 12 }, (_, i) => createMockNote(i + 1, `Note ${i + 1}`))

    const wrapper = mount(NotesList, {
      props: {
        notes,
        totalNotes: 12,
      },
    })

    // Click next page button
    const nextButton = wrapper.find('.pagination-button[aria-label="Next page"]')
    await nextButton.trigger('click')

    // Should show page 2
    expect(wrapper.find('.pagination-text').text()).toContain('Page 2 of 3')

    // Should still display 5 notes (notes 6-10)
    expect(wrapper.findAll('.note-item-wrapper')).toHaveLength(5)
  })

  it('should navigate to last page correctly', async () => {
    const notes = Array.from({ length: 12 }, (_, i) => createMockNote(i + 1, `Note ${i + 1}`))

    const wrapper = mount(NotesList, {
      props: {
        notes,
        totalNotes: 12,
      },
    })

    // Navigate to page 3 (last page)
    const nextButton = wrapper.find('.pagination-button[aria-label="Next page"]')
    await nextButton.trigger('click') // Page 2
    await nextButton.trigger('click') // Page 3

    // Should show page 3
    expect(wrapper.find('.pagination-text').text()).toContain('Page 3 of 3')

    // Should display remaining 2 notes (notes 11-12)
    expect(wrapper.findAll('.note-item-wrapper')).toHaveLength(2)
  })

  it('should disable navigation buttons at boundaries', async () => {
    const notes = Array.from({ length: 12 }, (_, i) => createMockNote(i + 1, `Note ${i + 1}`))

    const wrapper = mount(NotesList, {
      props: {
        notes,
        totalNotes: 12,
      },
    })

    const prevButton = wrapper.find('.pagination-button[aria-label="Previous page"]')
    const nextButton = wrapper.find('.pagination-button[aria-label="Next page"]')

    // Previous button should be disabled on first page
    expect(prevButton.attributes('disabled')).toBeDefined()

    // Navigate to last page
    await nextButton.trigger('click') // Page 2
    await nextButton.trigger('click') // Page 3

    // Next button should be disabled on last page
    expect(nextButton.attributes('disabled')).toBeDefined()
  })

  it('should reset to page 1 when notes change', async () => {
    const initialNotes = Array.from({ length: 12 }, (_, i) =>
      createMockNote(i + 1, `Note ${i + 1}`),
    )

    const wrapper = mount(NotesList, {
      props: {
        notes: initialNotes,
        totalNotes: 12,
      },
    })

    // Navigate to page 2
    const nextButton = wrapper.find('.pagination-button[aria-label="Next page"]')
    await nextButton.trigger('click')

    expect(wrapper.find('.pagination-text').text()).toContain('Page 2 of 3')

    // Change the notes prop
    const newNotes = Array.from({ length: 8 }, (_, i) => createMockNote(i + 1, `New Note ${i + 1}`))

    await wrapper.setProps({ notes: newNotes, totalNotes: 8 })

    // Should reset to page 1
    expect(wrapper.find('.pagination-text').text()).toContain('Page 1 of 2')
  })
})
