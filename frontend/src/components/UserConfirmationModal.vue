<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="close">
    <div class="modal-container">
      <div class="modal-header">
        <h2>{{ title }}</h2>
        <button @click="close" class="close-button">&times;</button>
      </div>
      <div class="modal-content">
        <p>{{ message }}</p>

        <!-- Toast Notifications -->
        <div v-if="notifications.length > 0" class="notifications-container">
          <transition-group name="notification" tag="div">
            <div
              v-for="notification in notifications"
              :key="notification.id"
              class="notification"
              :class="[
                notification.type,
                notification.type === 'error' ? 'error-notification' : '',
              ]"
            >
              <div class="notification-icon">
                <svg
                  v-if="notification.type === 'error'"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <svg
                  v-else-if="notification.type === 'info'"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="12" x2="12" y2="16"></line>
                </svg>
              </div>
              <div class="notification-content">
                <div class="notification-title">{{ notification.title }}</div>
                <div v-if="notification.message" class="notification-message">
                  {{ notification.message }}
                </div>
              </div>
              <button
                type="button"
                class="notification-close"
                @click="removeNotification(notification.id)"
                aria-label="Close notification"
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
          </transition-group>
        </div>

        <form @submit.prevent="handleSubmit" class="confirmation-form">
          <div class="form-group">
            <label for="birth-date">Date of Birth:</label>
            <input
              id="birth-date"
              v-model="formData.dateOfBirth"
              type="date"
              required
              class="form-control"
              :class="{ 'form-control-error': dateValidationError }"
              @blur="validateDateOfBirth"
              @change="validateDateOfBirth"
            />
            <div v-if="dateValidationError" class="field-error">
              {{ dateValidationError }}
            </div>
          </div>

          <div class="form-group">
            <label for="lifespan">Expected Lifespan (years):</label>
            <input
              id="lifespan"
              v-model.number="formData.lifespan"
              type="number"
              min="50"
              max="120"
              required
              class="form-control"
            />
          </div>

          <div class="modal-actions">
            <button type="button" @click="close" class="btn-outline">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="!isFormValid">
              {{ confirmButtonText }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  isOpen: boolean
  title: string
  message: string
  confirmButtonText?: string
  existingDateOfBirth?: string
  existingLifespan?: number
}

interface UserData {
  dateOfBirth: string
  lifespan: number
}

interface Notification {
  id: string
  type: 'error' | 'info' | 'success'
  title: string
  message?: string
}

const props = withDefaults(defineProps<Props>(), {
  confirmButtonText: 'Continue',
  existingDateOfBirth: '',
  existingLifespan: 80,
})

const emit = defineEmits<{
  close: []
  confirm: [data: UserData]
}>()

const formData = ref<UserData>({
  dateOfBirth: '',
  lifespan: 80,
})

const dateValidationError = ref<string>('')
const notifications = ref<Notification[]>([])

const isFormValid = computed(() => {
  return (
    formData.value.dateOfBirth.trim() !== '' &&
    formData.value.lifespan >= 50 &&
    formData.value.lifespan <= 120 &&
    !dateValidationError.value
  )
})

// Notification system
const showNotification = (type: 'error' | 'info' | 'success', title: string, message?: string) => {
  const notification: Notification = {
    id: Math.random().toString(36).substr(2, 9),
    type,
    title,
    message,
  }

  notifications.value.push(notification)

  // Auto-remove after 5 seconds
  setTimeout(() => {
    removeNotification(notification.id)
  }, 5000)
}

const removeNotification = (id: string) => {
  const index = notifications.value.findIndex((n) => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

// Date validation function
const validateDateOfBirth = () => {
  dateValidationError.value = ''

  if (!formData.value.dateOfBirth) {
    return
  }

  const inputDate = new Date(formData.value.dateOfBirth)
  const today = new Date()

  // Reset time to avoid timezone issues
  today.setHours(0, 0, 0, 0)
  inputDate.setHours(0, 0, 0, 0)

  if (inputDate > today) {
    const errorMessage = `Invalid date of birth: '${formData.value.dateOfBirth}' is in the future. Please provide a date on or before today (${today.toISOString().split('T')[0]}).`
    dateValidationError.value = errorMessage
    showNotification(
      'error',
      'Invalid Date of Birth',
      'The date of birth cannot be in the future. Please select a valid date.',
    )
    return
  }

  // Check for very old dates (before 1900)
  const minDate = new Date('1900-01-01')
  if (inputDate < minDate) {
    const errorMessage = `Invalid date of birth: '${formData.value.dateOfBirth}' is too far in the past. Please provide a date after ${minDate.toISOString().split('T')[0]}.`
    dateValidationError.value = errorMessage
    showNotification(
      'error',
      'Invalid Date of Birth',
      'The date of birth seems unusually old. Please verify the date is correct.',
    )
    return
  }

  // Clear any existing notifications when date is valid
  notifications.value = notifications.value.filter((n) => n.type !== 'error')
}

// Watch for prop changes to populate form data
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      formData.value = {
        dateOfBirth: props.existingDateOfBirth || '',
        lifespan: props.existingLifespan || 80,
      }
      // Clear validation state when modal opens
      dateValidationError.value = ''
      notifications.value = []
    }
  },
  { immediate: true },
)

const close = () => {
  emit('close')
}

const handleSubmit = () => {
  // Validate date before submitting
  validateDateOfBirth()

  if (isFormValid.value) {
    emit('confirm', { ...formData.value })
  }
}
</script>

<style scoped>
.modal-overlay {
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
}

.modal-container {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e5e5;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-button:hover {
  background-color: #f5f5f5;
}

.modal-content {
  padding: 1.5rem;
}

.modal-content p {
  margin-bottom: 1.5rem;
  color: #666;
  line-height: 1.5;
}

.confirmation-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #333;
}

.form-control {
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e5e5;
}

.btn-outline {
  padding: 0.75rem 1.5rem;
  border: 1px solid #ccc;
  background: white;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-outline:hover {
  background-color: #f8f9fa;
  border-color: #999;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Notifications */
.notifications-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1100;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 24rem;
}

.notification {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background-color: white;
  border: 1px solid #e5e5e5;
  border-radius: 0.5rem;
  box-shadow:
    0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05);
  position: absolute;
}

.notification.error {
  border-left: 4px solid #e53e3e;
}

.notification.info {
  border-left: 4px solid #3182ce;
}

.notification-icon {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.notification.error .notification-icon {
  color: #e53e3e;
}

.notification.info .notification-icon {
  color: #3182ce;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 0.25rem;
}

.notification-message {
  font-size: 0.8125rem;
  color: #718096;
  line-height: 1.4;
}

.notification-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border: none;
  background: none;
  color: #718096;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.notification-close:hover {
  background-color: #f8f9fa;
  color: #1a202c;
}

/* Notification Transitions */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* Form Validation */
.form-control-error {
  border-color: #e53e3e !important;
  box-shadow: 0 0 0 2px rgba(229, 62, 62, 0.25) !important;
}

.field-error {
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #e53e3e;
  font-weight: 500;
}
</style>
