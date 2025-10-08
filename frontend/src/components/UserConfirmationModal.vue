<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="close">
    <div class="modal-container">
      <div class="modal-header">
        <h2>{{ title }}</h2>
        <button @click="close" class="close-button">&times;</button>
      </div>
      <div class="modal-content">
        <p>{{ message }}</p>
        
        <form @submit.prevent="handleSubmit" class="confirmation-form">
          <div class="form-group">
            <label for="birth-date">Date of Birth:</label>
            <input
              id="birth-date"
              v-model="formData.dateOfBirth"
              type="date"
              required
              class="form-control"
            />
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

const isFormValid = computed(() => {
  return formData.value.dateOfBirth.trim() !== '' && 
         formData.value.lifespan >= 50 && 
         formData.value.lifespan <= 120
})

// Watch for prop changes to populate form data
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      formData.value = {
        dateOfBirth: props.existingDateOfBirth || '',
        lifespan: props.existingLifespan || 80,
      }
    }
  },
  { immediate: true }
)

const close = () => {
  emit('close')
}

const handleSubmit = () => {
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
</style>