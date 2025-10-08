<template>
  <div class="notes-search">
    <!-- Search Header -->
    <div class="search-header">
      <div class="search-title-section">
        <h2 v-if="showTitle" class="search-title">Search Notes</h2>
        <p v-if="searchResults" class="search-results-count">
          {{ searchResults.total }} {{ searchResults.total === 1 ? 'result' : 'results' }}
          <span v-if="searchQuery" class="search-query">for "{{ searchQuery }}"</span>
        </p>
      </div>

      <div class="search-actions">
        <button
          v-if="showAdvancedToggle"
          type="button"
          class="advanced-toggle-button"
          :class="{ active: showAdvancedFilters }"
          @click="toggleAdvancedFilters"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46"></polygon>
          </svg>
          {{ showAdvancedFilters ? 'Hide' : 'Show' }} Filters
        </button>
      </div>
    </div>

    <!-- Main Search Bar -->
    <div class="search-bar-container">
      <div class="search-input-wrapper">
        <div class="search-icon">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
        </div>
        <input
          id="search-query"
          ref="searchInput"
          v-model="searchFilters.query"
          type="text"
          class="search-input"
          placeholder="Search notes by title, content, or tags..."
          @input="handleSearchInput"
          @keydown.enter="performSearch"
          @keydown.escape="clearSearch"
        />
        <button
          v-if="searchFilters.query"
          type="button"
          class="clear-search-button"
          @click="clearSearch"
          aria-label="Clear search"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <button type="button" class="search-button" @click="performSearch" :disabled="isSearching">
        <span v-if="isSearching" class="loading-spinner small"></span>
        <svg
          v-else
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        Search
      </button>
    </div>

    <!-- Quick Filters -->
    <div v-if="showQuickFilters" class="quick-filters">
      <div class="quick-filter-group">
        <button
          type="button"
          class="quick-filter-button"
          :class="{ active: searchFilters.is_favorite === true }"
          @click="toggleQuickFilter('is_favorite', true)"
          data-testid="filter-favorites"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polygon
              points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"
            ></polygon>
          </svg>
          Favorites
        </button>

        <button
          type="button"
          class="quick-filter-button"
          :class="{ active: searchFilters.is_archived === true }"
          @click="toggleQuickFilter('is_archived', true)"
          data-testid="filter-archived"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="21,8 21,21 3,21 3,8"></polyline>
            <rect x="1" y="3" width="22" height="5"></rect>
          </svg>
          Archived
        </button>

        <button
          type="button"
          class="quick-filter-button"
          :class="{ active: searchFilters.is_archived === false }"
          @click="toggleQuickFilter('is_archived', false)"
          data-testid="filter-active"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14,2 14,8 20,8"></polyline>
          </svg>
          Active
        </button>
      </div>
    </div>

    <!-- Advanced Filters -->
    <transition name="advanced-filters" appear>
      <div v-if="showAdvancedFilters" class="advanced-filters">
        <div class="filters-grid">
          <!-- Category Filter -->
          <div class="filter-group">
            <label for="category-filter" class="filter-label">Category</label>
            <select
              id="category-filter"
              v-model="searchFilters.category"
              class="filter-select"
              @change="handleFilterChange"
            >
              <option value="">All Categories</option>
              <option v-for="category in availableCategories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
          </div>

          <!-- Tags Filter -->
          <div class="filter-group">
            <label for="tags-filter" class="filter-label">Tags</label>
            <div class="tags-filter-container">
              <div class="selected-tags">
                <span v-for="tag in selectedTags" :key="tag" class="selected-tag">
                  {{ tag }}
                  <button
                    type="button"
                    class="remove-tag-button"
                    @click="removeTag(tag)"
                    :aria-label="`Remove ${tag} tag filter`"
                  >
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>
                </span>
              </div>
              <input
                id="tags-filter"
                v-model="tagInput"
                type="text"
                class="filter-input"
                placeholder="Type to add tags..."
                list="available-tags"
                @keydown.enter.prevent="addTag"
                @keydown="handleTagKeydown"
                @blur="addTag"
              />
              <datalist id="available-tags">
                <option v-for="tag in availableTags" :key="tag" :value="tag">
                  {{ tag }}
                </option>
              </datalist>
            </div>
          </div>

          <!-- Date Range Filter -->
          <div class="filter-group">
            <span class="filter-label">Date Range</span>
            <div class="date-range-container">
              <input
                id="date-from"
                v-model="searchFilters.start_date"
                type="date"
                class="filter-input"
                aria-label="Start date"
                @change="handleFilterChange"
              />
              <span class="date-separator">to</span>
              <input
                id="date-to"
                v-model="searchFilters.end_date"
                type="date"
                class="filter-input"
                aria-label="End date"
                @change="handleFilterChange"
              />
            </div>
          </div>

          <!-- Week Range Filter -->
          <div class="filter-group">
            <label for="week-filter" class="filter-label">Week Number</label>
            <input
              id="week-filter"
              v-model.number="searchFilters.week_number"
              type="number"
              class="filter-input"
              placeholder="Week number..."
              min="0"
              :max="maxWeekNumber"
              @input="handleFilterChange"
            />
          </div>
        </div>

        <!-- Filter Actions -->
        <div class="filter-actions">
          <button
            type="button"
            class="btn btn-secondary"
            @click="clearAllFilters"
            data-testid="clear-all-filters"
          >
            Clear All Filters
          </button>
          <button
            type="button"
            class="btn btn-primary"
            @click="performSearch"
            :disabled="isSearching"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </transition>

    <!-- Active Filters Summary -->
    <div v-if="hasActiveFilters" class="active-filters">
      <span class="active-filters-label">Active filters:</span>
      <div class="active-filter-tags">
        <span
          v-if="searchFilters.query"
          class="active-filter-tag"
          data-testid="active-filter-query"
        >
          Search: "{{ searchFilters.query }}"
          <button type="button" @click="clearFilter('query')" class="remove-filter">×</button>
        </span>
        <span
          v-if="searchFilters.category"
          class="active-filter-tag"
          data-testid="active-filter-category"
        >
          Category: {{ searchFilters.category }}
          <button type="button" @click="clearFilter('category')" class="remove-filter">×</button>
        </span>
        <span
          v-if="selectedTags.length > 0"
          class="active-filter-tag"
          data-testid="active-filter-tags"
        >
          Tags: {{ selectedTags.join(', ') }}
          <button type="button" @click="clearFilter('tags')" class="remove-filter">×</button>
        </span>
        <span
          v-if="searchFilters.is_favorite === true"
          class="active-filter-tag"
          data-testid="active-filter-favorite"
        >
          Favorites only
          <button type="button" @click="clearFilter('is_favorite')" class="remove-filter">×</button>
        </span>
        <span
          v-if="searchFilters.is_archived === true"
          class="active-filter-tag"
          data-testid="active-filter-archived"
        >
          Archived only
          <button type="button" @click="clearFilter('is_archived')" class="remove-filter">×</button>
        </span>
        <span
          v-if="searchFilters.is_archived === false"
          class="active-filter-tag"
          data-testid="active-filter-active-only"
        >
          Active only
          <button type="button" @click="clearFilter('is_archived')" class="remove-filter">×</button>
        </span>
        <span v-if="searchFilters.start_date || searchFilters.end_date" class="active-filter-tag">
          Date: {{ formatDateRange() }}
          <button type="button" @click="clearDateRange()" class="remove-filter">×</button>
        </span>
        <span v-if="searchFilters.week_number !== undefined" class="active-filter-tag">
          Week: {{ searchFilters.week_number }}
          <button type="button" @click="clearFilter('week_number')" class="remove-filter">×</button>
        </span>
      </div>
    </div>

    <!-- Search Error -->
    <div v-if="searchError" class="search-error">
      <div class="error-icon">
        <svg
          width="24"
          height="24"
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
      <span class="error-message">{{ searchError }}</span>
      <button type="button" class="btn btn-secondary btn-small" @click="clearSearchError">
        Dismiss
      </button>
      <button type="button" class="btn btn-primary btn-small retry-button" @click="performSearch">
        Retry
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { NoteSearchRequest, NoteListResponse } from '@/types'

interface Props {
  availableCategories?: string[]
  availableTags?: string[]
  maxWeekNumber?: number
  searchResults?: NoteListResponse | null
  isSearching?: boolean
  searchError?: string | null
  showTitle?: boolean
  showQuickFilters?: boolean
  showAdvancedToggle?: boolean
  autoSearch?: boolean
  searchDelay?: number
}

interface Emits {
  (e: 'search', filters: NoteSearchRequest): void
  (e: 'clear'): void
  (e: 'filters-change', filters: NoteSearchRequest): void
}

const props = withDefaults(defineProps<Props>(), {
  availableCategories: () => [],
  availableTags: () => [],
  maxWeekNumber: 5000,
  searchResults: null,
  isSearching: false,
  searchError: null,
  showTitle: true,
  showQuickFilters: true,
  showAdvancedToggle: true,
  autoSearch: false,
  searchDelay: 500,
})

const emit = defineEmits<Emits>()

// Template refs
const searchInput = ref<HTMLInputElement>()

// Component state
const showAdvancedFilters = ref(false)
const tagInput = ref('')
const searchQuery = ref('')
let searchTimeout: ReturnType<typeof setTimeout> | null = null

// Search filters
const searchFilters = ref<NoteSearchRequest>({
  query: '',
  category: '',
  tags: [],
  week_number: undefined,
  is_favorite: undefined,
  is_archived: undefined,
  start_date: '',
  end_date: '',
})

// Computed properties
const selectedTags = computed(() => searchFilters.value.tags || [])

const hasActiveFilters = computed(() => {
  return (
    searchFilters.value.query ||
    searchFilters.value.category ||
    (searchFilters.value.tags && searchFilters.value.tags.length > 0) ||
    searchFilters.value.is_favorite !== undefined ||
    searchFilters.value.is_archived !== undefined ||
    searchFilters.value.start_date ||
    searchFilters.value.end_date ||
    searchFilters.value.week_number !== undefined
  )
})

// Methods
const toggleAdvancedFilters = () => {
  showAdvancedFilters.value = !showAdvancedFilters.value
}

const handleSearchInput = () => {
  if (props.autoSearch) {
    if (searchTimeout) {
      clearTimeout(searchTimeout)
    }
    if (props.searchDelay === 0) {
      performSearch()
    } else {
      searchTimeout = setTimeout(() => {
        performSearch()
      }, props.searchDelay)
    }
  }
}

const performSearch = () => {
  searchQuery.value = searchFilters.value.query || ''

  // Clean up empty values
  const cleanFilters: NoteSearchRequest = {}

  if (searchFilters.value.query?.trim()) {
    cleanFilters.query = searchFilters.value.query.trim()
  }
  if (searchFilters.value.category?.trim()) {
    cleanFilters.category = searchFilters.value.category.trim()
  }
  if (searchFilters.value.tags && searchFilters.value.tags.length > 0) {
    cleanFilters.tags = searchFilters.value.tags
  }
  if (searchFilters.value.is_favorite !== undefined) {
    cleanFilters.is_favorite = searchFilters.value.is_favorite
  }
  if (searchFilters.value.is_archived !== undefined) {
    cleanFilters.is_archived = searchFilters.value.is_archived
  }
  if (searchFilters.value.start_date?.trim()) {
    cleanFilters.start_date = searchFilters.value.start_date.trim()
  }
  if (searchFilters.value.end_date?.trim()) {
    cleanFilters.end_date = searchFilters.value.end_date.trim()
  }
  if (searchFilters.value.week_number !== undefined && searchFilters.value.week_number !== null) {
    cleanFilters.week_number = searchFilters.value.week_number
  }

  emit('search', cleanFilters)
}

const clearSearch = () => {
  searchFilters.value = {
    query: '',
    category: '',
    tags: [],
    week_number: undefined,
    is_favorite: undefined,
    is_archived: undefined,
    start_date: '',
    end_date: '',
  }
  searchQuery.value = ''
  tagInput.value = ''
  emit('clear')
}

const clearAllFilters = () => {
  clearSearch()
}

const clearFilter = (filterKey: keyof NoteSearchRequest) => {
  if (filterKey === 'tags') {
    searchFilters.value.tags = []
  } else if (
    filterKey === 'query' ||
    filterKey === 'category' ||
    filterKey === 'start_date' ||
    filterKey === 'end_date'
  ) {
    ;(searchFilters.value[filterKey] as string) = ''
  } else {
    searchFilters.value[filterKey] = undefined
  }
  handleFilterChange()
}

const clearDateRange = () => {
  searchFilters.value.start_date = ''
  searchFilters.value.end_date = ''
  handleFilterChange()
}

const clearSearchError = () => {
  // Emit an event to parent to clear error
  emit('search', searchFilters.value)
}

const handleFilterChange = () => {
  emit('filters-change', searchFilters.value)
  if (props.autoSearch) {
    handleSearchInput()
  }
}

const toggleQuickFilter = (filterKey: 'is_favorite' | 'is_archived', value: boolean) => {
  const currentValue = searchFilters.value[filterKey]
  searchFilters.value[filterKey] = currentValue === value ? undefined : value
  handleFilterChange()
}

const addTag = () => {
  const tag = tagInput.value.trim().toLowerCase()
  if (tag && searchFilters.value.tags && !searchFilters.value.tags.includes(tag)) {
    searchFilters.value.tags.push(tag)
    tagInput.value = ''
    handleFilterChange()
  } else if (tag && !searchFilters.value.tags) {
    searchFilters.value.tags = [tag]
    tagInput.value = ''
    handleFilterChange()
  }
}

const handleTagKeydown = (event: KeyboardEvent) => {
  if (event.key === ',' || event.key === 'Comma') {
    event.preventDefault()
    addTag()
  }
  tagInput.value = ''
}

const removeTag = (tag: string) => {
  if (searchFilters.value.tags) {
    searchFilters.value.tags = searchFilters.value.tags.filter((t) => t !== tag)
    handleFilterChange()
  }
}

const formatDateRange = (): string => {
  const start = searchFilters.value.start_date
  const end = searchFilters.value.end_date

  if (start && end) {
    return `${start} to ${end}`
  } else if (start) {
    return `from ${start}`
  } else if (end) {
    return `until ${end}`
  }
  return ''
}

// Focus search input on mount
onMounted(() => {
  if (searchInput.value) {
    searchInput.value.focus()
  }
})

// Watch for external changes to reset internal state
watch(
  () => props.searchResults,
  () => {
    if (searchTimeout) {
      clearTimeout(searchTimeout)
      searchTimeout = null
    }
  },
)
</script>

<style scoped>
/* CSS Variables */
:root {
  --search-bg: #ffffff;
  --search-border: #e2e8f0;
  --search-text-primary: #1a202c;
  --search-text-secondary: #718096;
  --search-text-muted: #a0aec0;
  --search-primary: #3182ce;
  --search-hover: #f7fafc;
  --search-active: #bee3f8;
  --search-error: #e53e3e;
  --search-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --search-border-radius: 0.5rem;
  --search-transition: all 0.2s ease;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --search-bg: #2d3748;
    --search-border: #4a5568;
    --search-text-primary: #f7fafc;
    --search-text-secondary: #a0aec0;
    --search-text-muted: #718096;
    --search-primary: #63b3ed;
    --search-hover: #4a5568;
    --search-active: #2c5282;
  }
}

/* Notes Search Container */
.notes-search {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem 3rem;
  background-color: var(--search-bg);
  border: 1px solid var(--search-border);
  border-radius: var(--search-border-radius);
  box-shadow: var(--search-shadow);
}

/* Search Header */
.search-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-title-section {
  flex: 1;
  min-width: 0;
}

.search-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--search-text-primary);
}

.search-results-count {
  margin: 0;
  font-size: 0.875rem;
  color: var(--search-text-secondary);
}

.search-query {
  font-weight: 500;
  color: var(--search-primary);
}

.search-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.advanced-toggle-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--search-border);
  background-color: var(--search-bg);
  color: var(--search-text-secondary);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: var(--search-transition);
}

.advanced-toggle-button:hover {
  background-color: var(--search-hover);
  color: var(--search-text-primary);
}

.advanced-toggle-button.active {
  background-color: var(--search-primary);
  color: white;
  border-color: var(--search-primary);
}

/* Search Bar */
.search-bar-container {
  display: flex;
  gap: 0.75rem;
  align-items: stretch;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1rem;
  z-index: 1;
  color: var(--search-text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 3rem;
  padding: 0 3rem 0 3rem;
  border-radius: 0.5rem;
  background-color: var(--search-bg);
  color: var(--search-text-primary);
  font-size: 1rem;
  transition: var(--search-transition);
}

.search-input:focus {
  outline: none;
  border-color: var(--search-primary);
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
}

.clear-search-button {
  position: absolute;
  right: 1rem;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border: none;
  background: none;
  color: var(--search-text-muted);
  border-radius: 0.25rem;
  cursor: pointer;
  transition: var(--search-transition);
}

.clear-search-button:hover {
  color: var(--search-text-secondary);
  background-color: var(--search-hover);
}

.search-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 1.5rem;
  height: 3rem;
  background-color: var(--search-primary);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--search-transition);
  white-space: nowrap;
}

.search-button:hover:not(:disabled) {
  background-color: #2c5282;
}

.search-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Quick Filters */
.quick-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.quick-filter-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.quick-filter-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--search-border);
  background-color: var(--search-bg);
  color: var(--search-text-secondary);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: var(--search-transition);
}

.quick-filter-button:hover {
  background-color: var(--search-hover);
  color: var(--search-text-primary);
}

.quick-filter-button.active {
  background-color: var(--search-active);
  color: var(--search-primary);
  border-color: var(--search-primary);
}

/* Advanced Filters */
.advanced-filters-enter-active,
.advanced-filters-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.advanced-filters-enter-from,
.advanced-filters-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-1rem);
}

.advanced-filters {
  padding: 1.5rem;
  background-color: var(--search-hover);
  border-radius: 0.5rem;
  border: 1px solid var(--search-border);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--search-text-primary);
}

.filter-input,
.filter-select {
  padding: 0.75rem;
  border: 1px solid var(--search-border);
  border-radius: 0.375rem;
  background-color: var(--search-bg);
  color: var(--search-text-primary);
  font-size: 0.875rem;
  transition: var(--search-transition);
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: var(--search-primary);
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
}

/* Tags Filter */
.tags-filter-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  min-height: 1.5rem;
}

.selected-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: var(--search-active);
  color: var(--search-primary);
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.remove-tag-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1rem;
  height: 1rem;
  border: none;
  background: none;
  color: var(--search-primary);
  border-radius: 50%;
  cursor: pointer;
  transition: var(--search-transition);
}

.remove-tag-button:hover {
  background-color: var(--search-primary);
  color: white;
}

/* Date Range */
.date-range-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.date-separator {
  font-size: 0.875rem;
  color: var(--search-text-secondary);
  white-space: nowrap;
}

/* Filter Actions */
.filter-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--search-border);
}

/* Active Filters */
.active-filters {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background-color: var(--search-hover);
  border-radius: 0.375rem;
  border: 1px solid var(--search-border);
}

.active-filters-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--search-text-primary);
}

.active-filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.active-filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  background-color: var(--search-primary);
  color: white;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.remove-filter {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  transition: var(--search-transition);
}

.remove-filter:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Search Error */
.search-error {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background-color: #fed7d7;
  color: #c53030;
  border-radius: 0.375rem;
  border: 1px solid #feb2b2;
}

.error-icon {
  flex-shrink: 0;
}

.error-message {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Loading Spinner */
.loading-spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-spinner.small {
  width: 1rem;
  height: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
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
  transition: var(--search-transition);
  text-decoration: none;
  min-height: 2.5rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--search-primary);
}

.btn-primary:hover:not(:disabled) {
  background-color: #2c5282;
}

.btn-secondary {
  background-color: var(--search-hover);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--search-border);
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  min-height: 2rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .notes-search {
    padding: 1rem;
    gap: 1rem;
  }

  .search-header {
    flex-direction: column;
    align-items: stretch;
  }

  .search-bar-container {
    flex-direction: column;
    gap: 0.75rem;
  }

  .search-button {
    width: 100%;
    justify-content: center;
  }

  .filters-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .date-range-container {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-actions {
    flex-direction: column-reverse;
  }

  .active-filters {
    padding: 0.75rem;
  }
}

@media (max-width: 480px) {
  .search-input {
    font-size: 0.875rem;
  }

  .quick-filter-button {
    font-size: 0.8125rem;
    padding: 0.375rem 0.625rem;
  }

  .btn {
    font-size: 0.8125rem;
    padding: 0.625rem 1.25rem;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .advanced-filters-enter-active,
  .advanced-filters-leave-active,
  .search-input,
  .filter-input,
  .filter-select,
  .btn,
  .quick-filter-button,
  .advanced-toggle-button {
    transition: none;
  }

  .loading-spinner {
    animation: none;
  }
}
</style>
