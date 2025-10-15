<template>
  <div class="notes-list">
    <!-- List Header -->
    <div class="notes-list-header">
      <div class="notes-list-info">
        <h2 class="notes-list-title">
          {{ title }}
        </h2>
        <p v-if="description" class="notes-list-description">
          {{ description }}
        </p>
      </div>

      <div class="notes-list-controls">
        <!-- View Toggle -->

        <!-- Sort Controls -->
        <div v-if="showSortControls" class="sort-controls">
          <select
            v-model="currentSortField"
            class="sort-select"
            @change="handleSortChange"
            aria-label="Sort by"
          >
            <option value="title">Title</option>
            <option value="updated_at">Last Updated</option>
            <option value="created_at">Date Created</option>
            <option value="word_count">Word Count</option>
            <option value="reading_time">Reading Time</option>
          </select>
          <button
            type="button"
            class="sort-direction-button"
            @click="toggleSortDirection"
            :aria-label="`Sort ${currentSortDirection === 'desc' ? 'ascending' : 'descending'}`"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              :class="{ 'rotate-180': currentSortDirection === 'asc' }"
            >
              <path d="M3 6h18l-6 6H9z"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && notes.length === 0" class="notes-loading">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading notes...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="notes.length === 0" class="notes-empty empty-state" data-testid="empty-notes">
      <div class="empty-icon">
        <svg
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14,2 14,8 20,8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10,9 9,9 8,9"></polyline>
        </svg>
      </div>
      <h3 class="empty-title">{{ emptyTitle }}</h3>
      <p class="empty-description">{{ emptyDescription }}</p>
      <button
        v-if="showCreateButton"
        type="button"
        class="btn btn-primary"
        @click="handleCreateNote"
      >
        Create Your First Note
      </button>
    </div>

    <!-- Notes Grid/List -->
    <div
      v-else
      class="notes-container"
      :class="{
        'notes-grid': viewMode === 'grid',
        'notes-list-view': viewMode === 'list',
      }"
    >
      <TransitionGroup
        name="note-item"
        tag="div"
        class="notes-wrapper"
        :class="{
          'notes-grid-wrapper': viewMode === 'grid',
          'notes-list-wrapper': viewMode === 'list',
        }"
      >
        <div v-for="note in displayedNotes" :key="note.id" class="note-item-wrapper">
          <NoteDisplay
            :note="note"
            :variant="viewMode === 'grid' ? 'card' : 'compact'"
            :show-footer="showNoteFooter"
            :is-loading="loadingNoteIds.includes(note.id)"
            @favorite-toggle="handleFavoriteToggle"
            @archive-toggle="handleArchiveToggle"
            @edit="handleEditNote"
            @duplicate="handleDuplicateNote"
            @delete="handleDeleteNote"
            @tag-click="handleTagClick"
          />
        </div>
      </TransitionGroup>
    </div>

    <!-- Load More Button -->
    <div v-if="showLoadMore" class="load-more-section">
      <button
        type="button"
        class="btn btn-secondary load-more-button"
        @click="handleLoadMore"
        :disabled="isLoadingMore"
      >
        <span v-if="isLoadingMore" class="loading-spinner small"></span>
        {{ isLoadingMore ? 'Loading...' : 'Load More Notes' }}
      </button>
    </div>

    <!-- Pagination -->
    <div v-if="shouldShowPagination" class="pagination-section">
      <nav class="pagination" role="navigation" aria-label="Notes pagination">
        <button
          type="button"
          class="pagination-button"
          :disabled="internalCurrentPage <= 1"
          @click="goToInternalPage(internalCurrentPage - 1)"
          aria-label="Previous page"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="15,18 9,12 15,6"></polyline>
          </svg>
        </button>

        <div class="pagination-info">
          <span class="pagination-text">
            Page {{ internalCurrentPage }} of {{ totalPagesComputed }}
          </span>
        </div>

        <button
          type="button"
          class="pagination-button"
          :disabled="internalCurrentPage >= totalPagesComputed"
          @click="goToInternalPage(internalCurrentPage + 1)"
          aria-label="Next page"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="9,18 15,12 9,6"></polyline>
          </svg>
        </button>
      </nav>
    </div>

    <!-- Error State -->
    <div v-if="error" class="notes-error">
      <div class="error-icon">
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
      <h3 class="error-title">Failed to load notes</h3>
      <p class="error-description">{{ error }}</p>
      <button type="button" class="btn btn-secondary" @click="handleRetry">Try Again</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { NoteResponse, SortOptions } from '@/types'
import NoteDisplay from './NoteDisplay.vue'

interface Props {
  notes: NoteResponse[]
  totalNotes?: number
  currentPage?: number
  totalPages?: number
  isLoading?: boolean
  isLoadingMore?: boolean
  error?: string | null
  title?: string
  description?: string
  emptyTitle?: string
  emptyDescription?: string
  showViewToggle?: boolean
  showSortControls?: boolean
  showLoadMore?: boolean
  showPagination?: boolean
  showCreateButton?: boolean
  showNoteFooter?: boolean
  loadingNoteIds?: number[]
  defaultViewMode?: 'list' | 'grid'
  defaultSortField?: string
  defaultSortDirection?: 'asc' | 'desc'
  hasFilters?: boolean
}

interface Emits {
  (e: 'note-favorite-toggle', note: NoteResponse): void
  (e: 'note-archive-toggle', note: NoteResponse): void
  (e: 'note-edit', note: NoteResponse): void
  (e: 'note-duplicate', note: NoteResponse): void
  (e: 'note-delete', note: NoteResponse): void
  (e: 'tag-click', tag: string, note: NoteResponse): void
  (e: 'create-note'): void
  (e: 'load-more'): void
  (e: 'page-change', page: number): void
  (e: 'sort-change', sortOptions: SortOptions): void
  (e: 'view-mode-change', viewMode: 'list' | 'grid'): void
  (e: 'retry'): void
  // Legacy aliases for backward compatibility with tests
  (e: 'favorite', note: NoteResponse): void
  (e: 'archive', note: NoteResponse): void
  (e: 'edit', note: NoteResponse): void
  (e: 'delete', note: NoteResponse): void
}

const props = withDefaults(defineProps<Props>(), {
  totalNotes: 0,
  currentPage: 1,
  totalPages: 1,
  isLoading: false,
  isLoadingMore: false,
  error: null,
  title: 'Notes',
  description: '',
  emptyTitle: 'No notes found',
  emptyDescription: 'Start by creating your first note to capture your thoughts and ideas.',
  showViewToggle: true,
  showSortControls: true,
  showLoadMore: false,
  showPagination: true,
  showCreateButton: true,
  showNoteFooter: true,
  loadingNoteIds: () => [],
  defaultViewMode: 'grid',
  defaultSortField: 'updated_at',
  defaultSortDirection: 'desc',
  hasFilters: false,
})

const emit = defineEmits<Emits>()

// Constants
const NOTES_PER_PAGE = 5

// Component state
const viewMode = ref<'list' | 'grid'>(props.defaultViewMode)
const currentSortField = ref(props.defaultSortField)
const currentSortDirection = ref<'asc' | 'desc'>(props.defaultSortDirection)
const internalCurrentPage = ref(1)

// Computed properties
const sortedNotes = computed(() => {
  if (!props.notes) return []

  // Create a copy to avoid mutating the original array
  const sortedNotes = [...props.notes]

  // Sort notes
  sortedNotes.sort((a, b) => {
    let aValue: string | number = a[currentSortField.value as keyof NoteResponse] as string | number
    let bValue: string | number = b[currentSortField.value as keyof NoteResponse] as string | number

    // Handle null/undefined values
    if (aValue === null || aValue === undefined) aValue = ''
    if (bValue === null || bValue === undefined) bValue = ''

    // Convert to string for comparison if needed
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      aValue = aValue.toLowerCase()
      bValue = bValue.toLowerCase()
    }

    let comparison = 0
    if (aValue < bValue) {
      comparison = -1
    } else if (aValue > bValue) {
      comparison = 1
    }

    return currentSortDirection.value === 'desc' ? -comparison : comparison
  })

  return sortedNotes
})

const totalPagesComputed = computed(() => {
  return Math.ceil(sortedNotes.value.length / NOTES_PER_PAGE)
})

const shouldShowPagination = computed(() => {
  return sortedNotes.value.length > NOTES_PER_PAGE
})

const displayedNotes = computed(() => {
  if (!sortedNotes.value.length) return []

  // If we don't need pagination, return all notes
  if (!shouldShowPagination.value) {
    return sortedNotes.value
  }

  // Calculate pagination
  const startIndex = (internalCurrentPage.value - 1) * NOTES_PER_PAGE
  const endIndex = startIndex + NOTES_PER_PAGE

  return sortedNotes.value.slice(startIndex, endIndex)
})

// Methods
const setViewMode = (mode: 'list' | 'grid') => {
  viewMode.value = mode
  emit('view-mode-change', mode)
}

const handleSortChange = () => {
  const sortOptions: SortOptions = {
    field: currentSortField.value,
    direction: currentSortDirection.value,
  }
  emit('sort-change', sortOptions)
}

const toggleSortDirection = () => {
  currentSortDirection.value = currentSortDirection.value === 'desc' ? 'asc' : 'desc'
  handleSortChange()
}

const handleFavoriteToggle = (note: NoteResponse) => {
  emit('note-favorite-toggle', note)
  // Legacy alias for tests emitting 'favorite'
  ;(emit as any)('favorite', note)
}

const handleArchiveToggle = (note: NoteResponse) => {
  emit('note-archive-toggle', note)
  ;(emit as any)('archive', note)
}

const handleEditNote = (note: NoteResponse) => {
  emit('note-edit', note)
  ;(emit as any)('edit', note)
}

const handleDuplicateNote = (note: NoteResponse) => {
  emit('note-duplicate', note)
}

const handleDeleteNote = (note: NoteResponse) => {
  emit('note-delete', note)
  ;(emit as any)('delete', note)
}

const handleTagClick = (tag: string, note: NoteResponse) => {
  emit('tag-click', tag, note)
}

const handleCreateNote = () => {
  emit('create-note')
}

const handleLoadMore = () => {
  emit('load-more')
}

const goToPage = (page: number) => {
  if (page >= 1 && page <= props.totalPages) {
    emit('page-change', page)
  }
}

const goToInternalPage = (page: number) => {
  if (page >= 1 && page <= totalPagesComputed.value) {
    internalCurrentPage.value = page
  }
}

const handleRetry = () => {
  emit('retry')
}

// Watch for prop changes to update local state
watch(
  () => props.defaultViewMode,
  (newMode) => {
    viewMode.value = newMode
  },
)

watch(
  () => props.defaultSortField,
  (newField) => {
    currentSortField.value = newField
  },
)

watch(
  () => props.defaultSortDirection,
  (newDirection) => {
    currentSortDirection.value = newDirection
  },
)

// Reset internal pagination when notes change or sort changes
watch([() => props.notes, currentSortField, currentSortDirection], () => {
  internalCurrentPage.value = 1
})
</script>

<style scoped>
/* CSS Variables */
:root {
  --notes-list-bg: #ffffff;
  --notes-list-border: #e2e8f0;
  --notes-list-text-primary: #1a202c;
  --notes-list-text-secondary: #718096;
  --notes-list-text-muted: #a0aec0;
  --notes-list-primary: #3182ce;
  --notes-list-hover: #f7fafc;
  --notes-list-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  --notes-list-border-radius: 0.5rem;
  --notes-list-transition: all 0.2s ease;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --notes-list-bg: #2d3748;
    --notes-list-border: #4a5568;
    --notes-list-text-primary: #f7fafc;
    --notes-list-text-secondary: #a0aec0;
    --notes-list-text-muted: #718096;
    --notes-list-primary: #63b3ed;
    --notes-list-hover: #4a5568;
  }
}

/* Notes List Container */
.notes-list {
  display: flex;
  flex-direction: column;
  width: 100%;
}

/* Header */
.notes-list-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
}

.notes-list-info {
  flex: 1;
  min-width: 0;
}

.notes-list-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--notes-list-text-primary);
  line-height: 1.2;
}

.notes-list-description {
  margin: 0 0 0.75rem 0;
  color: var(--notes-list-text-secondary);
  font-size: 1rem;
  line-height: 1.5;
}

.notes-count {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--notes-list-text-muted);
}

.filtered-count {
  font-weight: 500;
  color: var(--notes-list-primary);
}

/* Controls */
.notes-list-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-select {
  padding: 0.5rem 0.5rem;
  border-radius: 0.5rem;
  background-color: var(--notes-list-bg);
  color: var(--notes-list-text-primary);
  font-size: 0.875rem;
  cursor: pointer;
}

.sort-direction-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border: 1px solid var(--notes-list-border);
  background-color: var(--notes-list-bg);
  border-radius: 0.375rem;
  color: var(--notes-list-text-muted);
  cursor: pointer;
  transition: var(--notes-list-transition);
}

.sort-direction-button:hover {
  color: var(--notes-list-text-secondary);
  background-color: var(--notes-list-hover);
}

.rotate-180 {
  transform: rotate(180deg);
}

/* Loading State */
.notes-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid var(--notes-list-border);
  border-top: 3px solid var(--notes-list-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.loading-spinner.small {
  width: 1rem;
  height: 1rem;
  border-width: 2px;
  margin: 0;
}

.loading-text {
  margin: 0;
  color: var(--notes-list-text-secondary);
  font-size: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Empty State */
.notes-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon {
  margin-bottom: 1.5rem;
  color: var(--notes-list-text-muted);
}

.empty-title {
  margin: 0 0 0.75rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--notes-list-text-primary);
}

.empty-description {
  margin: 0 0 2rem 0;
  color: var(--notes-list-text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  max-width: 28rem;
}

/* Notes Container */
.notes-container {
  width: 100%;
}

.notes-grid-wrapper {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fill, minmax(20rem, 1fr));
}

.notes-list-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.note-item-wrapper {
  width: 100%;
}

/* Transitions */
.note-item-enter-active,
.note-item-leave-active {
  transition: var(--notes-list-transition);
}

.note-item-enter-from {
  opacity: 0;
  transform: translateY(1rem);
}

.note-item-leave-to {
  opacity: 0;
  transform: translateY(-1rem);
}

/* Load More */
.load-more-section {
  display: flex;
  justify-content: center;
  padding: 1rem 0;
}

.load-more-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Pagination */
.pagination-section {
  display: flex;
  justify-content: center;
  padding: 1rem 0;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pagination-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border: 1px solid var(--notes-list-border);
  background-color: var(--notes-list-bg);
  border-radius: 0.375rem;
  color: var(--notes-list-text-muted);
  cursor: pointer;
  transition: var(--notes-list-transition);
}

.pagination-button:hover:not(:disabled) {
  color: var(--notes-list-text-secondary);
  background-color: var(--notes-list-hover);
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  padding: 0 1rem;
}

.pagination-text {
  font-size: 0.875rem;
  color: var(--notes-list-text-secondary);
  font-weight: 500;
}

/* Error State */
.notes-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.error-icon {
  margin-bottom: 1.5rem;
  color: #e53e3e;
}

.error-title {
  margin: 0 0 0.75rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--notes-list-text-primary);
}

.error-description {
  margin: 0 0 2rem 0;
  color: var(--notes-list-text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  max-width: 28rem;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--notes-list-transition);
  text-decoration: none;
  min-height: 2.5rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--notes-list-primary);
}

.btn-primary:hover:not(:disabled) {
  background-color: #2c5282;
}

.btn-secondary {
  background-color: var(--notes-list-hover);
  color: var(--notes-list-text-primary);
  border: 1px solid var(--notes-list-border);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--notes-list-border);
}

/* Responsive Design */
@media (max-width: 768px) {
  .notes-list-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .notes-list-controls {
    justify-content: space-between;
  }

  .notes-list-title {
    font-size: 1.5rem;
  }

  .notes-grid-wrapper {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .sort-controls {
    order: -1;
  }
}

@media (max-width: 480px) {
  .notes-list {
    gap: 1rem;
  }

  .notes-loading,
  .notes-empty,
  .notes-error {
    padding: 2rem 1rem;
  }

  .empty-title,
  .error-title {
    font-size: 1.25rem;
  }

  .btn {
    font-size: 0.8125rem;
    padding: 0.625rem 1.25rem;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
    animation: none !important;
  }
}
</style>
