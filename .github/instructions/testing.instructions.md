---
description: 'Testing standards and best practices for Python FastAPI and Vue.js applications'
applyTo: '**/*test*.py, **/*spec*.ts, **/*test*.ts, **/*spec*.js'
---

# Testing Guidelines

Apply comprehensive testing practices across both backend (Python/FastAPI) and frontend (Vue.js/TypeScript) codebases.

## General Testing Philosophy

- **Testing is mandatory** - All new features and bug fixes must include corresponding tests
- **Test behavior, not implementation** - Focus on what the code does, not how it does it
- **Comprehensive coverage** - Include happy path, edge cases, and error scenarios
- **Fast and reliable** - Tests should run quickly and produce consistent results
- **Maintainable** - Tests should be easy to read, understand, and update

## Backend Testing (Python/FastAPI)

### Test Organization
```
tests/backend/
├── conftest.py              # Pytest fixtures and configuration
├── test_app.py             # Application-level tests
├── test_models.py          # Database model tests
├── test_repositories.py    # Data access layer tests
├── test_services.py        # Business logic tests
└── test_api/              # API endpoint tests
    ├── test_auth.py
    ├── test_users.py
    └── test_notes.py
```

### Testing Framework Configuration
```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

### Unit Testing Examples

#### Testing Services
```python
# test_user_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.user import UserService
from app.schemas.user import CreateUserRequest
from app.models.user import User

class TestUserService:
    @pytest.fixture
    def mock_user_repository(self):
        return Mock()
    
    @pytest.fixture
    def user_service(self, mock_user_repository):
        return UserService(user_repository=mock_user_repository)
    
    def test_create_user_success(self, user_service, mock_user_repository):
        # Arrange
        user_data = CreateUserRequest(
            name="John Doe",
            email="john@example.com"
        )
        expected_user = User(id=1, name="John Doe", email="john@example.com")
        mock_user_repository.create.return_value = expected_user
        
        # Act
        result = user_service.create_user(user_data)
        
        # Assert
        assert result.name == "John Doe"
        assert result.email == "john@example.com"
        mock_user_repository.create.assert_called_once()
    
    def test_create_user_duplicate_email(self, user_service, mock_user_repository):
        # Arrange
        user_data = CreateUserRequest(
            name="John Doe",
            email="existing@example.com"
        )
        mock_user_repository.get_by_email.return_value = User(id=1, email="existing@example.com")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            user_service.create_user(user_data)
```

#### Testing API Endpoints
```python
# test_api/test_users.py
import pytest
from fastapi import status

class TestUserAPI:
    def test_create_user_success(self, client):
        # Arrange
        user_data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        # Act
        response = client.post("/api/v1/users", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert "id" in data
    
    def test_create_user_invalid_email(self, client):
        # Arrange
        user_data = {
            "name": "John Doe",
            "email": "invalid-email"
        }
        
        # Act
        response = client.post("/api/v1/users", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_user_not_found(self, client):
        # Act
        response = client.get("/api/v1/users/999")
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize("user_id,expected_status", [
        (1, status.HTTP_200_OK),
        (999, status.HTTP_404_NOT_FOUND),
        (-1, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ])
    def test_get_user_various_ids(self, client, user_id, expected_status):
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == expected_status
```

#### Testing Database Models
```python
# test_models.py
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User

class TestUserModel:
    def test_create_user(self, db_session):
        # Arrange & Act
        user = User(name="John Doe", email="john@example.com")
        db_session.add(user)
        db_session.commit()
        
        # Assert
        assert user.id is not None
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
    
    def test_user_email_uniqueness(self, db_session):
        # Arrange
        user1 = User(name="John Doe", email="john@example.com")
        user2 = User(name="Jane Doe", email="john@example.com")
        
        # Act & Assert
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
```

## Frontend Testing (Vue.js/TypeScript)

### Test Organization
```
src/
├── components/
│   ├── UserCard.vue
│   └── __tests__/
│       └── UserCard.spec.ts
├── composables/
│   ├── useFetch.ts
│   └── __tests__/
│       └── useFetch.spec.ts
└── stores/
    ├── user.ts
    └── __tests__/
        └── user.spec.ts

cypress/
├── e2e/
│   ├── auth.cy.ts
│   └── users.cy.ts
└── support/
    └── commands.ts
```

### Component Testing with Vitest

#### Testing Vue Components
```typescript
// components/__tests__/UserCard.spec.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeEach } from 'vitest'
import UserCard from '../UserCard.vue'
import type { User } from '@/types/user'

describe('UserCard', () => {
  let mockUser: User

  beforeEach(() => {
    mockUser = {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      isActive: true
    }
  })

  it('renders user information correctly', () => {
    const wrapper = mount(UserCard, {
      props: { user: mockUser }
    })

    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('john@example.com')
    expect(wrapper.find('[data-testid="user-name"]').text()).toBe('John Doe')
  })

  it('emits edit event when edit button is clicked', async () => {
    const wrapper = mount(UserCard, {
      props: { user: mockUser }
    })

    await wrapper.find('[data-testid="edit-button"]').trigger('click')
    
    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')![0]).toEqual([mockUser])
  })

  it('applies correct CSS class based on user status', () => {
    const inactiveUser = { ...mockUser, isActive: false }
    const wrapper = mount(UserCard, {
      props: { user: inactiveUser }
    })

    expect(wrapper.classes()).toContain('user-card--inactive')
  })

  it('handles missing user data gracefully', () => {
    const incompleteUser = { id: 1, name: '', email: '' } as User
    const wrapper = mount(UserCard, {
      props: { user: incompleteUser }
    })

    expect(wrapper.find('[data-testid="placeholder"]').exists()).toBe(true)
  })
})
```

#### Testing Composables
```typescript
// composables/__tests__/useFetch.spec.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useFetch } from '../useFetch'

describe('useFetch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('executes fetch and updates data on success', async () => {
    // Arrange
    const mockData = { id: 1, name: 'Test' }
    const mockFetcher = vi.fn().mockResolvedValue(mockData)
    const { data, loading, error, execute } = useFetch(mockFetcher)

    // Act
    await execute()

    // Assert
    expect(mockFetcher).toHaveBeenCalledTimes(1)
    expect(data.value).toEqual(mockData)
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  it('handles fetch error correctly', async () => {
    // Arrange
    const mockError = new Error('Fetch failed')
    const mockFetcher = vi.fn().mockRejectedValue(mockError)
    const { data, loading, error, execute } = useFetch(mockFetcher)

    // Act
    await execute()

    // Assert
    expect(data.value).toBeNull()
    expect(loading.value).toBe(false)
    expect(error.value).toBe('Fetch failed')
  })
})
```

#### Testing Pinia Stores
```typescript
// stores/__tests__/user.spec.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useUserStore } from '../user'
import * as userApi from '@/api/user'

// Mock the API
vi.mock('@/api/user')

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetches users successfully', async () => {
    // Arrange
    const mockUsers = [
      { id: 1, name: 'John', email: 'john@example.com' },
      { id: 2, name: 'Jane', email: 'jane@example.com' }
    ]
    vi.mocked(userApi.getUsers).mockResolvedValue(mockUsers)
    
    const store = useUserStore()

    // Act
    await store.fetchUsers()

    // Assert
    expect(store.users).toEqual(mockUsers)
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('handles fetch error', async () => {
    // Arrange
    const errorMessage = 'API Error'
    vi.mocked(userApi.getUsers).mockRejectedValue(new Error(errorMessage))
    
    const store = useUserStore()

    // Act
    await store.fetchUsers()

    // Assert
    expect(store.users).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBe(errorMessage)
  })

  it('computed activeUsers filters correctly', () => {
    // Arrange
    const store = useUserStore()
    store.users = [
      { id: 1, name: 'Active User', isActive: true },
      { id: 2, name: 'Inactive User', isActive: false }
    ]

    // Act & Assert
    expect(store.activeUsers).toHaveLength(1)
    expect(store.activeUsers[0].name).toBe('Active User')
  })
})
```

### End-to-End Testing with Cypress

#### User Authentication Flow
```typescript
// cypress/e2e/auth.cy.ts
describe('User Authentication', () => {
  beforeEach(() => {
    cy.visit('/login')
  })

  it('allows user to log in with valid credentials', () => {
    cy.get('[data-testid="email-input"]').type('user@example.com')
    cy.get('[data-testid="password-input"]').type('password123')
    cy.get('[data-testid="login-button"]').click()

    cy.url().should('include', '/dashboard')
    cy.get('[data-testid="user-menu"]').should('be.visible')
  })

  it('shows error for invalid credentials', () => {
    cy.get('[data-testid="email-input"]').type('invalid@example.com')
    cy.get('[data-testid="password-input"]').type('wrongpassword')
    cy.get('[data-testid="login-button"]').click()

    cy.get('[data-testid="error-message"]')
      .should('be.visible')
      .and('contain', 'Invalid credentials')
  })

  it('validates required fields', () => {
    cy.get('[data-testid="login-button"]').click()
    
    cy.get('[data-testid="email-error"]')
      .should('be.visible')
      .and('contain', 'Email is required')
    
    cy.get('[data-testid="password-error"]')
      .should('be.visible')
      .and('contain', 'Password is required')
  })
})
```

#### API Integration Tests
```typescript
// cypress/e2e/users.cy.ts
describe('User Management', () => {
  beforeEach(() => {
    // Authenticate user
    cy.login('admin@example.com', 'admin123')
    cy.visit('/users')
  })

  it('creates a new user', () => {
    cy.get('[data-testid="add-user-button"]').click()
    
    cy.get('[data-testid="name-input"]').type('New User')
    cy.get('[data-testid="email-input"]').type('newuser@example.com')
    cy.get('[data-testid="submit-button"]').click()

    cy.get('[data-testid="success-message"]').should('be.visible')
    cy.get('[data-testid="user-list"]').should('contain', 'New User')
  })

  it('handles API errors gracefully', () => {
    // Intercept API call to simulate error
    cy.intercept('POST', '/api/v1/users', {
      statusCode: 400,
      body: { detail: 'Email already exists' }
    }).as('createUserError')

    cy.get('[data-testid="add-user-button"]').click()
    cy.get('[data-testid="name-input"]').type('Test User')
    cy.get('[data-testid="email-input"]').type('existing@example.com')
    cy.get('[data-testid="submit-button"]').click()

    cy.wait('@createUserError')
    cy.get('[data-testid="error-message"]')
      .should('be.visible')
      .and('contain', 'Email already exists')
  })
})
```

## Test Coverage and Quality Standards

### Coverage Requirements
- **Backend:** Minimum 90% code coverage for services and repositories
- **Frontend:** Minimum 80% code coverage for components and composables
- **Critical paths:** 100% coverage for authentication, data validation, and core business logic

### Test Quality Checklist
- ✅ Tests are isolated and don't depend on external services
- ✅ Tests use descriptive names that explain what they verify
- ✅ Tests follow Arrange-Act-Assert pattern
- ✅ Edge cases and error scenarios are covered
- ✅ Tests are fast and can run in parallel
- ✅ Mock external dependencies appropriately
- ✅ Use data-testid attributes instead of relying on CSS selectors
- ✅ Clean up resources after tests (database, temporary files)

### Continuous Integration Testing
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests with coverage
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run unit tests
        run: |
          cd frontend
          npm run test:unit
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e
```

## Testing Best Practices

### Do's
- Write tests first for new features (TDD approach)
- Use meaningful test names that describe the scenario
- Test one thing at a time
- Use appropriate assertions and matchers
- Mock external dependencies and API calls
- Test error conditions and edge cases
- Use factories or fixtures for test data setup
- Run tests frequently during development

### Don'ts
- Don't test implementation details
- Don't write overly complex test setups
- Don't skip tests or mark them as pending without good reason
- Don't use production data in tests
- Don't rely on test execution order
- Don't ignore flaky or intermittent test failures
- Don't test framework code (Vue.js, FastAPI internals)
- Don't use real external services in unit tests