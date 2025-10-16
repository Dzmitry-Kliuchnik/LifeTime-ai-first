<!-- Based on: https://github.com/github/awesome-copilot/blob/main/instructions/vuejs3.instructions.md -->
---
description: 'Vue.js 3 with TypeScript development standards and best practices'
applyTo: '**/*.vue, **/*.ts, **/*.js'
---

# Vue.js 3 + TypeScript Development Guidelines

Apply the [general coding guidelines](../copilot-instructions.md) to all frontend code.

## Project Context

- Vue 3.x with **Composition API** as default approach
- **TypeScript** for type safety with strict mode enabled
- **Single File Components** (`.vue`) with `<script setup>` syntax
- **Vite** for build tooling and development server
- **Pinia** for application state management
- **Vue Router 4** for client-side routing
- Follow Vue's official style guide and best practices

## Development Standards

### Architecture Patterns
- Favor the **Composition API** (`<script setup>` and composables) over Options API
- Organize components and composables by feature or domain for scalability
- Separate presentational components (UI-focused) from container components (logic-focused)
- Extract reusable logic into composable functions in `composables/` directory
- Structure Pinia stores by domain with clearly defined state, actions, and getters

### TypeScript Integration
- Enable `strict` mode in `tsconfig.json` for maximum type safety
- Use `<script setup lang="ts">` with `defineProps()` and `defineEmits()`
- Leverage `PropType<T>` for complex prop types and default values
- Use interfaces or type aliases for component props, emits, and state shapes
- Define types for API responses, route parameters, and store state
- Implement generic components and composables where applicable

### Component Design Best Practices
- Adhere to the **Single Responsibility Principle** for components
- Use **PascalCase** for component names and **kebab-case** for file names
- Keep components small and focused on one primary concern
- Use `<script setup>` syntax for better performance and developer experience
- Validate props with TypeScript; avoid runtime prop validation unless necessary
- Favor slots and scoped slots for flexible component composition

### Example Component Structure
```vue
<template>
  <div class="user-profile">
    <UserAvatar :user="user" :size="avatarSize" />
    <div class="user-info">
      <h2>{{ user.name }}</h2>
      <p>{{ user.email }}</p>
      <slot name="actions" :user="user" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { User } from '@/types/user'
import UserAvatar from './UserAvatar.vue'

interface Props {
  user: User
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  compact: false
})

const avatarSize = computed(() => props.compact ? 'small' : 'medium')
</script>

<style scoped>
.user-profile {
  display: flex;
  gap: 1rem;
  padding: 1rem;
}
</style>
```

### State Management with Pinia

#### Store Definition
```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import type { User, CreateUserRequest } from '@/types/user'
import { userApi } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  // State
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters (computed)
  const activeUsers = computed(() => 
    users.value.filter(user => user.isActive)
  )

  // Actions
  async function fetchUsers() {
    loading.value = true
    error.value = null
    try {
      users.value = await userApi.getUsers()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  async function createUser(userData: CreateUserRequest): Promise<User> {
    const newUser = await userApi.createUser(userData)
    users.value.push(newUser)
    return newUser
  }

  return {
    // State
    users: readonly(users),
    currentUser: readonly(currentUser),
    loading: readonly(loading),
    error: readonly(error),
    // Getters
    activeUsers,
    // Actions
    fetchUsers,
    createUser
  }
})
```

### Composition API Patterns

#### Custom Composables
```typescript
// composables/useFetch.ts
import { ref, Ref } from 'vue'

interface UseFetchReturn<T> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<string | null>
  execute: () => Promise<void>
}

export function useFetch<T>(
  fetcher: () => Promise<T>
): UseFetchReturn<T> {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const execute = async () => {
    loading.value = true
    error.value = null
    try {
      data.value = await fetcher()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Fetch failed'
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, execute }
}
```

#### Lifecycle and Watchers
```typescript
<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

const searchQuery = ref('')
const results = ref([])

// Watch with proper cleanup
const stopWatcher = watch(
  searchQuery,
  async (newQuery) => {
    if (newQuery) {
      results.value = await searchApi(newQuery)
    } else {
      results.value = []
    }
  },
  { debounce: 300 }
)

// Lifecycle hooks
onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
  stopWatcher() // Cleanup watchers
})
</script>
```

### Styling Guidelines

#### Scoped Styles and CSS Modules
- Use `<style scoped>` for component-level styles
- Consider CSS Modules for more complex styling needs
- Follow consistent naming conventions (BEM or functional CSS)
- Use CSS custom properties for theming and design tokens
- Implement mobile-first, responsive design patterns

#### Styling Example
```vue
<style scoped>
.user-card {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius);
  background: var(--color-surface);
  box-shadow: var(--shadow-sm);
}

.user-card__header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.user-card__title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

/* Mobile-first responsive */
@media (min-width: 768px) {
  .user-card {
    flex-direction: row;
    align-items: center;
  }
}
</style>
```

### Performance Optimization

#### Component Optimization
```vue
<template>
  <!-- Use v-memo for expensive renders -->
  <UserList 
    v-memo="[users, selectedUserId]"
    :users="users"
    :selected-id="selectedUserId"
  />
  
  <!-- Lazy load components -->
  <Suspense>
    <AsyncUserProfile :user-id="userId" />
    <template #fallback>
      <UserProfileSkeleton />
    </template>
  </Suspense>
</template>

<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

// Lazy load heavy components
const AsyncUserProfile = defineAsyncComponent(
  () => import('./UserProfile.vue')
)
</script>
```

#### Route-Level Code Splitting
```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/views/Home.vue')
    },
    {
      path: '/users',
      component: () => import('@/views/Users.vue')
    }
  ]
})
```

### Data Fetching Patterns

#### API Integration
```typescript
// api/user.ts
import type { User, CreateUserRequest, UpdateUserRequest } from '@/types/user'

class UserApi {
  private baseUrl = '/api/users'

  async getUsers(): Promise<User[]> {
    const response = await fetch(this.baseUrl)
    if (!response.ok) {
      throw new Error(`Failed to fetch users: ${response.statusText}`)
    }
    return response.json()
  }

  async getUserById(id: number): Promise<User> {
    const response = await fetch(`${this.baseUrl}/${id}`)
    if (!response.ok) {
      throw new Error(`User not found: ${id}`)
    }
    return response.json()
  }

  async createUser(userData: CreateUserRequest): Promise<User> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    })
    if (!response.ok) {
      throw new Error(`Failed to create user: ${response.statusText}`)
    }
    return response.json()
  }
}

export const userApi = new UserApi()
```

### Error Handling

#### Global Error Handler
```typescript
// main.ts
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)

app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err)
  console.error('Component:', instance)
  console.error('Error info:', info)
  
  // Send to error reporting service
  errorReportingService.report(err, { instance, info })
}
```

#### Component Error Boundaries
```vue
<template>
  <div>
    <ErrorBoundary @error="handleError">
      <UserDashboard />
    </ErrorBoundary>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ErrorBoundary from '@/components/ErrorBoundary.vue'

const error = ref<string | null>(null)

function handleError(errorInfo: any) {
  error.value = 'Something went wrong. Please try again.'
  console.error('Component error:', errorInfo)
}
</script>
```

### Form Handling and Validation

#### Form with Validation
```vue
<template>
  <form @submit.prevent="handleSubmit">
    <div class="form-group">
      <label for="email">Email</label>
      <input
        id="email"
        v-model="form.email"
        type="email"
        :class="{ 'error': errors.email }"
        @blur="validateField('email')"
      />
      <span v-if="errors.email" class="error-message">
        {{ errors.email }}
      </span>
    </div>
    
    <button type="submit" :disabled="!isFormValid || loading">
      {{ loading ? 'Submitting...' : 'Submit' }}
    </button>
  </form>
</template>

<script setup lang="ts">
import { reactive, computed, ref } from 'vue'
import { z } from 'zod'

const userSchema = z.object({
  email: z.string().email('Invalid email address'),
  name: z.string().min(1, 'Name is required')
})

const form = reactive({
  email: '',
  name: ''
})

const errors = reactive({
  email: '',
  name: ''
})

const loading = ref(false)

const isFormValid = computed(() => 
  !errors.email && !errors.name && form.email && form.name
)

function validateField(field: keyof typeof form) {
  try {
    userSchema.pick({ [field]: true }).parse({ [field]: form[field] })
    errors[field] = ''
  } catch (error) {
    if (error instanceof z.ZodError) {
      errors[field] = error.errors[0].message
    }
  }
}

async function handleSubmit() {
  // Validate all fields
  Object.keys(form).forEach(field => 
    validateField(field as keyof typeof form)
  )
  
  if (!isFormValid.value) return
  
  loading.value = true
  try {
    await userApi.createUser(form)
    // Handle success
  } catch (error) {
    // Handle error
  } finally {
    loading.value = false
  }
}
</script>
```

### Testing Guidelines

#### Component Testing
```typescript
// components/__tests__/UserCard.spec.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import UserCard from '../UserCard.vue'
import type { User } from '@/types/user'

describe('UserCard', () => {
  const mockUser: User = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    isActive: true
  }

  it('displays user information correctly', () => {
    const wrapper = mount(UserCard, {
      props: { user: mockUser }
    })

    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('john@example.com')
  })

  it('emits edit event when edit button is clicked', async () => {
    const wrapper = mount(UserCard, {
      props: { user: mockUser }
    })

    await wrapper.find('[data-testid="edit-button"]').trigger('click')
    
    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')![0]).toEqual([mockUser])
  })
})
```

### Security Best Practices

#### Input Sanitization
```typescript
// utils/sanitize.ts
import DOMPurify from 'dompurify'

export function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html)
}

export function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}
```

#### Secure API Communication
```typescript
// api/client.ts
class ApiClient {
  private async request<T>(
    url: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        ...options.headers
      },
      credentials: 'same-origin' // Include cookies
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return response.json()
  }
}
```

### Accessibility Guidelines

#### Semantic HTML and ARIA
```vue
<template>
  <div role="dialog" aria-labelledby="modal-title" aria-modal="true">
    <h2 id="modal-title">{{ title }}</h2>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="user-name">Name</label>
        <input
          id="user-name"
          v-model="name"
          type="text"
          :aria-invalid="errors.name ? 'true' : 'false'"
          :aria-describedby="errors.name ? 'name-error' : undefined"
        />
        <div 
          v-if="errors.name" 
          id="name-error" 
          role="alert"
          class="error-message"
        >
          {{ errors.name }}
        </div>
      </div>
    </form>
  </div>
</template>
```

#### Focus Management
```typescript
<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'

const modalRef = ref<HTMLElement>()
const firstFocusableElement = ref<HTMLElement>()

onMounted(async () => {
  await nextTick()
  firstFocusableElement.value?.focus()
})

function trapFocus(event: KeyboardEvent) {
  if (event.key === 'Tab') {
    // Implement focus trapping logic
  }
}
</script>
```

## Common Anti-Patterns to Avoid

- Don't use the Options API for new components; prefer Composition API
- Don't mutate props directly; use events or v-model instead
- Don't put business logic directly in components; use composables or stores
- Don't ignore TypeScript errors or use `any` without justification
- Don't use `v-html` with unsanitized user input
- Don't create deep component hierarchies; favor composition
- Don't forget to cleanup event listeners and watchers in `onUnmounted`
- Don't use global state for component-specific state