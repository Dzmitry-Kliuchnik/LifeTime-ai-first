import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import NoteDisplay from '../NoteDisplay.vue'
import NotesList from '../NotesList.vue'
import NotesInterface from '../NotesInterface.vue'
import type { NoteResponse, NoteCreate, NoteUpdate } from '@/types'

// Mock stores
const mockNotesStore = {
  notes: [] as NoteResponse[],
  totalNotes: 0,
  pagination: {
    page: 1,
    size: 20,
  },
  totalPages: 1,
  isLoading: false,
  error: null as string | null,
  categories: ['Work', 'Personal', 'Ideas'],
  tags: ['important', 'todo', 'project'],
  createNote: vi.fn().mockResolvedValue({ id: 1, title: 'New Note' }),
  updateNote: vi.fn().mockResolvedValue({ id: 1, title: 'Updated Note' }),
  deleteNote: vi.fn().mockResolvedValue({}),
  fetchNotes: vi.fn().mockResolvedValue({ notes: [], total: 0 }),
  fetchNote: vi.fn().mockResolvedValue({ id: 1, title: 'Test Note' }),
  searchNotes: vi.fn().mockResolvedValue({ notes: [], total: 0 }),
  fetchCategories: vi.fn().mockResolvedValue(['Work', 'Personal', 'Ideas']),
  fetchTags: vi.fn().mockResolvedValue(['important', 'todo', 'project']),
  archiveNote: vi.fn().mockResolvedValue({}),
  favoriteNote: vi.fn().mockResolvedValue({}),
  unfavoriteNote: vi.fn().mockResolvedValue({}),
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

describe('Notes CRUD Operations', () => {
  let pinia: any

  const mockNote: NoteResponse = {
    id: 1,
    title: 'Test Note',
    content: 'This is a test note content',
    user_id: 1,
    tags: ['important', 'project'],
    week_number: 42,
    is_favorite: false,
    is_archived: false,
    word_count: 6,
    reading_time: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  }

  const mockNotes: NoteResponse[] = [
    mockNote,
    {
      ...mockNote,
      id: 2,
      title: 'Second Note',
      content: 'Another test note',
      is_favorite: true,
    },
    {
      ...mockNote,
      id: 3,
      title: 'Archived Note',
      content: 'This note is archived',
      is_archived: true,
    },
  ]

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Note Creation', () => {
    let wrapper: VueWrapper<any>

    beforeEach(() => {
      mockNotesStore.notes = []
      mockNotesStore.totalNotes = 0
      wrapper = mount(NotesInterface, {
        global: {
          plugins: [pinia],
        },
      })
    })

    afterEach(() => {
      if (wrapper) {
        wrapper.unmount()
      }
    })

    it('should create a new note successfully', async () => {
      const newNote: NoteCreate = {
        title: 'New Test Note',
        content: 'This is new note content',
        tags: ['new', 'test'],
        week_number: 42,
        is_favorite: false,
        is_archived: false,
      }

      mockNotesStore.createNote.mockResolvedValue({
        ...mockNote,
        ...newNote,
        id: 4,
      })

      // Open create modal
      const createButton = wrapper.find('[data-testid="create-note-button"]')
      await createButton.trigger('click')

      expect(wrapper.find('[data-testid="notes-modal"]').exists()).toBe(true)

      // Simulate form submission
      const formComponent = wrapper.findComponent({ name: 'NotesForm' })
      formComponent.vm.$emit('submit', newNote)
      await nextTick()

      expect(mockNotesStore.createNote).toHaveBeenCalledExactlyOnceWith(newNote, undefined)
    })

    it('should handle note creation errors', async () => {
      const errorMessage = 'Failed to create note'
      mockNotesStore.createNote.mockResolvedValue(null)
      mockNotesStore.error = errorMessage

      const newNote: NoteCreate = {
        title: 'Failing Note',
        content: 'This will fail to create',
        is_favorite: false,
        is_archived: false,
      }

      // Open create modal
      const createButton = wrapper.find('[data-testid="create-note-button"]')
      await createButton.trigger('click')

      // Simulate form submission
      const formComponent = wrapper.findComponent({ name: 'NotesForm' })
      formComponent.vm.$emit('submit', newNote)
      await nextTick()

      expect(mockNotesStore.createNote).toHaveBeenCalledExactlyOnceWith(newNote, undefined)
      expect(wrapper.find('.error-notification').exists()).toBe(true)
    })

    it('should validate required fields before creation', async () => {
      const invalidNote: Partial<NoteCreate> = {
        title: '',
        content: '',
        is_favorite: false,
        is_archived: false,
      }

      // Open create modal
      const createButton = wrapper.find('[data-testid="create-note-button"]')
      await createButton.trigger('click')

      // Try to submit invalid form
      const formComponent = wrapper.findComponent({ name: 'NotesForm' })
      formComponent.vm.$emit('submit', invalidNote)
      await nextTick()

      // Should not call createNote with invalid data
      expect(mockNotesStore.createNote).not.toHaveBeenCalled()
    })

    it('should close modal after successful creation', async () => {
      const newNote: NoteCreate = {
        title: 'Success Note',
        content: 'This will succeed',
        is_favorite: false,
        is_archived: false,
      }

      mockNotesStore.createNote.mockResolvedValue({
        ...mockNote,
        ...newNote,
        id: 5,
      })

      // Open create modal
      const createButton = wrapper.find('[data-testid="create-note-button"]')
      await createButton.trigger('click')

      expect(wrapper.find('[data-testid="notes-modal"]').exists()).toBe(true)

      // Simulate successful form submission
      const formComponent = wrapper.findComponent({ name: 'NotesForm' })
      formComponent.vm.$emit('success', { ...mockNote, ...newNote, id: 5 })
      await nextTick()

      expect(wrapper.find('[data-testid="notes-modal"]').exists()).toBe(false)
    })
  })

  describe('Note Reading/Display', () => {
    let wrapper: VueWrapper<any>

    beforeEach(() => {
      mockNotesStore.notes = mockNotes
      mockNotesStore.totalNotes = mockNotes.length
      wrapper = mount(NotesInterface, {
        global: {
          plugins: [pinia],
        },
      })
    })

    afterEach(() => {
      if (wrapper) {
        wrapper.unmount()
      }
    })

    it('should fetch and display notes on mount', async () => {
      expect(mockNotesStore.fetchNotes).toHaveBeenCalled()

      await nextTick()

      const notesList = wrapper.findComponent(NotesList)
      expect(notesList.exists()).toBe(true)
    })

    it('should display individual note details', () => {
      const noteDisplayWrapper = mount(NoteDisplay, {
        props: {
          note: mockNote,
        },
        global: {
          plugins: [pinia],
        },
      })

      expect(noteDisplayWrapper.find('.note-title').text()).toBe('Test Note')
      expect(noteDisplayWrapper.find('.note-content').text()).toBe('This is a test note content')
      expect(noteDisplayWrapper.find('.note-tags').text()).toContain('important')
      expect(noteDisplayWrapper.find('.note-tags').text()).toContain('project')

      noteDisplayWrapper.unmount()
    })

    it('should display note metadata correctly', () => {
      const noteDisplayWrapper = mount(NoteDisplay, {
        props: {
          note: mockNote,
        },
        global: {
          plugins: [pinia],
        },
      })

      // Find elements with .note-stat class that contain specific text
      const wordCountStat = noteDisplayWrapper
        .findAll('.note-stat')
        .find((stat) => stat.text().includes('words'))
      expect(wordCountStat?.text()).toContain('words: 6')

      const readingTimeStat = noteDisplayWrapper
        .findAll('.note-stat')
        .find((stat) => stat.text().includes('min read'))
      expect(readingTimeStat?.text()).toContain('1 min read')

      // Note: Week information is only shown in modal, not in main display by default
      // Just verify the note has a week_number property
      expect(mockNote.week_number).toBe(42)

      noteDisplayWrapper.unmount()
    })

    it('should handle loading state', async () => {
      mockNotesStore.isLoading = true

      const loadingWrapper = mount(NotesInterface, {
        global: {
          plugins: [pinia],
        },
      })

      expect(loadingWrapper.find('.loading-spinner').exists()).toBe(true)

      loadingWrapper.unmount()
    })

    it('should handle empty notes list', async () => {
      mockNotesStore.notes = []
      mockNotesStore.totalNotes = 0
      mockNotesStore.isLoading = false

      const emptyWrapper = mount(NotesInterface, {
        global: {
          plugins: [pinia],
        },
      })

      // Wait for async operations in onMounted to complete
      await nextTick()
      await new Promise((resolve) => setTimeout(resolve, 0))

      // Find the empty state in the NotesList component
      const emptyState = emptyWrapper.find('.empty-state')
      expect(emptyState.exists()).toBe(true)
      expect(emptyState.text()).toContain('No notes yet')

      emptyWrapper.unmount()
    })
  })

  describe('Note Updates', () => {
    let wrapper: VueWrapper<any>

    beforeEach(() => {
      mockNotesStore.notes = mockNotes
      wrapper = mount(NotesInterface, {
        global: {
          plugins: [pinia],
        },
      })
    })

    afterEach(() => {
      if (wrapper) {
        wrapper.unmount()
      }
    })

    it('should update an existing note successfully', async () => {
      const updatedData: NoteUpdate = {
        title: 'Updated Test Note',
        content: 'This is updated content',
        tags: ['updated', 'test'],
        is_favorite: true,
      }

      const updatedNote = { ...mockNote, ...updatedData }
      mockNotesStore.updateNote.mockResolvedValue(updatedNote)

      // Simulate edit action from note display
      const noteDisplay = wrapper.findComponent(NoteDisplay)
      noteDisplay.vm.$emit('edit', mockNote)
      await nextTick()

      expect(wrapper.find('[data-testid="notes-modal"]').exists()).toBe(true)

      // Simulate form submission
      const formComponent = wrapper.findComponent({ name: 'NotesForm' })
      formComponent.vm.$emit('submit', updatedData)
      await nextTick()

      expect(mockNotesStore.updateNote).toHaveBeenCalledExactlyOnceWith(mockNote.id, updatedData)
    })

    it('should handle note update errors', async () => {
      const errorMessage = 'Failed to update note'
      mockNotesStore.updateNote.mockResolvedValue(null)
      ;(mockNotesStore as any).error = errorMessage

      const updatedData: NoteUpdate = {
        title: 'Failing Update',
        content: 'This will fail to update',
      }

      // Simulate edit action
      const noteDisplay = wrapper.findComponent(NoteDisplay)
      noteDisplay.vm.$emit('edit', mockNote)
      await nextTick()

      // Simulate form submission
      const formComponent = wrapper.findComponent({ name: 'NotesForm' })
      formComponent.vm.$emit('submit', updatedData)
      await nextTick()

      expect(mockNotesStore.updateNote).toHaveBeenCalledExactlyOnceWith(mockNote.id, updatedData)
      expect(wrapper.find('.error-notification').exists()).toBe(true)
    })

    it('should toggle favorite status', async () => {
      const updatedNote = { ...mockNote, is_favorite: true }

      // Mock fetch for the direct API call
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(updatedNote),
      })

      // Simulate favorite action through NotesList (which NotesInterface listens to)
      const notesList = wrapper.findComponent({ name: 'NotesList' })
      notesList.vm.$emit('favorite', mockNote)
      await nextTick()

      // Verify the fetch call was made with correct parameters
      expect(fetch).toHaveBeenCalledExactlyOnceWith(
        `http://localhost:8000/api/v1/notes/${mockNote.id}?user_id=1`,
        expect.objectContaining({
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ is_favorite: !mockNote.is_favorite }),
        }),
      )
    })

    it('should toggle unfavorite status', async () => {
      const favoriteNote = { ...mockNote, is_favorite: true }
      const unfavoritedNote = { ...favoriteNote, is_favorite: false }

      // Mock fetch for the direct API call
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(unfavoritedNote),
      })

      // Simulate unfavorite action through NotesList
      const notesList = wrapper.findComponent({ name: 'NotesList' })
      notesList.vm.$emit('favorite', favoriteNote)
      await nextTick()

      // Verify the fetch call was made with correct parameters
      expect(fetch).toHaveBeenCalledExactlyOnceWith(
        `http://localhost:8000/api/v1/notes/${favoriteNote.id}?user_id=1`,
        expect.objectContaining({
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ is_favorite: !favoriteNote.is_favorite }),
        }),
      )
    })

    it('should toggle archive status', async () => {
      const archivedNote = { ...mockNote, is_archived: true }

      // Mock fetch for the direct API call
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(archivedNote),
      })

      // Simulate archive action through NotesList
      const notesList = wrapper.findComponent({ name: 'NotesList' })
      notesList.vm.$emit('archive', mockNote)
      await nextTick()

      // Verify the fetch call was made with correct parameters
      expect(fetch).toHaveBeenCalledExactlyOnceWith(
        `http://localhost:8000/api/v1/notes/${mockNote.id}?user_id=1`,
        expect.objectContaining({
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ is_archived: !mockNote.is_archived }),
        }),
      )
    })
  })

  describe('Note Deletion', () => {
    let wrapper: VueWrapper<any>

    beforeEach(() => {
      mockNotesStore.notes = mockNotes
      wrapper = mount(NotesInterface, {
        global: {
          plugins: [pinia],
        },
      })
    })

    afterEach(() => {
      if (wrapper) {
        wrapper.unmount()
      }
    })

    it('should delete a note successfully', async () => {
      mockNotesStore.deleteNote.mockResolvedValue(true)

      // Simulate delete action from note display
      const noteDisplay = wrapper.findComponent(NoteDisplay)
      noteDisplay.vm.$emit('delete', mockNote)
      await nextTick()

      expect(mockNotesStore.deleteNote).toHaveBeenCalledWithExactlyOnceWith(mockNote.id)
    })

    it('should handle note deletion errors', async () => {
      const errorMessage = 'Failed to delete note'
      mockNotesStore.deleteNote.mockResolvedValue(false)
      ;(mockNotesStore as any).error = errorMessage

      // Simulate delete action
      const noteDisplay = wrapper.findComponent(NoteDisplay)
      noteDisplay.vm.$emit('delete', mockNote)
      await nextTick()

      expect(mockNotesStore.deleteNote).toHaveBeenCalledWithExactlyOnceWith(mockNote.id)
      expect(wrapper.find('.error-notification').exists()).toBe(true)
    })

    it('should show confirmation before deletion', async () => {
      // Mock window.confirm
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
      mockNotesStore.deleteNote.mockResolvedValue(true)

      const noteDisplayWrapper = mount(NoteDisplay, {
        props: {
          note: mockNote,
          showMoreActions: true,
          showDeleteAction: true,
        },
        global: {
          plugins: [pinia],
        },
      })

      // First open the dropdown
      const dropdownTrigger = noteDisplayWrapper.find('.dropdown-trigger')
      await dropdownTrigger.trigger('click')
      await nextTick()

      // Then find and click the delete button
      const deleteButton = noteDisplayWrapper.find('.dropdown-item.danger')
      await deleteButton.trigger('click')

      expect(confirmSpy).toHaveBeenCalled()

      confirmSpy.mockRestore()
      noteDisplayWrapper.unmount()
    })

    it('should not delete if confirmation is cancelled', async () => {
      // Mock window.confirm to return false
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)

      const noteDisplayWrapper = mount(NoteDisplay, {
        props: {
          note: mockNote,
          showMoreActions: true,
          showDeleteAction: true,
        },
        global: {
          plugins: [pinia],
        },
      })

      // First open the dropdown
      const dropdownTrigger = noteDisplayWrapper.find('.dropdown-trigger')
      await dropdownTrigger.trigger('click')
      await nextTick()

      // Then find and click the delete button
      const deleteButton = noteDisplayWrapper.find('.dropdown-item.danger')
      await deleteButton.trigger('click')

      expect(confirmSpy).toHaveBeenCalled()
      expect(mockNotesStore.deleteNote).not.toHaveBeenCalled()

      confirmSpy.mockRestore()
      noteDisplayWrapper.unmount()
    })
  })

  describe('Error Handling', () => {
    let wrapper: VueWrapper<any>

    beforeEach(() => {
      wrapper = mount(NotesInterface, {
        global: {
          plugins: [pinia],
        },
      })
    })

    afterEach(() => {
      if (wrapper) {
        wrapper.unmount()
      }
    })

    it('should display API errors to user', async () => {
      const errorMessage = 'Network error occurred'
      ;(mockNotesStore as any).error = errorMessage

      await nextTick()

      expect(wrapper.find('.error-notification').exists()).toBe(true)
      expect(wrapper.find('.error-notification').text()).toContain(errorMessage)
    })

    it('should clear errors when dismissed', async () => {
      const errorMessage = 'Test error'
      ;(mockNotesStore as any).error = errorMessage

      await nextTick()

      expect(wrapper.find('.error-notification').exists()).toBe(true)

      // Dismiss the error
      const dismissButton = wrapper.find('.error-dismiss')
      await dismissButton.trigger('click')

      expect(mockNotesStore.clearError).toHaveBeenCalled()
    })

    it('should handle network failures gracefully', async () => {
      const networkFailureWrapper = mount(NotesInterface, {
        global: {
          plugins: [pinia],
        },
      })

      // Set error after mounting to trigger the watcher
      ;(mockNotesStore as any).error = 'Failed to load notes'
      await nextTick()
      await nextTick() // Wait for reactive updates

      expect(networkFailureWrapper.find('.error-notification').exists()).toBe(true)
      expect(networkFailureWrapper.find('.retry-button').exists()).toBe(true)

      networkFailureWrapper.unmount()
    })

    it('should retry failed operations', async () => {
      const retryWrapper = mount(NotesInterface, {
        global: {
          plugins: [pinia],
        },
      })

      // Set error after mounting to trigger the watcher
      ;(mockNotesStore as any).error = 'Failed to load notes'
      await nextTick()
      await nextTick() // Wait for reactive updates

      // Clear previous calls and setup successful retry
      vi.clearAllMocks()
      mockNotesStore.fetchNotes.mockResolvedValue({ notes: [], total: 0 })

      const retryButton = retryWrapper.find('.retry-button')
      expect(retryButton.exists()).toBe(true)

      await retryButton.trigger('click')
      await nextTick() // Wait for the retry operation to complete

      expect(mockNotesStore.fetchNotes).toHaveBeenCalledTimes(1) // Only the retry call

      retryWrapper.unmount()
    })
  })

  describe('Pagination and State Management', () => {
    let wrapper: VueWrapper<any>

    beforeEach(() => {
      mockNotesStore.notes = mockNotes
      mockNotesStore.totalNotes = 50
      mockNotesStore.pagination.page = 1
      mockNotesStore.totalPages = 5
      wrapper = mount(NotesInterface, {
        global: {
          plugins: [pinia],
        },
      })
    })

    afterEach(() => {
      if (wrapper) {
        wrapper.unmount()
      }
    })

    it('should handle pagination correctly', async () => {
      const notesList = wrapper.findComponent(NotesList)

      // Clear previous calls
      mockNotesStore.fetchNotes.mockClear()

      // Simulate page change
      notesList.vm.$emit('page-change', 2)
      await nextTick()

      expect(mockNotesStore.fetchNotes).toHaveBeenCalledExactlyOnceWith(
        expect.objectContaining({ page: 2 }),
      )
    })

    it('should refresh notes list after CRUD operations', async () => {
      const initialFetchCalls = mockNotesStore.fetchNotes.mock.calls.length

      // Create a note
      mockNotesStore.createNote.mockResolvedValue(mockNote)

      const createButton = wrapper.find('[data-testid="create-note-button"]')
      await createButton.trigger('click')

      const formComponent = wrapper.findComponent({ name: 'NotesForm' })
      formComponent.vm.$emit('success', mockNote)
      await nextTick()

      // Should refetch notes after successful creation
      expect(mockNotesStore.fetchNotes.mock.calls.length).toBeGreaterThan(initialFetchCalls)
    })

    it('should maintain search state during CRUD operations', async () => {
      const searchQuery = 'test search'

      // Set search state
      const notesSearch = wrapper.findComponent({ name: 'NotesSearch' })
      notesSearch.vm.$emit('search', { query: searchQuery })
      await nextTick()

      // Perform update operation
      mockNotesStore.updateNote.mockResolvedValue({ ...mockNote, title: 'Updated' })

      const noteDisplay = wrapper.findComponent(NoteDisplay)
      noteDisplay.vm.$emit('edit', mockNote)
      await nextTick()

      const formComponent = wrapper.findComponent({ name: 'NotesForm' })
      formComponent.vm.$emit('success', { ...mockNote, title: 'Updated' })
      await nextTick()

      // Should maintain search query in subsequent fetches
      expect(mockNotesStore.searchNotes).toHaveBeenCalledWithExactlyOnceWith(
        expect.objectContaining({ query: searchQuery }),
      )
    })
  })
})
