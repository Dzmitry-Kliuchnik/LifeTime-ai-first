<template>
  <article
    class="note-display"
    :class="{
      'note-favorite': note.is_favorite,
      'note-archived': note.is_archived,
      'note-compact': variant === 'compact',
      'note-expanded': variant === 'expanded',
      'note-card': variant === 'card',
    }"
    :aria-labelledby="`note-title-${note.id}`"
  >
    <!-- Note Header -->
    <header class="note-header">
      <div class="note-title-section">
        <h3 :id="`note-title-${note.id}`" class="note-title">
          {{ note.title }}
        </h3>
        <div class="note-metadata">
          <span class="note-date" :title="formatDateFull(note.updated_at)">
            {{ formatDateRelative(note.updated_at) }}
          </span>
        </div>
      </div>

      <div class="note-actions">
        <button
          v-if="showFavoriteAction"
          type="button"
          class="note-action-button favorite-button"
          :class="{ active: note.is_favorite }"
          @click.stop.prevent="handleFavoriteToggle"
          :aria-label="note.is_favorite ? 'Remove from favorites' : 'Add to favorites'"
          :title="note.is_favorite ? 'Remove from favorites' : 'Add to favorites'"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            :fill="note.is_favorite ? 'currentColor' : 'none'"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polygon
              points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"
            />
          </svg>
        </button>

        <button
          v-if="showArchiveAction"
          type="button"
          class="note-action-button archive-button"
          :class="{ active: note.is_archived }"
          @click="handleArchiveToggle"
          :aria-label="note.is_archived ? 'Unarchive note' : 'Archive note'"
          :title="note.is_archived ? 'Unarchive note' : 'Archive note'"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="21,8 21,21 3,21 3,8"></polyline>
            <rect x="1" y="3" width="22" height="5"></rect>
            <line x1="10" y1="12" x2="14" y2="12"></line>
          </svg>
        </button>

        <div v-if="showMoreActions" class="dropdown" ref="dropdown">
          <button
            type="button"
            class="note-action-button dropdown-trigger"
            @click="toggleDropdown"
            :aria-expanded="isDropdownOpen"
            aria-haspopup="true"
            :aria-label="'More actions for ' + note.title"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="1"></circle>
              <circle cx="12" cy="5" r="1"></circle>
              <circle cx="12" cy="19" r="1"></circle>
            </svg>
          </button>

          <div v-if="isDropdownOpen" class="dropdown-menu" role="menu" @click.stop>
            <button
              v-if="showEditAction"
              type="button"
              class="dropdown-item"
              role="menuitem"
              @click="handleEdit"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              Edit Note
            </button>

            <button
              v-if="showDuplicateAction"
              type="button"
              class="dropdown-item"
              role="menuitem"
              @click="handleDuplicate"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              Duplicate Note
            </button>
            <button
              v-if="showDeleteAction"
              type="button"
              class="dropdown-item danger"
              role="menuitem"
              @click="handleDelete"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <polyline points="3,6 5,6 21,6"></polyline>
                <path
                  d="M19,6v14a2,2,0,0,1-2,2H7a2,2,0,0,1-2-2V6M8,6V4a2,2,0,0,1,2-2h4a2,2,0,0,1,2,2V6"
                ></path>
              </svg>
              Delete Note
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Note Content -->
    <div class="note-content">
      <button
        v-if="!isExpanded && variant !== 'expanded'"
        type="button"
        class="note-preview"
        @click="handleExpand"
      >
        {{ truncatedContent }}
        <span v-if="isTruncated" class="read-more">... Read more</span>
      </button>

      <div v-else class="note-full-content">
        <div
          class="note-text"
          :class="{ 'note-text-formatted': preserveFormatting }"
          v-html="formattedContent"
        ></div>

        <button
          v-if="variant !== 'expanded' && canCollapse"
          type="button"
          class="collapse-button"
          @click="handleCollapse"
        >
          Show less
        </button>
      </div>
    </div>

    <!-- Note Tags -->
    <div v-if="note.tags && note.tags.length > 0" class="note-tags">
      <button
        v-for="tag in note.tags"
        :key="tag"
        type="button"
        class="note-tag"
        @click="handleTagClick(tag)"
      >
        #{{ tag }}
      </button>
    </div>

    <!-- Note Footer -->
    <footer v-if="showFooter" class="note-footer">
      <div class="note-stats">
        <span v-if="note.word_count" class="note-stat" title="Word count">
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14,2 14,8 20,8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10,9 9,9 8,9"></polyline>
          </svg>
          words: {{ note.word_count }}
        </span>

        <span v-if="note.reading_time" class="note-stat" title="Estimated reading time">
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12,6 12,12 16,14"></polyline>
          </svg>
          {{ note.reading_time }} min read
        </span>
      </div>

      <div class="note-dates">
        <span class="note-created" title="Created">
          Created {{ formatDateRelative(note.created_at) }}
        </span>
        <span v-if="note.updated_at !== note.created_at" class="note-updated" title="Last updated">
          Updated {{ formatDateRelative(note.updated_at) }}
        </span>
      </div>
    </footer>

    <!-- Loading Overlay -->
    <div v-if="isLoading" class="note-loading-overlay">
      <div class="loading-spinner"></div>
    </div>

    <!-- Week Information Modal -->
    <div
      v-if="showWeekModal"
      class="week-modal-overlay"
      @click="showWeekModal = false"
      @keydown.esc="showWeekModal = false"
    >
      <dialog class="week-modal" @click.stop :aria-labelledby="`week-modal-title-${note.id}`" open>
        <div class="week-modal-header">
          <h3 :id="`week-modal-title-${note.id}`" class="week-modal-title">
            Week {{ note.week_number }}
          </h3>
          <button
            type="button"
            class="week-modal-close"
            @click="showWeekModal = false"
            aria-label="Close week information"
          >
            <svg
              width="20"
              height="20"
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

        <div class="week-modal-content">
          <div v-if="weekInfo" class="week-info">
            <div class="week-info-item">
              <span class="week-info-label">Week Type:</span>
              <span class="week-info-value" :class="`week-type-${weekInfo.type}`">
                {{ weekInfo.typeLabel }}
              </span>
            </div>

            <div class="week-info-item">
              <span class="week-info-label">Date Range:</span>
              <span class="week-info-value">
                {{ weekInfo.startDate }} - {{ weekInfo.endDate }}
              </span>
            </div>

            <div class="week-info-item">
              <span class="week-info-label">Week Number:</span>
              <span class="week-info-value"> {{ note.week_number }} of your lifetime </span>
            </div>
          </div>

          <div v-else class="week-info-error">
            <p>Unable to calculate detailed week information.</p>
            <p>Week {{ note.week_number }}</p>
          </div>
        </div>
      </dialog>
    </div>
  </article>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { NoteResponse } from '@/types'
import { useWeekCalculationStore } from '@/stores/week-calculation'
import { useUserStore } from '@/stores/user'

interface Props {
  note: NoteResponse
  variant?: 'compact' | 'card' | 'expanded'
  maxPreviewLength?: number
  preserveFormatting?: boolean
  showFavoriteAction?: boolean
  showArchiveAction?: boolean
  showEditAction?: boolean
  showDuplicateAction?: boolean
  showDeleteAction?: boolean
  showMoreActions?: boolean
  showFooter?: boolean
  isLoading?: boolean
  clickableExpand?: boolean
  clickableTags?: boolean
}

interface Emits {
  (e: 'favorite-toggle', note: NoteResponse): void
  (e: 'favorite', note: NoteResponse): void // Legacy alias for tests
  (e: 'archive-toggle', note: NoteResponse): void
  (e: 'archive', note: NoteResponse): void // Legacy alias for tests
  (e: 'edit', note: NoteResponse): void
  (e: 'duplicate', note: NoteResponse): void
  (e: 'delete', note: NoteResponse): void
  (e: 'tag-click', tag: string, note: NoteResponse): void
  (e: 'expand', note: NoteResponse): void
  (e: 'collapse', note: NoteResponse): void
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'card',
  maxPreviewLength: 300,
  preserveFormatting: false,
  showFavoriteAction: true,
  showArchiveAction: true,
  showEditAction: true,
  showDuplicateAction: true,
  showDeleteAction: true,
  showMoreActions: true,
  showFooter: true,
  isLoading: false,
  clickableExpand: true,
  clickableTags: true,
})

const emit = defineEmits<Emits>()

// Stores
const weekCalculationStore = useWeekCalculationStore()
const userStore = useUserStore()

// Component state
const isExpanded = ref(false)
const isDropdownOpen = ref(false)
const showWeekModal = ref(false)
const dropdown = ref<HTMLElement>()

// Computed properties
const truncatedContent = computed(() => {
  if (props.note.content.length <= props.maxPreviewLength) {
    return props.note.content
  }
  return props.note.content.substring(0, props.maxPreviewLength).trim()
})

const isTruncated = computed(() => {
  return props.note.content.length > props.maxPreviewLength
})

const canCollapse = computed(() => {
  return isTruncated.value && props.clickableExpand
})

const formattedContent = computed(() => {
  if (props.preserveFormatting) {
    // Convert line breaks to HTML breaks and preserve whitespace
    return props.note.content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br>')
      .replace(/ {2}/g, '&nbsp;&nbsp;')
  }
  return props.note.content
})

// Week information for modal
const weekInfo = computed(() => {
  if (props.note.week_number === undefined || !userStore.currentUser?.date_of_birth) {
    return null
  }

  try {
    const weekNumber = props.note.week_number
    const dateOfBirth = userStore.currentUser.date_of_birth

    // Get week date range
    const dateRange = weekCalculationStore.getWeekDateRangeLocal(dateOfBirth, weekNumber)

    // Get week type
    const weekType = weekCalculationStore.getWeekTypeLocal(dateOfBirth, weekNumber)

    if (!dateRange) {
      return null
    }

    const startDate = dateRange.start.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })
    const endDate = dateRange.end.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })

    // Fix nested ternary by extracting to separate logic
    let typeLabel = 'Future Week'
    if (weekType === 'current') {
      typeLabel = 'Current Week'
    } else if (weekType === 'past') {
      typeLabel = 'Past Week'
    }

    return {
      type: weekType,
      typeLabel,
      startDate,
      endDate,
    }
  } catch (error) {
    console.error('Error generating week information:', error)
    return null
  }
})

// Date formatting functions
const formatDateRelative = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInMs = now.getTime() - date.getTime()
  const diffInMinutes = Math.floor(diffInMs / (1000 * 60))
  const diffInHours = Math.floor(diffInMinutes / 60)
  const diffInDays = Math.floor(diffInHours / 24)

  if (diffInMinutes < 1) {
    return 'Just now'
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}m ago`
  } else if (diffInHours < 24) {
    return `${diffInHours}h ago`
  } else if (diffInDays < 7) {
    return `${diffInDays}d ago`
  } else if (diffInDays < 30) {
    const weeks = Math.floor(diffInDays / 7)
    return `${weeks}w ago`
  } else if (diffInDays < 365) {
    const months = Math.floor(diffInDays / 30)
    return `${months}mo ago`
  } else {
    const years = Math.floor(diffInDays / 365)
    return `${years}y ago`
  }
}

const formatDateFull = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

// Event handlers
const handleFavoriteToggle = () => {
  emit('favorite-toggle', props.note)
  // Legacy alias for tests
  emit('favorite', props.note)
}

const handleArchiveToggle = () => {
  emit('archive-toggle', props.note)
  // Legacy alias for tests
  emit('archive', props.note)
}

const handleEdit = () => {
  emit('edit', props.note)
  isDropdownOpen.value = false
}

const handleDuplicate = () => {
  emit('duplicate', props.note)
  isDropdownOpen.value = false
}

const handleDelete = () => {
  const confirmed = window.confirm(
    `Are you sure you want to delete "${props.note.title}"? This action cannot be undone.`,
  )
  if (confirmed) {
    emit('delete', props.note)
  }
  isDropdownOpen.value = false
}

const handleTagClick = (tag: string) => {
  if (props.clickableTags) {
    emit('tag-click', tag, props.note)
  }
}

const handleExpand = () => {
  if (props.clickableExpand && isTruncated.value) {
    isExpanded.value = true
    emit('expand', props.note)
  }
}

const handleCollapse = () => {
  isExpanded.value = false
  emit('collapse', props.note)
}

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const closeDropdown = (event: MouseEvent) => {
  if (dropdown.value && !dropdown.value.contains(event.target as Node)) {
    isDropdownOpen.value = false
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && showWeekModal.value) {
    showWeekModal.value = false
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', closeDropdown)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* CSS Variables */
:root {
  --note-bg: #ffffff;
  --note-border: #e2e8f0;
  --note-text-primary: #1a202c;
  --note-text-secondary: #718096;
  --note-text-muted: #a0aec0;
  --note-link: #3182ce;
  --note-favorite: #f6ad55;
  --note-archive: #9f7aea;
  --note-danger: #e53e3e;
  --note-hover: #f7fafc;
  --note-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  --note-shadow-hover: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --note-border-radius: 0.5rem;
  --note-transition: all 0.2s ease;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --note-bg: #2d3748;
    --note-border: #4a5568;
    --note-text-primary: #f7fafc;
    --note-text-secondary: #a0aec0;
    --note-text-muted: #718096;
    --note-link: #63b3ed;
    --note-hover: #4a5568;
  }
}

/* Note Display Base */
.note-display {
  background-color: var(--note-bg);
  border: 1px solid;
  border-radius: 0.5rem;
  position: relative;
  transition: var(--note-transition);
  overflow: hidden;
}

.note-card {
  box-shadow: var(--note-shadow);
  padding: 1.5rem;
}

.note-card:hover {
  box-shadow: var(--note-shadow-hover);
  transform: translateY(-1px);
}

.note-compact {
  padding: 1rem;
  border-radius: 0.375rem;
}

.note-expanded {
  padding: 2rem;
  border-radius: 0.75rem;
}

.note-favorite {
  border-left: 4px solid;
}

.note-archived {
  opacity: 0.7;
  background-color: var(--note-hover);
}

/* Note Header */
.note-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 1rem;
}

.note-title-section {
  flex: 1;
  min-width: 0;
}

.note-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--note-text-primary);
  line-height: 1.4;
  word-wrap: break-word;
}

.note-compact .note-title {
  font-size: 1.125rem;
  margin-bottom: 0.25rem;
}

.note-expanded .note-title {
  font-size: 1.5rem;
  margin-bottom: 0.75rem;
}

.note-metadata {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: var(--note-text-secondary);
}

.note-date {
  display: inline-block;
}

.note-week-button {
  background-color: var(--note-link);
  color: white;
  padding: 0.125rem 0.5rem;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--note-transition);
  font-family: inherit;
}

.note-week-button:hover {
  background-color: #2c5282;
  transform: translateY(-1px);
}

.note-week-button:focus {
  outline: 2px solid var(--note-link);
  outline-offset: 2px;
}

/* Note Actions */
.note-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-shrink: 0;
}

.note-action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  background: none;
  border-radius: 0.375rem;
  color: var(--note-text-muted);
  cursor: pointer;
  transition: var(--note-transition);
}

.note-action-button:hover {
  background-color: var(--note-hover);
  color: var(--note-text-secondary);
}

.note-action-button:focus {
  outline: 2px solid var(--note-link);
  outline-offset: 2px;
}

.favorite-button.active {
  color: var(--note-favorite);
}

.archive-button.active {
  color: var(--note-archive);
}

/* Dropdown */
.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 70%;
  right: 0;
  z-index: 10;
  min-width: 12rem;
  background-color: white;
  border: 1px solid black;
  border-radius: 0.375rem;
  box-shadow: var(--note-shadow-hover);
  padding: 0.5rem 0;
  margin-top: 0.25rem;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  color: var(--note-text-primary);
  font-size: 0.875rem;
  text-align: left;
  cursor: pointer;
  transition: var(--note-transition);
}

.dropdown-item:hover {
  background-color: var(--note-hover);
}

.dropdown-item.danger {
  color: var(--note-danger);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--note-border);
  margin: 0.5rem 0;
}

/* Note Content */
.note-content {
  margin-bottom: 1rem;
}

.note-preview {
  color: var(--note-text-primary);
  line-height: 1.6;
  cursor: pointer;
  transition: var(--note-transition);
  background: none;
  border: none;
  text-align: left;
  width: 100%;
  padding: 0;
  font-size: inherit;
  font-family: inherit;
}

.note-preview:hover {
  color: var(--note-text-secondary);
}

.note-preview:focus {
  outline: 2px solid var(--note-link);
  outline-offset: 2px;
  border-radius: 0.25rem;
}

.note-full-content {
  color: var(--note-text-primary);
  line-height: 1.6;
}

.note-text-formatted {
  white-space: pre-wrap;
  font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
  font-size: 0.875rem;
}

.read-more {
  color: var(--note-link);
  font-weight: 500;
}

.collapse-button {
  margin-top: 0.75rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--note-border);
  background-color: var(--note-bg);
  color: var(--note-link);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: var(--note-transition);
}

.collapse-button:hover {
  background-color: var(--note-hover);
}

/* Note Tags */
.note-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.note-tag {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: var(--note-border);
  color: var(--note-text-secondary);
  border: none;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--note-transition);
  font-family: inherit;
}

.note-tag:hover {
  background-color: var(--note-link);
  color: white;
}

.note-tag:focus {
  outline: 2px solid var(--note-link);
  outline-offset: 2px;
}

/* Note Footer */
.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--note-border);
  font-size: 0.75rem;
  color: var(--note-text-muted);
}

.note-stats,
.note-dates {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.note-stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Loading Overlay */
.note-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--note-border);
  border-top: 2px solid var(--note-link);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Week Modal Styles */
.week-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.week-modal {
  background-color: var(--note-bg);
  border: 1px solid var(--note-border);
  border-radius: 0.75rem;
  box-shadow: var(--note-shadow-hover);
  max-width: 28rem;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  margin: 0;
  padding: 0;
}

.week-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem 1.5rem;
  border-bottom: 1px solid var(--note-border);
}

.week-modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--note-text-primary);
}

.week-modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  background: none;
  border-radius: 0.375rem;
  color: var(--note-text-muted);
  cursor: pointer;
  transition: var(--note-transition);
}

.week-modal-close:hover {
  background-color: var(--note-hover);
  color: var(--note-text-secondary);
}

.week-modal-close:focus {
  outline: 2px solid var(--note-link);
  outline-offset: 2px;
}

.week-modal-content {
  padding: 1rem 1.5rem 1.5rem 1.5rem;
}

.week-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.week-info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background-color: var(--note-hover);
  border-radius: 0.5rem;
  border: 1px solid var(--note-border);
}

.week-info-label {
  font-weight: 500;
  color: var(--note-text-secondary);
  font-size: 0.875rem;
}

.week-info-value {
  font-weight: 600;
  color: var(--note-text-primary);
  text-align: right;
  font-size: 0.875rem;
}

.week-type-current {
  color: var(--note-link);
}

.week-type-past {
  color: var(--note-text-muted);
}

.week-type-future {
  color: var(--note-favorite);
}

.week-info-error {
  text-align: center;
  color: var(--note-text-muted);
  padding: 2rem 1rem;
}

.week-info-error p {
  margin: 0.5rem 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .note-card,
  .note-expanded {
    padding: 1rem;
  }

  .note-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .note-actions {
    align-self: flex-end;
  }

  .note-metadata {
    gap: 0.5rem;
  }

  .note-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .dropdown-menu {
    right: auto;
    left: 0;
  }

  .week-modal {
    margin: 0.5rem;
    max-width: none;
  }

  .week-modal-header {
    padding: 1rem;
  }

  .week-modal-content {
    padding: 0.75rem 1rem 1rem 1rem;
  }

  .week-info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .week-info-value {
    text-align: left;
  }
}

@media (max-width: 480px) {
  .note-title {
    font-size: 1.125rem;
  }

  .note-expanded .note-title {
    font-size: 1.25rem;
  }

  .note-actions {
    gap: 0.125rem;
  }

  .note-action-button {
    width: 1.75rem;
    height: 1.75rem;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .note-display {
    border: 2px solid currentColor;
  }

  .note-action-button {
    border: 1px solid currentColor;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .note-display,
  .note-action-button,
  .note-tag,
  .collapse-button {
    transition: none;
  }

  .loading-spinner {
    animation: none;
  }
}
</style>
