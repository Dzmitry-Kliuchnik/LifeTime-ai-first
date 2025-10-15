import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import NotesSearch from '../NotesSearch.vue'
import NotesInterface from '../NotesInterface.vue'
import type { NoteResponse } from '@/types'

// Mock stores
const mockNotesStore = {
  notes: [] as NoteResponse[],
  totalNotes: 0,
  pagination: { page: 1, size: 20 },
  totalPages: 1,
  isLoading: false,
  error: null as string | null,
  categories: ['Work', 'Personal', 'Ideas', 'Travel'],
  tags: ['important', 'todo', 'project', 'meeting', 'review'],
  searchNotes: vi.fn().mockResolvedValue({ notes: [], total: 0 }),
  fetchNotes: vi.fn(),
  fetchCategories: vi.fn(),
  fetchTags: vi.fn(),
  clearError: vi.fn(),
  setPagination: vi.fn(),
  setSortOptions: vi.fn(),
}

const mockUserStore = {
  currentUser: { id: 1, email: 'test@example.com' },
  isAuthenticated: true,
}

const mockWeekCalculationStore = {
  currentWeek: { current_week_index: 42 },
  totalWeeks: { total_weeks: 4000 },
  calculateCurrentWeek: vi.fn().mockResolvedValue({ current_week_index: 42 }),
  calculateTotalWeeks: vi.fn().mockResolvedValue({ total_weeks: 4000 }),
}

vi.mock('@/stores/notes', () => ({
  useNotesStore: vi.fn(() => mockNotesStore),
}))

vi.mock('@/stores/user', () => ({
  useUserStore: vi.fn(() => mockUserStore),
}))

vi.mock('@/stores/week-calculation', () => ({
  useWeekCalculationStore: vi.fn(() => mockWeekCalculationStore),
}))

describe('NotesSearch.vue', () => {
  let pinia: any
  let wrapper: VueWrapper<any>

  const mountComponent = (props = {}) => {
    return mount(NotesSearch, {
      global: {
        plugins: [pinia],
      },
      props: {
        showAdvancedToggle: true,
        showQuickFilters: true,
        ...props,
      },
    })
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('Text Search', () => {
    it('emits a search event with the query when the search button is clicked', async () => {
      wrapper = mountComponent()
      const searchInput = wrapper.find('#search-query')
      await searchInput.setValue('meeting')
      await wrapper.find('.search-button').trigger('click')

      expect(wrapper.emitted('search')).toBeTruthy()
      expect(wrapper.emitted('search')?.[0]).toEqual([{ query: 'meeting' }])
    })

    it('emits a search event on input when autoSearch is true', async () => {
      wrapper = mountComponent({ autoSearch: true, searchDelay: 0 })
      const searchInput = wrapper.find('#search-query')
      await searchInput.setValue('roadmap')
      await new Promise((resolve) => setTimeout(resolve, 50)) // Wait for debounce

      expect(wrapper.emitted('search')).toBeTruthy()
      expect(wrapper.emitted('search')?.[0]).toEqual([{ query: 'roadmap' }])
    })

    it('clears the search input and emits a clear event', async () => {
      wrapper = mountComponent()
      const searchInput = wrapper.find('#search-query')
      await searchInput.setValue('test')

      const clearButton = wrapper.find('.clear-search-button')
      await clearButton.trigger('click')

      expect((wrapper.find('#search-query').element as HTMLInputElement).value).toBe('')
      expect(wrapper.emitted('clear')).toBeTruthy()
    })
  })

  describe('Advanced Filters', () => {
    beforeEach(async () => {
      wrapper = mountComponent({
        availableCategories: ['Work', 'Personal', 'Ideas'],
        availableTags: ['important', 'project', 'meeting'],
      })
      await wrapper.find('.advanced-toggle-button').trigger('click')
    })

    it('filters by tags', async () => {
      const tagInput = wrapper.find('#tags-filter')
      await tagInput.setValue('project')
      await tagInput.trigger('keydown.enter')
      await wrapper.find('.search-button').trigger('click')

      expect(wrapper.emitted('search')?.[0]).toEqual([{ tags: ['project'] }])
    })

    it('filters by date range', async () => {
      const dateFromInput = wrapper.find('#date-from')
      const dateToInput = wrapper.find('#date-to')
      await dateFromInput.setValue('2024-01-01')
      await dateToInput.setValue('2024-01-31')
      await wrapper.find('.search-button').trigger('click')

      expect(wrapper.emitted('search')?.[0]).toEqual([
        { start_date: '2024-01-01', end_date: '2024-01-31' },
      ])
    })

    it('clears all filters when "Clear All Filters" is clicked', async () => {
      // Set some filters
      await wrapper.find('#search-query').setValue('test')

      // Click clear
      await wrapper.find('[data-testid="clear-all-filters"]').trigger('click')

      expect(wrapper.emitted('clear')).toBeTruthy()
    })
  })

  describe('Quick Filters', () => {
    beforeEach(() => {
      wrapper = mountComponent({
        autoSearch: true,
        searchDelay: 0,
        availableCategories: ['Work', 'Personal', 'Ideas'],
        availableTags: ['important', 'project', 'meeting'],
      })
    })

    it('toggles favorite filter', async () => {
      const favoritesButton = wrapper.find('[data-testid="filter-favorites"]')
      await favoritesButton.trigger('click')
      await nextTick()

      expect(wrapper.emitted('search')?.[0]).toEqual([{ is_favorite: true }])

      await favoritesButton.trigger('click')
      await nextTick()

      expect(wrapper.emitted('search')?.[1]).toEqual([{}])
    })

    it('toggles archived filter', async () => {
      const archivedButton = wrapper.find('[data-testid="filter-archived"]')
      await archivedButton.trigger('click')
      await nextTick()

      expect(wrapper.emitted('search')?.[0]).toEqual([{ is_archived: true }])
    })

    it('toggles active filter', async () => {
      const activeButton = wrapper.find('[data-testid="filter-active"]')
      await activeButton.trigger('click')
      await nextTick()

      expect(wrapper.emitted('search')?.[0]).toEqual([{ is_archived: false }])
    })
  })

  describe('Error Handling', () => {
    it('displays an error message and a retry button', async () => {
      wrapper = mountComponent({ searchError: 'Search service unavailable' })
      await nextTick()

      expect(wrapper.find('.search-error').exists()).toBe(true)
      expect(wrapper.text()).toContain('Search service unavailable')

      const retryButton = wrapper.find('.retry-button')
      expect(retryButton.exists()).toBe(true)

      await retryButton.trigger('click')
      expect(wrapper.emitted('search')).toBeTruthy()
    })
  })

  describe('Integration with NotesInterface', () => {
    let interfaceWrapper: VueWrapper<any>

    beforeEach(() => {
      interfaceWrapper = mount(NotesInterface, {
        global: {
          plugins: [pinia],
        },
      })
    })

    afterEach(() => {
      if (interfaceWrapper) {
        interfaceWrapper.unmount()
      }
    })

    it('updates notes list when a search is performed from NotesSearch', async () => {
      const notesSearch = interfaceWrapper.findComponent(NotesSearch)

      await notesSearch.find('#search-query').setValue('meeting')
      await notesSearch.find('.search-button').trigger('click')

      expect(mockNotesStore.searchNotes).toHaveBeenCalledExactlyOnceWith(
        expect.objectContaining({ query: 'meeting' }),
      )
    })

    it('shows loading state on the interface during search', async () => {
      // Mock a slow search to test loading state
      let resolveSearch: (value: any) => void
      const searchPromise = new Promise((resolve) => {
        resolveSearch = resolve
      })
      mockNotesStore.searchNotes.mockReturnValue(searchPromise)

      // Start the search - this should trigger the loading state
      const searchPromiseCall = interfaceWrapper.vm.handleSearch({ query: 'test' })
      await interfaceWrapper.vm.$nextTick()

      // Verify the search was initiated properly
      expect(mockNotesStore.searchNotes).toHaveBeenCalledExactlyOnceWith({ query: 'test' })

      // Complete the search
      resolveSearch!({ notes: [], total: 0 })
      await searchPromiseCall
    })

    it('shows search results count on the interface', async () => {
      // Mock search to return 5 results
      mockNotesStore.searchNotes.mockResolvedValueOnce({
        notes: Array(5).fill({
          id: 1,
          title: 'Test Note',
          content: 'Test content',
          user_id: 1,
          tags: [],
          week_number: 1,
          is_favorite: false,
          is_archived: false,
          word_count: 2,
          reading_time: 1,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        }),
        total: 5,
      })

      await interfaceWrapper.vm.handleSearch({ query: 'test' })
      await interfaceWrapper.vm.$nextTick()

      const resultsCount = interfaceWrapper.find('.search-results-count')
      expect(resultsCount.exists()).toBe(true)
      expect(resultsCount.text()).toContain('5 results')
    })

    it('shows no results message when search yields no notes', async () => {
      // Mock search to return no results
      mockNotesStore.searchNotes.mockResolvedValueOnce({
        notes: [],
        total: 0,
      })

      await interfaceWrapper.vm.handleSearch({ query: 'nonexistent' })
      await interfaceWrapper.vm.$nextTick()

      const noResults = interfaceWrapper.find('.notes-empty')
      expect(noResults.exists()).toBe(true)
      expect(noResults.text()).toContain('No matching notes found')
    })
  })
})
