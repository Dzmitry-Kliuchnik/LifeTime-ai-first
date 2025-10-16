---
mode: 'edit'  
description: 'Generate and update documentation for Python FastAPI and Vue.js applications'
---

# Documentation Generation Assistant

You are a documentation specialist for Python FastAPI and Vue.js applications. Generate comprehensive, up-to-date, and user-friendly documentation.

## Documentation Philosophy

### Goals of Good Documentation
- **Clarity** - Easy to understand for intended audience
- **Completeness** - Covers all necessary information
- **Currency** - Always up-to-date with current code
- **Accessibility** - Available to all team members and stakeholders
- **Actionability** - Provides clear next steps for readers

### Documentation Types
- **API Documentation** - Endpoint specifications and examples
- **Component Documentation** - Component usage and props
- **Architecture Documentation** - System design and patterns
- **User Documentation** - End-user guides and tutorials
- **Developer Documentation** - Setup, contribution guidelines
- **Deployment Documentation** - Infrastructure and deployment processes

## API Documentation (FastAPI)

### Automatic OpenAPI Documentation
FastAPI automatically generates OpenAPI documentation. Enhance it with:

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="LifeTime Application API",
    description="Personal life management and note-taking application",
    version="1.0.0",
    contact={
        "name": "Development Team",
        "email": "dev@lifetime-app.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

class UserResponse(BaseModel):
    """User information response model."""
    
    id: int = Field(..., description="Unique user identifier", example=1)
    name: str = Field(..., description="User's full name", example="John Doe")
    email: str = Field(..., description="User's email address", example="john@example.com")
    is_active: bool = Field(..., description="Whether user account is active", example=True)
    created_at: datetime = Field(..., description="Account creation timestamp")

@app.post(
    "/api/v1/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user account with the provided information.",
    response_description="Successfully created user information",
    tags=["Users"],
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "John Doe",
                        "email": "john@example.com",
                        "is_active": True,
                        "created_at": "2023-10-15T10:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid email format"
                    }
                }
            }
        },
        409: {
            "description": "User already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User with this email already exists"
                    }
                }
            }
        }
    }
)
async def create_user(user_data: CreateUserRequest) -> UserResponse:
    """
    Create a new user account.
    
    This endpoint creates a new user with the provided information.
    The email must be unique across the system.
    
    Args:
        user_data: User creation data including name, email, and optional fields
        
    Returns:
        UserResponse: The created user information
        
    Raises:
        HTTPException: 400 if validation fails, 409 if user already exists
        
    Example:
        ```python
        import httpx
        
        response = httpx.post(
            "http://localhost:8000/api/v1/users",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "age": 25
            }
        )
        
        if response.status_code == 201:
            user = response.json()
            print(f"Created user: {user['name']}")
        ```
    """
    # Implementation here...
```

### API Documentation Best Practices
```python
# Include comprehensive docstrings
class NoteService:
    """
    Service for managing user notes and related operations.
    
    This service handles all business logic related to notes including:
    - Creating, updating, and deleting notes
    - Managing note tags and categories
    - Note search and filtering
    - Note sharing and permissions
    
    Attributes:
        note_repository: Repository for note data access
        tag_service: Service for managing note tags
        
    Example:
        ```python
        note_service = NoteService(note_repository, tag_service)
        note = await note_service.create_note(user_id, note_data)
        ```
    """
    
    async def create_note(
        self, 
        user_id: int, 
        note_data: CreateNoteRequest
    ) -> Note:
        """
        Create a new note for the specified user.
        
        Args:
            user_id: ID of the user creating the note
            note_data: Note creation data including title, content, and tags
            
        Returns:
            Note: The created note object
            
        Raises:
            ValueError: If user_id is invalid or note_data is malformed
            PermissionError: If user doesn't have permission to create notes
            
        Example:
            ```python
            note_data = CreateNoteRequest(
                title="Meeting Notes",
                content="Discussion about project timeline",
                tags=["work", "project"]
            )
            note = await note_service.create_note(123, note_data)
            ```
        """
        # Implementation...
```

## Component Documentation (Vue.js)

### Component Documentation Template
```vue
<!--
# UserCard Component

A reusable component for displaying user information in a card format.

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| user | User | Yes | - | User object to display |
| compact | boolean | No | false | Whether to show compact view |
| editable | boolean | No | true | Whether edit actions are available |

## Events

| Event | Payload | Description |
|-------|---------|-------------|
| edit | User | Emitted when edit button is clicked |
| delete | number | Emitted when delete is confirmed (user ID) |
| view | number | Emitted when user card is clicked (user ID) |

## Slots

| Slot | Description |
|------|-------------|
| actions | Custom action buttons (replaces default edit/delete) |
| avatar | Custom avatar content |

## Examples

### Basic Usage
```vue
<UserCard 
  :user="user" 
  @edit="handleEdit" 
  @delete="handleDelete" 
/>
```

### Compact Mode
```vue
<UserCard 
  :user="user" 
  compact 
  :editable="false" 
/>
```

### With Custom Actions
```vue
<UserCard :user="user">
  <template #actions>
    <button @click="sendMessage">Message</button>
    <button @click="viewProfile">Profile</button>
  </template>
</UserCard>
```

## Accessibility

This component follows WCAG 2.1 AA guidelines:
- Uses semantic HTML structure
- Includes proper ARIA labels and roles
- Supports keyboard navigation
- Maintains proper color contrast ratios

## Related Components

- `UserList` - For displaying multiple users
- `UserProfile` - For detailed user information
- `UserForm` - For editing user data
-->

<template>
  <div 
    class="user-card"
    :class="cardClasses"
    role="article"
    :aria-labelledby="`user-${user.id}-name`"
    tabindex="0"
    @click="handleView"
    @keydown.enter="handleView"
    @keydown.space.prevent="handleView"
  >
    <slot name="avatar">
      <img 
        :src="user.avatar || defaultAvatar"
        :alt="`${user.name} avatar`"
        class="user-card__avatar"
        @error="handleAvatarError"
      />
    </slot>
    
    <div class="user-card__content">
      <h3 :id="`user-${user.id}-name`" class="user-card__name">
        {{ user.name }}
      </h3>
      
      <p v-if="!compact" class="user-card__email">
        {{ user.email }}
      </p>
      
      <div v-if="editable" class="user-card__actions">
        <slot name="actions">
          <button 
            type="button"
            class="btn btn--small btn--primary"
            :aria-label="`Edit ${user.name}`"
            @click.stop="handleEdit"
          >
            Edit
          </button>
          <button 
            type="button"
            class="btn btn--small btn--danger"
            :aria-label="`Delete ${user.name}`"
            @click.stop="handleDelete"
          >
            Delete
          </button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * UserCard - A reusable component for displaying user information
 * 
 * @component
 * @example
 * <UserCard :user="user" @edit="handleEdit" />
 */

import { computed, ref } from 'vue'
import type { User } from '@/types/user'

interface Props {
  /** User object to display */
  user: User
  /** Show compact version without email */
  compact?: boolean
  /** Show edit/delete actions */
  editable?: boolean
}

interface Emits {
  /** Emitted when edit button is clicked */
  edit: [user: User]
  /** Emitted when delete button is clicked */
  delete: [userId: number]
  /** Emitted when card is clicked */
  view: [userId: number]
}

const props = withDefaults(defineProps<Props>(), {
  compact: false,
  editable: true
})

const emit = defineEmits<Emits>()

// Component logic...
</script>
```

### Composable Documentation
```typescript
/**
 * useUsers - Composable for managing user data and operations
 * 
 * Provides reactive user state management including fetching, caching,
 * and CRUD operations with proper error handling and loading states.
 * 
 * @returns {Object} User management interface
 * 
 * @example
 * ```vue
 * <script setup>
 * import { useUsers } from '@/composables/useUsers'
 * 
 * const { 
 *   users, 
 *   loading, 
 *   error, 
 *   fetchUsers, 
 *   createUser 
 * } = useUsers()
 * 
 * // Fetch users on component mount
 * onMounted(() => {
 *   fetchUsers()
 * })
 * 
 * // Create new user
 * const handleCreate = async (userData) => {
 *   try {
 *     await createUser(userData)
 *     console.log('User created successfully')
 *   } catch (error) {
 *     console.error('Failed to create user:', error)
 *   }
 * }
 * </script>
 * ```
 * 
 * @since 1.0.0
 */
export function useUsers() {
  const users = ref<User[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Fetch all users from the API
   * 
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number for pagination
   * @param {number} params.limit - Number of users per page
   * @param {string} params.search - Search term for filtering
   * 
   * @throws {Error} When API request fails
   * 
   * @example
   * ```typescript
   * // Fetch first page
   * await fetchUsers({ page: 1, limit: 20 })
   * 
   * // Search users
   * await fetchUsers({ search: 'john' })
   * ```
   */
  async function fetchUsers(params: FetchUsersParams = {}) {
    // Implementation...
  }

  /**
   * Create a new user
   * 
   * @param {CreateUserRequest} userData - User creation data
   * @returns {Promise<User>} The created user
   * 
   * @throws {ValidationError} When user data is invalid
   * @throws {ConflictError} When user already exists
   */
  async function createUser(userData: CreateUserRequest): Promise<User> {
    // Implementation...
  }

  return {
    // State (readonly for external access)
    users: readonly(users),
    loading: readonly(loading),
    error: readonly(error),
    
    // Actions
    fetchUsers,
    createUser,
    updateUser,
    deleteUser
  }
}
```

## Architecture Documentation

### System Overview
```markdown
# LifeTime Application Architecture

## Overview

LifeTime is a personal life management application built with a modern fullstack architecture:

- **Backend**: Python FastAPI with SQLAlchemy ORM
- **Frontend**: Vue.js 3 with TypeScript and Pinia
- **Database**: SQLite with optional encryption
- **Deployment**: Docker containers with CI/CD pipeline

## System Architecture

```mermaid
graph TB
    Client[Web Browser] --> Frontend[Vue.js Frontend]
    Frontend --> API[FastAPI Backend]
    API --> DB[(SQLite Database)]
    API --> Cache[Redis Cache]
    API --> Queue[Task Queue]
```

## Backend Architecture

### Layered Architecture Pattern

```
app/
├── api/          # HTTP layer (routes, endpoints)
├── services/     # Business logic layer
├── repositories/ # Data access layer
├── models/       # Database models
├── schemas/      # Request/response models
└── core/         # Configuration, database, logging
```

### Key Design Patterns

1. **Repository Pattern** - Abstracts data access
2. **Service Layer** - Contains business logic
3. **Dependency Injection** - Manages component dependencies
4. **Schema Validation** - Pydantic for request/response validation

## Frontend Architecture

### Component-Based Architecture

```
src/
├── components/   # Reusable UI components
├── composables/  # Shared reactive logic
├── stores/       # Pinia state management
├── views/        # Page-level components
├── types/        # TypeScript type definitions
└── utils/        # Utility functions
```

### State Management

- **Local State** - Vue's reactive system for component state
- **Global State** - Pinia stores for shared application state
- **Server State** - Composables for API data management

## Database Design

### Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Note : creates
    User {
        int id PK
        string email UK
        string name
        datetime created_at
        boolean is_active
    }
    
    Note ||--o{ Tag : has
    Note {
        int id PK
        int user_id FK
        string title
        text content
        datetime created_at
        datetime updated_at
    }
    
    Tag {
        int id PK
        string name UK
        string color
    }
```

## Security Architecture

### Authentication Flow

1. User submits credentials
2. Backend validates and generates JWT token
3. Frontend stores token in HTTP-only cookie
4. Token included in subsequent API requests
5. Backend validates token on protected routes

### Authorization Layers

- **Route Level** - Middleware checks authentication
- **Service Level** - Business logic enforces permissions  
- **Data Level** - Repository filters data by ownership

## Performance Considerations

### Backend Optimizations

- Connection pooling for database connections
- Query optimization with SQLAlchemy indexes
- Response caching with Redis
- Async/await for I/O operations

### Frontend Optimizations

- Code splitting with Vue Router
- Component lazy loading
- Virtual scrolling for large lists
- Memoization with computed properties

## Deployment Architecture

### Production Environment

```mermaid
graph LR
    LB[Load Balancer] --> App1[App Instance 1]
    LB --> App2[App Instance 2]
    App1 --> DB[(Database)]
    App2 --> DB
    App1 --> Redis[(Redis Cache)]
    App2 --> Redis
```

### CI/CD Pipeline

1. Code pushed to repository
2. Automated tests run
3. Security scans performed
4. Docker images built
5. Deployment to staging
6. Automated acceptance tests
7. Production deployment
```

## User Documentation

### Getting Started Guide
```markdown
# Getting Started with LifeTime

## What is LifeTime?

LifeTime is a personal life management application that helps you organize your thoughts, track your goals, and manage your daily activities.

## Quick Start

### 1. Create Your Account

1. Visit [https://lifetime-app.com](https://lifetime-app.com)
2. Click "Sign Up" in the top right corner
3. Enter your email and create a secure password
4. Verify your email address

### 2. Create Your First Note

1. Click the "+" button in the main navigation
2. Add a title for your note
3. Write your content using the rich text editor
4. Add tags to organize your notes
5. Click "Save" to store your note

### 3. Organize with Tags

Tags help you categorize and find your notes quickly:

- Use descriptive tags like "work", "personal", "ideas"
- Create color-coded tags for visual organization  
- Filter notes by tags using the sidebar

## Features

### Note Management
- **Rich Text Editor** - Format your notes with bold, italic, lists, and links
- **Tag Organization** - Categorize notes with customizable tags
- **Search** - Find notes quickly with full-text search
- **Export** - Download your notes in various formats

### Privacy & Security
- **Data Encryption** - Your notes are encrypted at rest
- **Secure Authentication** - Protected login with strong passwords
- **Privacy First** - Your data belongs to you, not us

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Create new note | Ctrl/Cmd + N |
| Save note | Ctrl/Cmd + S |
| Search notes | Ctrl/Cmd + F |
| Bold text | Ctrl/Cmd + B |
| Italic text | Ctrl/Cmd + I |

## Getting Help

- **Documentation** - Visit our [help center](https://help.lifetime-app.com)
- **Support** - Email us at [support@lifetime-app.com](mailto:support@lifetime-app.com)
- **Community** - Join our [Discord server](https://discord.gg/lifetime)

## Next Steps

- Explore the [Advanced Features Guide](./advanced-features.md)
- Learn about [Data Export and Backup](./data-export.md)
- Check out [Keyboard Shortcuts](./shortcuts.md)
```

## Developer Documentation

### Contributing Guide
```markdown
# Contributing to LifeTime

Thank you for your interest in contributing to LifeTime! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Git
- Docker (optional, for local database)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/lifetime-ai-first.git
   cd lifetime-ai-first
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   python run.py
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   # Edit .env.local with your configuration
   npm run dev
   ```

4. **Run tests**
   ```bash
   # Backend tests
   cd backend && pytest
   
   # Frontend tests
   cd frontend && npm test
   ```

## Code Standards

### Python (Backend)
- Follow PEP 8 style guidelines
- Use Black for code formatting
- Include type hints for all functions
- Write docstrings for all public methods
- Maintain 90%+ test coverage

### TypeScript (Frontend)  
- Use ESLint and Prettier for formatting
- Enable TypeScript strict mode
- Write JSDoc comments for components
- Follow Vue.js style guide
- Maintain 80%+ test coverage

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our standards
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   ```bash
   # Run all tests
   ./run-tests.sh
   
   # Check code quality
   ./check-quality.sh
   ```

4. **Submit pull request**
   - Use the PR template
   - Include screenshots for UI changes
   - Request review from maintainers

## Issue Guidelines

### Bug Reports
Include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, browser, version)
- Screenshots or error messages

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Implementation complexity estimate

## Getting Help

- Join our [Discord](https://discord.gg/lifetime) for real-time help
- Check existing [GitHub Issues](https://github.com/your-org/lifetime/issues)
- Read our [Development Wiki](https://github.com/your-org/lifetime/wiki)
```

## Documentation Best Practices

### Writing Guidelines
- **Clear and Concise** - Use simple language and short sentences
- **User-Focused** - Write from the user's perspective
- **Action-Oriented** - Use active voice and clear action words
- **Well-Structured** - Use headers, lists, and formatting for readability
- **Up-to-Date** - Keep documentation synchronized with code changes

### Maintenance
- **Regular Reviews** - Schedule periodic documentation reviews
- **Version Control** - Track documentation changes with code
- **Feedback Integration** - Update based on user feedback and questions
- **Automation** - Use tools to generate documentation from code where possible

Always ensure documentation serves its intended audience and provides clear, actionable information.