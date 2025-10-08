<template>
  <form @submit.prevent="handleSubmit" class="notes-form">
    <div class="form-header"></div>

    <div class="form-content">
      <!-- Title Field -->
      <div class="form-group">
        <label for="title" class="form-label required">Title</label>
        <input
          id="title"
          v-model="formData.title"
          type="text"
          class="form-input"
          :class="{ error: errors.title }"
          placeholder="Enter note title"
          required
          maxlength="200"
          @blur="validateTitle"
          @input="clearFieldError('title')"
        />
        <div v-if="errors.title" class="error-message">
          {{ errors.title }}
        </div>
        <div class="character-count">{{ formData.title.length }}/200</div>
      </div>

      <!-- Content Field -->
      <div class="form-group">
        <label for="content" class="form-label required">Content</label>
        <textarea
          id="content"
          v-model="formData.content"
          class="form-textarea"
          :class="{ error: errors.content }"
          placeholder="Write your note content here..."
          rows="10"
          required
          maxlength="10000"
          @blur="validateContent"
          @input="clearFieldError('content')"
        ></textarea>
        <div v-if="errors.content" class="error-message">
          {{ errors.content }}
        </div>
        <div class="character-count">{{ formData.content.length }}/10000</div>
      </div>

      <!-- Category Field -->
      <div class="form-group">
        <label for="category" class="form-label">Category</label>
        <div class="category-input-container">
          <input
            id="category"
            v-model="formData.category"
            type="text"
            class="form-input"
            :class="{ error: errors.category }"
            placeholder="Enter or select category"
            list="categories"
            maxlength="100"
            @blur="validateCategory"
            @input="clearFieldError('category')"
          />
          <datalist id="categories">
            <option v-for="category in availableCategories" :key="category" :value="category">
              {{ category }}
            </option>
          </datalist>
        </div>
        <div v-if="errors.category" class="error-message">
          {{ errors.category }}
        </div>
      </div>

      <!-- Tags Field -->
      <div class="form-group">
        <label for="tags" class="form-label">Tags</label>
        <div class="tags-input-container">
          <div class="tags-list">
            <span v-for="(tag, index) in formData.tags" :key="`tag-${index}`" class="tag-chip">
              {{ tag }}
              <button
                type="button"
                class="tag-remove"
                @click="removeTag(index)"
                :aria-label="`Remove tag ${tag}`"
              >
                ×
              </button>
            </span>
          </div>
          <input
            id="tags"
            v-model="tagInput"
            type="text"
            class="form-input"
            :class="{ error: errors.tags }"
            placeholder="Type tag and press Enter"
            list="tags"
            maxlength="50"
            @keydown.enter.prevent="addTag"
            @keydown="handleTagKeydown"
            @blur="addTag"
            @input="clearFieldError('tags')"
          />
          <datalist id="tags">
            <option v-for="tag in availableTags" :key="tag" :value="tag">
              {{ tag }}
            </option>
          </datalist>
        </div>
        <div v-if="errors.tags" class="error-message">
          {{ errors.tags }}
        </div>
        <div class="helper-text">Press Enter or comma to add tags. Maximum 10 tags.</div>
      </div>

      <!-- Week Number Field -->
      <div class="form-group">
        <label for="weekNumber" class="form-label">Week Number</label>
        <input
          id="weekNumber"
          v-model.number="formData.week_number"
          type="number"
          class="form-input"
          :class="{ error: errors.week_number }"
          placeholder="Week number (optional)"
          :min="0"
          :max="maxWeekNumber"
          @blur="validateWeekNumber"
          @input="clearFieldError('week_number')"
        />
        <div v-if="errors.week_number" class="error-message">
          {{ errors.week_number }}
        </div>
        <div class="helper-text">Current week: {{ currentWeek }}. Maximum: {{ maxWeekNumber }}</div>
      </div>

      <!-- Favorite Toggle -->
      <div class="form-group checkbox-group">
        <label class="checkbox-label">
          <input
            id="favorite"
            v-model="formData.is_favorite"
            type="checkbox"
            class="form-checkbox"
          />
          <span class="checkbox-text">Mark as favorite</span>
        </label>
      </div>

      <!-- Archive Toggle -->
      <div class="form-group checkbox-group">
        <label class="checkbox-label">
          <input
            id="archived"
            v-model="formData.is_archived"
            type="checkbox"
            class="form-checkbox"
          />
          <span class="checkbox-text">Archive this note</span>
        </label>
      </div>
    </div>

    <!-- Form Actions -->
    <div class="form-actions">
      <button
        type="button"
        class="btn btn-secondary"
        @click="handleCancel"
        :disabled="isSubmitting"
      >
        Cancel
      </button>
      <button type="submit" class="btn btn-primary" :disabled="!isFormValid || isSubmitting">
        <span v-if="isSubmitting" class="loading-spinner"></span>
        {{ isEditMode ? 'Update Note' : 'Create Note' }}
      </button>
    </div>

    <!-- General Form Error -->
    <div v-if="generalError" class="form-error">
      {{ generalError }}
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { NoteCreate, NoteUpdate, NoteResponse } from '@/types'
import { useNotesStore } from '@/stores/notes'
import { useWeekCalculationStore } from '@/stores/week-calculation'

interface Props {
  note?: NoteResponse | null
  isEditMode?: boolean
}

interface Emits {
  (e: 'submit', data: NoteCreate | NoteUpdate): void
  (e: 'cancel'): void
  (e: 'success', note: NoteResponse): void
  (e: 'error', error: string): void
}

const props = withDefaults(defineProps<Props>(), {
  note: null,
  isEditMode: false,
})

const emit = defineEmits<Emits>()

// Stores
const notesStore = useNotesStore()
const weekStore = useWeekCalculationStore()

// Form data
const formData = ref<NoteCreate & { week_number?: number }>({
  title: '',
  content: '',
  category: '',
  tags: [] as string[],
  week_number: undefined,
  is_favorite: false,
  is_archived: false,
})

// Form state
const tagInput = ref('')
const isSubmitting = ref(false)
const generalError = ref<string | null>(null)

// Validation errors
const errors = ref<Record<string, string>>({})

// Available options
const availableCategories = computed(() => notesStore.categories)
const availableTags = computed(() => notesStore.tags)

// Week information
const currentWeek = computed(() => weekStore.currentWeek?.current_week_index || 0)
const maxWeekNumber = computed(() => weekStore.totalWeeks?.total_weeks || 5000)

// Form validation
const isFormValid = computed(() => {
  return (
    formData.value.title.trim().length > 0 &&
    formData.value.content.trim().length > 0 &&
    Object.keys(errors.value).length === 0
  )
})

// Initialize form data when note prop changes
watch(
  () => props.note,
  (newNote) => {
    if (newNote && props.isEditMode) {
      formData.value = {
        title: newNote.title,
        content: newNote.content,
        category: newNote.category || '',
        tags: [...(newNote.tags || [])],
        week_number: newNote.week_number || undefined,
        is_favorite: newNote.is_favorite,
        is_archived: newNote.is_archived,
      }
    }
  },
  { immediate: true },
)

// Load categories and tags on mount
onMounted(async () => {
  await Promise.all([
    notesStore.fetchCategories(),
    notesStore.fetchTags(),
    weekStore.calculateCurrentWeek(),
    weekStore.calculateTotalWeeks(),
  ])
})

// Validation functions
const validateTitle = () => {
  const title = formData.value.title.trim()
  if (!title) {
    errors.value.title = 'Title is required'
  } else if (title.length < 3) {
    errors.value.title = 'Title must be at least 3 characters long'
  } else if (title.length > 200) {
    errors.value.title = 'Title must be less than 200 characters'
  } else {
    delete errors.value.title
  }
}

const validateContent = () => {
  const content = formData.value.content.trim()
  if (!content) {
    errors.value.content = 'Content is required'
  } else if (content.length < 10) {
    errors.value.content = 'Content must be at least 10 characters long'
  } else if (content.length > 10000) {
    errors.value.content = 'Content must be less than 10,000 characters'
  } else {
    delete errors.value.content
  }
}

const validateCategory = () => {
  const category = formData.value.category?.trim() || ''
  if (category && category.length > 100) {
    errors.value.category = 'Category must be less than 100 characters'
  } else {
    delete errors.value.category
  }
}

const validateWeekNumber = () => {
  const weekNumber = formData.value.week_number
  if (weekNumber !== undefined && weekNumber !== null) {
    if (weekNumber < 0) {
      errors.value.week_number = 'Week number cannot be negative'
    } else if (weekNumber > currentWeek.value) {
      errors.value.week_number = 'Cannot create notes for future weeks'
    } else if (weekNumber > maxWeekNumber.value) {
      errors.value.week_number = `Week number cannot exceed ${maxWeekNumber.value}`
    } else {
      delete errors.value.week_number
    }
  } else {
    delete errors.value.week_number
  }
}

const validateTags = () => {
  if (formData.value.tags && formData.value.tags.length > 10) {
    errors.value.tags = 'Maximum 10 tags allowed'
  } else {
    delete errors.value.tags
  }
}

const clearFieldError = (field: string) => {
  delete errors.value[field]
  generalError.value = null
}

// Tag management
const addTag = () => {
  const tag = tagInput.value.trim().toLowerCase()
  if (tag && formData.value.tags && !formData.value.tags.includes(tag)) {
    if (formData.value.tags.length < 10) {
      formData.value.tags.push(tag)
      tagInput.value = ''
      validateTags()
    } else {
      errors.value.tags = 'Maximum 10 tags allowed'
    }
  }
  tagInput.value = ''
}

const handleTagKeydown = (event: KeyboardEvent) => {
  if (event.key === ',' || event.key === 'Comma') {
    event.preventDefault()
    addTag()
  }
}

const removeTag = (index: number) => {
  if (formData.value.tags) {
    formData.value.tags.splice(index, 1)
    validateTags()
  }
}

// Form submission
const handleSubmit = async () => {
  // Prevent double submission
  if (isSubmitting.value) {
    return
  }

  // Validate all fields
  validateTitle()
  validateContent()
  validateCategory()
  validateWeekNumber()
  validateTags()

  if (!isFormValid.value) {
    generalError.value = 'Please fix the errors above'
    return
  }

  isSubmitting.value = true
  generalError.value = null

  try {
    // Prepare submission data
    const submitData: NoteCreate | NoteUpdate = {
      title: formData.value.title.trim(),
      content: formData.value.content.trim(),
      category: formData.value.category?.trim() || undefined,
      tags: formData.value.tags && formData.value.tags.length > 0 ? formData.value.tags : undefined,
      week_number: formData.value.week_number || undefined,
      is_favorite: formData.value.is_favorite,
      is_archived: formData.value.is_archived,
    }

    emit('submit', submitData)

    // Let the parent component handle the API call to avoid double submission
    // The parent will call handleFormSuccess or handleFormError which will handle the result
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred'
    generalError.value = errorMessage
    emit('error', errorMessage)
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  resetForm()
  emit('cancel')
}

const resetForm = () => {
  if (!props.isEditMode) {
    formData.value = {
      title: '',
      content: '',
      category: '',
      tags: [],
      week_number: undefined,
      is_favorite: false,
      is_archived: false,
    }
  }
  tagInput.value = ''
  errors.value = {}
  generalError.value = null
  isSubmitting.value = false
}

// Expose methods for parent components
defineExpose({
  resetForm,
  validateForm: () => {
    validateTitle()
    validateContent()
    validateCategory()
    validateWeekNumber()
    validateTags()
    return isFormValid.value
  },
})
</script>

<style scoped>
.notes-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

.form-header {
  border-bottom: 1px solid var(--border-color, #e2e8f0);
  padding-bottom: 1rem;
}

.form-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary, #1a202c);
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-weight: 500;
  font-size: 0.875rem;
}

.form-label.required::after {
  content: ' *';
  color: var(--error-color, #e53e3e);
}

.form-input,
.form-textarea {
  padding: 0.75rem;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 0.375rem;
  font-size: 1rem;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
  background-color: var(--bg-color, #ffffff);
  color: var(--text-primary, #1a202c);
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color, #3182ce);
  box-shadow: 0 0 0 3px var(--primary-color-alpha, rgba(49, 130, 206, 0.1));
}

.form-input.error,
.form-textarea.error {
  border-color: var(--error-color, #e53e3e);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
  font-family: inherit;
}

.character-count {
  font-size: 0.75rem;
  color: var(--text-secondary, #718096);
  align-self: flex-end;
}

.category-input-container,
.tags-input-container {
  position: relative;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  min-height: 1.5rem;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: var(--primary-light, #bee3f8);
  color: var(--primary-dark, #2c5282);
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.tag-remove {
  background: none;
  border: none;
  color: var(--primary-dark, #2c5282);
  cursor: pointer;
  padding: 0;
  width: 1rem;
  height: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 1rem;
  line-height: 1;
}

.tag-remove:hover {
  background-color: var(--primary-dark, #2c5282);
  color: white;
}

.checkbox-group {
  flex-direction: row;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 400;
}

.form-checkbox {
  width: 1rem;
  height: 1rem;
  accent-color: var(--primary-color, #3182ce);
}

.helper-text {
  font-size: 0.75rem;
  color: var(--text-secondary, #718096);
}

.error-message {
  color: var(--error-color, #e53e3e);
  font-size: 0.75rem;
  font-weight: 500;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color, #e2e8f0);
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 2.5rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--primary-color, #3182ce);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-dark, #2c5282);
}

.btn-secondary {
  background-color: var(--gray-light, #f7fafc);
  color: var(--text-primary, #1a202c);
  border: 1px solid var(--border-color, #e2e8f0);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--gray-lighter, #edf2f7);
}

.form-error {
  padding: 0.75rem;
  background-color: var(--error-light, #fed7d7);
  color: var(--error-dark, #c53030);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .notes-form {
    --bg-color: #2d3748;
    --text-primary: #f7fafc;
    --text-secondary: #a0aec0;
    --border-color: #4a5568;
    --primary-color: #63b3ed;
    --primary-dark: #3182ce;
    --primary-light: #2c5282;
    --error-color: #fc8181;
    --error-light: #742a2a;
    --error-dark: #fc8181;
    --gray-light: #4a5568;
    --gray-lighter: #2d3748;
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .notes-form {
    gap: 1rem;
  }

  .form-content {
    gap: 1rem;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .tags-list {
    gap: 0.25rem;
  }

  .tag-chip {
    font-size: 0.6875rem;
  }
}
</style>
