<template>
  <teleport to="body">
    <!-- Modal Overlay -->
    <transition name="modal-overlay" appear>
      <div
        v-if="isOpen"
        class="modal-overlay"
        :style="solidOverlayStyles"
        @click="handleOverlayClick"
        :aria-hidden="!isOpen"
      >
        <!-- Drawer/Modal Container -->
        <transition name="modal-content" appear>
          <dialog
            v-if="isOpen"
            ref="modalContent"
            class="modal-content solid-modal"
            :class="[`modal-${variant}`, `modal-${size}`, { 'modal-mobile': isMobile }]"
            :style="solidModalStyles"
            :aria-labelledby="titleId"
            :aria-describedby="descriptionId"
            open
            @click.stop
          >
            <!-- Modal Header -->
            <div class="modal-header" :style="solidModalStyles">
              <div class="modal-header-top">
                <div class="modal-title-section">
                  <h2 v-if="title" :id="titleId" class="modal-title">
                    {{ title }}
                  </h2>
                  <p v-if="description" :id="descriptionId" class="modal-description">
                    {{ description }}
                  </p>
                </div>
                <button
                  v-if="showCloseButton"
                  type="button"
                  class="modal-close-button"
                  @click="close"
                  aria-label="Close modal"
                >
                  <svg
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <!-- Header Actions Slot -->
              <div v-if="$slots.headerActions" class="modal-header-actions">
                <slot name="headerActions" :close="close" :isOpen="isOpen" />
              </div>
            </div>

            <!-- Modal Body -->
            <div class="modal-body" :style="solidModalStyles">
              <slot :close="close" :isOpen="isOpen" />
            </div>

            <!-- Modal Footer -->
            <div v-if="$slots.footer" class="modal-footer" :style="solidModalStyles">
              <slot name="footer" :close="close" :isOpen="isOpen" />
            </div>
          </dialog>
        </transition>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

interface Props {
  isOpen: boolean
  title?: string
  description?: string
  variant?: 'drawer' | 'modal' | 'fullscreen'
  size?: 'small' | 'medium' | 'large' | 'xl'
  closeOnOverlay?: boolean
  closeOnEscape?: boolean
  showCloseButton?: boolean
  persistent?: boolean
  zIndex?: number
}

interface Emits {
  (e: 'update:isOpen', value: boolean): void
  (e: 'close'): void
  (e: 'open'): void
  (e: 'before-close'): void
  (e: 'after-close'): void
  (e: 'before-open'): void
  (e: 'after-open'): void
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'drawer',
  size: 'medium',
  closeOnOverlay: true,
  closeOnEscape: true,
  showCloseButton: true,
  persistent: false,
  zIndex: 1000,
})

const emit = defineEmits<Emits>()

// Template refs
const modalContent = ref<HTMLElement>()

// State
const titleId = ref(`modal-title-${Math.random().toString(36).substr(2, 9)}`)
const descriptionId = ref(`modal-desc-${Math.random().toString(36).substr(2, 9)}`)
const previousActiveElement = ref<HTMLElement | null>(null)

// Computed
const isMobile = computed(() => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 768
})

// Solid modal styles to force opacity
const solidModalStyles = computed(() => ({
  backgroundColor: '#ffffff',
  opacity: '1',
  backdropFilter: 'none',
  WebkitBackdropFilter: 'none',
}))

const solidOverlayStyles = computed(() => ({
  backgroundColor: 'rgba(0, 0, 0, 0.95)',
  opacity: '1',
  backdropFilter: 'none',
  WebkitBackdropFilter: 'none',
}))

// Methods
const close = () => {
  if (props.persistent) return

  emit('before-close')
  emit('update:isOpen', false)
  emit('close')

  nextTick(() => {
    emit('after-close')
  })
}

const open = () => {
  emit('before-open')
  emit('update:isOpen', true)
  emit('open')

  nextTick(() => {
    emit('after-open')
  })
}

const handleOverlayClick = () => {
  if (props.closeOnOverlay && !props.persistent) {
    close()
  }
}

const handleEscapeKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.closeOnEscape && props.isOpen && !props.persistent) {
    close()
  }
}

const handleTabKey = (event: KeyboardEvent) => {
  if (!props.isOpen || !modalContent.value) return

  const focusableElements = modalContent.value.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
  ) as NodeListOf<HTMLElement>

  const firstFocusable = focusableElements[0]
  const lastFocusable = focusableElements[focusableElements.length - 1]

  if (event.key === 'Tab') {
    if (event.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstFocusable) {
        event.preventDefault()
        lastFocusable?.focus()
      }
    } else if (document.activeElement === lastFocusable) {
      // Tab
      event.preventDefault()
      firstFocusable?.focus()
    }
  }
}

const trapFocus = () => {
  if (!props.isOpen || !modalContent.value) return

  const focusableElements = modalContent.value.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
  ) as NodeListOf<HTMLElement>

  if (focusableElements.length > 0) {
    focusableElements[0]?.focus()
  } else {
    modalContent.value.focus()
  }
}

const restoreFocus = () => {
  if (previousActiveElement.value) {
    previousActiveElement.value.focus()
    previousActiveElement.value = null
  }
}

// Watchers
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      // Store current active element
      previousActiveElement.value = document.activeElement as HTMLElement

      // Prevent body scroll
      document.body.style.overflow = 'hidden'

      // Add event listeners
      document.addEventListener('keydown', handleEscapeKey)
      document.addEventListener('keydown', handleTabKey)

      // Focus trap
      nextTick(() => {
        trapFocus()
      })
    } else {
      // Restore body scroll
      document.body.style.overflow = ''

      // Remove event listeners
      document.removeEventListener('keydown', handleEscapeKey)
      document.removeEventListener('keydown', handleTabKey)

      // Restore focus
      restoreFocus()
    }
  },
)

// Lifecycle
onMounted(() => {
  // Set z-index if provided
  if (props.zIndex !== 1000) {
    document.documentElement.style.setProperty('--modal-z-index', props.zIndex.toString())
  }
})

onUnmounted(() => {
  // Clean up body styles
  if (props.isOpen) {
    document.body.style.overflow = ''
  }

  // Remove event listeners
  document.removeEventListener('keydown', handleEscapeKey)
  document.removeEventListener('keydown', handleTabKey)

  // Restore focus if needed
  restoreFocus()
})

// Expose methods for parent components
defineExpose({
  close,
  open,
  focus: trapFocus,
})
</script>

<style scoped>
/* CSS Variables for theming */
:root {
  --modal-z-index: 2147483647;
  --modal-overlay-bg: rgba(0, 0, 0, 0.9);
  --modal-bg: #ffffff !important; /* Force completely solid white background */
  --modal-border-radius: 0.75rem;
  --modal-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
  --modal-border: 4px solid #4a5568;
  --modal-header-border: 1px solid #e2e8f0;
  --modal-text-primary: #1a202c;
  --modal-text-secondary: #718096;
  --modal-close-hover: #f7fafc;
  --modal-transition-duration: 0.3s;
}

/* Dark mode variables */
@media (prefers-color-scheme: dark) {
  :root {
    --modal-overlay-bg: rgba(0, 0, 0, 0.95);
    --modal-bg: #2d3748 !important; /* Force solid dark background */
    --modal-border: 4px solid #a0aec0;
    --modal-header-border: 1px solid #4a5568;
    --modal-text-primary: #f7fafc;
    --modal-text-secondary: #a0aec0;
    --modal-close-hover: #4a5568;
  }
}

/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  background-color: var(--modal-overlay-bg);
  z-index: var(--modal-z-index) !important;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Ensure overlay is fully visible */
  opacity: 1 !important;
  /* Force it to be above everything */
  isolation: isolate;
}

/* Modal Content Base */
.modal-content {
  background-color: var(--modal-bg) !important;
  border-radius: var(--modal-border-radius);
  box-shadow: var(--modal-shadow);
  border: var(--modal-border) !important;
  display: flex;
  flex-direction: column;
  max-height: 80vh;
  min-height: auto;
  overflow: hidden;
  position: relative !important;
  opacity: 1 !important; /* Force modal content to be fully opaque */
  z-index: 2147483647 !important; /* Ensure content is above everything */
  /* Force solid styling to prevent any transparency */
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

/* Modal Variants */
.modal-modal {
  margin: 1rem;
  width: 100%;
  max-width: var(--modal-max-width, 32rem);
  max-height: 65vh;
}

.modal-drawer {
  position: fixed;
  top: 0;
  right: 0;
  max-height: none;
  border-radius: 0;
  border-right: none;
  border-top: none;
  border-bottom: none;
  box-shadow:
    -4px 0 15px -3px rgba(0, 0, 0, 0.1),
    -2px 0 6px -2px rgba(0, 0, 0, 0.05);
}

.modal-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  max-height: none;
  border-radius: 0;
  border: none;
  margin: 0;
}

/* Modal Sizes */
.modal-small {
  --modal-max-width: 24rem;
  --modal-drawer-width: 24rem;
}

.modal-medium {
  --modal-max-width: 32rem;
  --modal-drawer-width: 32rem;
}

.modal-large {
  --modal-max-width: 44rem;
  --modal-drawer-width: 40rem;
}

.modal-xl {
  --modal-max-width: 64rem;
  --modal-drawer-width: 48rem;
}

.modal-drawer.modal-small,
.modal-drawer.modal-medium,
.modal-drawer.modal-large,
.modal-drawer.modal-xl {
  width: var(--modal-drawer-width);
}

/* Mobile Responsiveness */
.modal-mobile.modal-modal {
  margin: 0.5rem;
  border-radius: 0.5rem;
  max-height: 95vh;
}

.modal-mobile.modal-drawer {
  width: 100vw;
  border-radius: 0;
}

/* Modal Header */
.modal-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 0.75rem 1.25rem 0.5rem 1.25rem;
  border-bottom: var(--modal-header-border);
  flex-shrink: 0;
  background-color: var(--modal-bg) !important;
  opacity: 1 !important;
}

.modal-header-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.modal-title-section {
  flex: 1;
  margin-right: 1rem;
}

.modal-header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 0.5rem;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--modal-text-primary);
  line-height: 1.4;
}

.modal-description {
  margin: 0.5rem 0 0 0;
  font-size: 0.875rem;
  color: var(--modal-text-secondary);
  line-height: 1.4;
}

.modal-close-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  background: none;
  border-radius: 0.375rem;
  color: var(--modal-text-secondary);
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    color 0.2s ease;
  flex-shrink: 0;
}

.modal-close-button:hover {
  background-color: var(--modal-close-hover);
  color: var(--modal-text-primary);
}

.modal-close-button:focus {
  outline: 2px solid #3182ce;
  outline-offset: 2px;
}

/* Modal Body */
.modal-body {
  flex: 1;
  padding: 0;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 400px;
  /* Force modal body to have completely solid background */
  background-color: var(--modal-bg) !important;
  opacity: 1 !important;
  /* Force solid appearance */
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

/* Modal Footer */
.modal-footer {
  padding: 0.75rem 1.5rem 1rem 1.5rem;
  border-top: var(--modal-header-border);
  flex-shrink: 0;
  background-color: var(--modal-bg) !important;
  opacity: 1 !important;
}

/* Transitions */
.modal-overlay-enter-active,
.modal-overlay-leave-active {
  transition: opacity var(--modal-transition-duration) ease;
}

.modal-overlay-enter-from,
.modal-overlay-leave-to {
  opacity: 0;
}

.modal-content-enter-active,
.modal-content-leave-active {
  transition: all var(--modal-transition-duration) ease;
}

/* Modal transition */
.modal-modal.modal-content-enter-from,
.modal-modal.modal-content-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-1rem);
}

/* Drawer transition */
.modal-drawer.modal-content-enter-from,
.modal-drawer.modal-content-leave-to {
  transform: translateX(100%);
}

/* Fullscreen transition */
.modal-fullscreen.modal-content-enter-from,
.modal-fullscreen.modal-content-leave-to {
  opacity: 0;
  transform: scale(0.98);
}

/* Anti-transparency utility classes */
dialog.modal-content,
dialog.modal-content *,
.modal-content *,
.modal-header *,
.modal-body *,
.modal-footer * {
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

dialog.modal-content,
.modal-content,
.modal-header,
.modal-body,
.modal-footer {
  background-color: var(--modal-bg) !important;
  opacity: 1 !important;
}

/* Force dialog element to be completely solid */
dialog[open] {
  background-color: var(--modal-bg) !important;
  opacity: 1 !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  border: 5px solid hsl(253, 72%, 51%) !important; /* Red border for high visibility */
}

/* Solid modal class - maximum opacity enforcement */
.solid-modal {
  background-color: #ffffff !important;
  opacity: 1 !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  border: 5px solid hsl(253, 72%, 51%) !important; /* Red border for high visibility */
  border-radius: 0.75rem !important;
  /* Override CSS variables locally */
  --modal-bg: #ffffff !important;
  --modal-overlay-bg: rgba(0, 0, 0, 0.95) !important;
}

.solid-modal,
.solid-modal * {
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.solid-modal > *,
.solid-modal .modal-header,
.solid-modal .modal-body,
.solid-modal .modal-footer {
  background-color: #ffffff !important;
  opacity: 1 !important;
}

/* Nuclear option - force everything to be solid */
[class*='modal'] {
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.modal-overlay,
.modal-content,
.modal-header,
.modal-body,
.modal-footer,
dialog {
  background-color: unset;
  background-color: #ffffff !important;
  opacity: 1 !important;
}

/* Scrollbar styling */
.modal-body::-webkit-scrollbar {
  width: 0.5rem;
}

.modal-body::-webkit-scrollbar-track {
  background: var(--modal-bg);
}

.modal-body::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 0.25rem;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

@media (prefers-color-scheme: dark) {
  .modal-body::-webkit-scrollbar-thumb {
    background: #4a5568;
  }

  .modal-body::-webkit-scrollbar-thumb:hover {
    background: #718096;
  }
}

/* Focus management */
.modal-content:focus {
  outline: none;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .modal-content {
    max-height: 75vh;
    margin: 0.5rem;
    min-width: 300px;
  }

  .modal-body {
    max-height: 55vh;
    padding: 0.5rem 1rem;
  }

  .modal-header {
    padding: 0.75rem 1rem 0.5rem 1rem;
  }

  .modal-footer {
    padding: 0.5rem 1rem 0.75rem 1rem;
  }

  .modal-title {
    font-size: 1.125rem;
  }

  .modal-description {
    font-size: 0.8125rem;
  }

  /* Make modal sizes wider on mobile for better button visibility */
  .modal-small {
    --modal-max-width: 20rem;
  }

  .modal-medium {
    --modal-max-width: 28rem;
  }

  .modal-large {
    --modal-max-width: 36rem;
  }
}

@media (max-width: 480px) {
  .modal-overlay {
    padding: 0;
  }

  .modal-content {
    margin: 0.25rem;
    min-width: 280px;
    max-width: calc(100vw - 0.5rem);
  }

  .modal-modal {
    margin: 0;
    height: 100vh;
    max-height: none;
    border-radius: 0;
    border: none;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .modal-content {
    border: 2px solid currentColor;
  }

  .modal-close-button {
    border: 1px solid currentColor;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .modal-overlay-enter-active,
  .modal-overlay-leave-active,
  .modal-content-enter-active,
  .modal-content-leave-active {
    transition-duration: 0.1s;
  }

  .modal-close-button {
    transition: none;
  }
}
</style>
