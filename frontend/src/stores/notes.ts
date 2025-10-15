// Notes store for managing notes state and operations
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  NoteResponse,
  NoteCreate,
  NoteUpdate,
  NoteListResponse,
  NoteSearchRequest,
  WeekNotesResponse,
  NoteStatistics,
  LoadingState,
  PaginationParams,
  SortOptions,
} from '@/types'
import { notesApi, apiUtils } from '@/utils/api'
import { useUserStore } from './user'

export const useNotesStore = defineStore('notes', () => {
  // State
  const notes = ref<NoteResponse[]>([])
  const currentNote = ref<NoteResponse | null>(null)
  const weekNotes = ref<WeekNotesResponse | null>(null)
  const statistics = ref<NoteStatistics | null>(null)
  const tags = ref<string[]>([])
  const loadingState = ref<LoadingState>('idle')
  const error = ref<string | null>(null)

  // Pagination and filtering state
  const pagination = ref<PaginationParams>({
    page: 1,
    size: 20,
  })
  const totalNotes = ref(0)
  const hasNextPage = ref(false)
  const hasPrevPage = ref(false)
  const searchFilters = ref<NoteSearchRequest>({})
  const sortOptions = ref<SortOptions>({
    field: 'updated_at',
    direction: 'desc',
  })

  // Getters
  const favoriteNotes = computed(() => notes.value.filter((note) => note.is_favorite))

  const archivedNotes = computed(() => notes.value.filter((note) => note.is_archived))

  const activeNotes = computed(() => notes.value.filter((note) => !note.is_archived))

  const notesByWeek = computed(() => {
    const grouped: Record<number, NoteResponse[]> = {}
    notes.value.forEach((note) => {
      if (note.week_number != null) {
        grouped[note.week_number] ??= []
        grouped[note.week_number]!.push(note)
      }
    })
    return grouped
  })

  const totalPages = computed(() => Math.ceil(totalNotes.value / (pagination.value.size || 20)))

  const isLoading = computed(() => loadingState.value === 'loading')
  const isIdle = computed(() => loadingState.value === 'idle')
  const hasError = computed(() => loadingState.value === 'error')

  // Actions
  const setLoadingState = (state: LoadingState) => {
    loadingState.value = state
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const clearError = () => {
    error.value = null
  }

  const getUserId = (): number | null => {
    const userStore = useUserStore()
    return userStore.currentUser?.id || null
  }

  const createNote = async (
    noteData: NoteCreate,
    focusedWeek?: number,
  ): Promise<NoteResponse | null> => {
    const userId = getUserId()
    if (!userId) {
      setError('User not authenticated')
      return null
    }

    try {
      setLoadingState('loading')
      clearError()

      const note = await notesApi.createNote(userId, noteData, focusedWeek)

      // Add to the beginning of the notes array
      notes.value.unshift(note)
      totalNotes.value += 1

      setLoadingState('success')
      return note
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to create note: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const fetchNote = async (noteId: number): Promise<NoteResponse | null> => {
    const userId = getUserId()
    if (!userId) {
      setError('User not authenticated')
      return null
    }

    try {
      setLoadingState('loading')
      clearError()

      const note = await notesApi.getNote(noteId, userId)
      currentNote.value = note

      // Update the note in the notes array if it exists
      const index = notes.value.findIndex((n) => n.id === noteId)
      if (index !== -1) {
        notes.value[index] = note
      }

      setLoadingState('success')
      return note
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to fetch note: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const updateNote = async (noteId: number, noteData: NoteUpdate): Promise<NoteResponse | null> => {
    const userId = getUserId()
    if (!userId) {
      setError('User not authenticated')
      return null
    }

    try {
      setLoadingState('loading')
      clearError()

      console.log('Calling API to update note:', { noteId, userId, noteData })
      const updatedNote = await notesApi.updateNote(noteId, userId, noteData)
      console.log('API response received:', updatedNote)

      // Update in notes array
      const index = notes.value.findIndex((n) => n.id === noteId)
      if (index !== -1) {
        notes.value[index] = updatedNote
        console.log('Updated note in array at index:', index)
      } else {
        console.warn('Note not found in array for update, noteId:', noteId)
      }

      // Update current note if it's the same
      if (currentNote.value?.id === noteId) {
        currentNote.value = updatedNote
        console.log('Updated current note')
      }

      setLoadingState('success')
      console.log('updateNote returning:', updatedNote)
      return updatedNote
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      console.error('updateNote failed with error:', err)
      console.error('Error message:', errorMessage)
      setError(`Failed to update note: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const deleteNote = async (noteId: number): Promise<boolean> => {
    const userId = getUserId()
    if (!userId) {
      setError('User not authenticated')
      return false
    }

    try {
      setLoadingState('loading')
      clearError()

      await notesApi.deleteNote(noteId, userId)

      // Remove from notes array
      notes.value = notes.value.filter((n) => n.id !== noteId)
      totalNotes.value = Math.max(0, totalNotes.value - 1)

      // Clear current note if it's the deleted one
      if (currentNote.value?.id === noteId) {
        currentNote.value = null
      }

      setLoadingState('success')
      return true
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to delete note: ${errorMessage}`)
      setLoadingState('error')
      return false
    }
  }

  const fetchNotes = async (
    paginationParams?: PaginationParams,
    filters?: NoteSearchRequest,
    append = false,
  ): Promise<NoteListResponse | null> => {
    const userId = getUserId()
    if (!userId) {
      setError('User not authenticated')
      return null
    }

    try {
      setLoadingState('loading')
      clearError()

      const params = { ...pagination.value, ...paginationParams }
      const searchFiltersToUse = { ...searchFilters.value, ...filters }

      const response = await notesApi.listNotes(userId, params, searchFiltersToUse)

      if (append) {
        notes.value.push(...response.notes)
      } else {
        notes.value = response.notes
      }

      totalNotes.value = response.total
      pagination.value.page = response.page
      pagination.value.size = response.size
      hasNextPage.value = response.has_next
      hasPrevPage.value = response.has_prev

      setLoadingState('success')
      return response
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to fetch notes: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const searchNotes = async (searchData: NoteSearchRequest): Promise<NoteListResponse | null> => {
    const userId = getUserId()
    if (!userId) {
      setError('User not authenticated')
      return null
    }

    try {
      setLoadingState('loading')
      clearError()

      const response = await notesApi.searchNotes(userId, searchData)
      notes.value = response.notes
      totalNotes.value = response.total
      searchFilters.value = searchData

      setLoadingState('success')
      return response
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to search notes: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const fetchWeekNotes = async (weekNumber: number): Promise<WeekNotesResponse | null> => {
    const userId = getUserId()
    if (!userId) {
      setError('User not authenticated')
      return null
    }

    try {
      setLoadingState('loading')
      clearError()

      const response = await notesApi.getWeekNotes(userId, weekNumber)
      weekNotes.value = response

      setLoadingState('success')
      return response
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to fetch week notes: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const fetchStatistics = async (): Promise<NoteStatistics | null> => {
    const userId = getUserId()
    if (!userId) {
      setError('User not authenticated')
      return null
    }

    try {
      setLoadingState('loading')
      clearError()

      const stats = await notesApi.getNoteStatistics(userId)
      statistics.value = stats

      setLoadingState('success')
      return stats
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to fetch statistics: ${errorMessage}`)
      setLoadingState('error')
      return null
    }
  }

  const fetchTags = async (): Promise<string[] | null> => {
    const userId = getUserId()
    if (!userId) {
      setError('User not authenticated')
      return null
    }

    try {
      const tagList = await notesApi.getTags(userId)
      tags.value = tagList
      return tagList
    } catch (err) {
      const errorMessage = apiUtils.getErrorMessage(err)
      setError(`Failed to fetch tags: ${errorMessage}`)
      return null
    }
  }

  const toggleFavorite = async (noteId: number): Promise<boolean> => {
    const note = notes.value.find((n) => n.id === noteId)
    if (!note) {
      setError('Note not found')
      return false
    }

    console.log('toggleFavorite called for note:', {
      noteId,
      currentFavoriteStatus: note.is_favorite,
    })
    const result = await updateNote(noteId, { is_favorite: !note.is_favorite })
    console.log('updateNote returned:', result)
    console.log('toggleFavorite will return:', result !== null)
    // Don't clear the error if updateNote failed - let the error propagate
    return result !== null
  }

  const toggleArchive = async (noteId: number): Promise<boolean> => {
    const note = notes.value.find((n) => n.id === noteId)
    if (!note) {
      setError('Note not found')
      return false
    }

    return (await updateNote(noteId, { is_archived: !note.is_archived })) !== null
  }

  const loadMore = async (): Promise<boolean> => {
    if (!hasNextPage.value || isLoading.value) {
      return false
    }

    const nextPage = (pagination.value.page || 1) + 1
    const response = await fetchNotes({ page: nextPage }, undefined, true)
    return response !== null
  }

  const refresh = async (): Promise<boolean> => {
    const response = await fetchNotes({ page: 1 })
    return response !== null
  }

  const clearNotes = () => {
    notes.value = []
    currentNote.value = null
    weekNotes.value = null
    totalNotes.value = 0
    pagination.value.page = 1
    hasNextPage.value = false
    hasPrevPage.value = false
    searchFilters.value = {}
  }

  const setCurrentNote = (note: NoteResponse | null) => {
    currentNote.value = note
  }

  const setPagination = (params: PaginationParams) => {
    pagination.value = { ...pagination.value, ...params }
  }

  const setSearchFilters = (filters: NoteSearchRequest) => {
    searchFilters.value = filters
  }

  const setSortOptions = (options: SortOptions) => {
    sortOptions.value = options
  }

  return {
    // State
    notes,
    currentNote,
    weekNotes,
    statistics,
    tags,
    loadingState,
    error,
    pagination,
    totalNotes,
    hasNextPage,
    hasPrevPage,
    searchFilters,
    sortOptions,

    // Getters
    favoriteNotes,
    archivedNotes,
    activeNotes,
    notesByWeek,
    totalPages,
    isLoading,
    isIdle,
    hasError,

    // Actions
    createNote,
    fetchNote,
    updateNote,
    deleteNote,
    fetchNotes,
    searchNotes,
    fetchWeekNotes,
    fetchStatistics,
    fetchTags,
    toggleFavorite,
    toggleArchive,
    loadMore,
    refresh,
    clearNotes,
    setCurrentNote,
    setPagination,
    setSearchFilters,
    setSortOptions,
    clearError,
    setError,
  }
})
