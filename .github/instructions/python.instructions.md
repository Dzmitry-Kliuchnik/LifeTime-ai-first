<!-- Based on: https://github.com/github/awesome-copilot/blob/main/instructions/python.instructions.md -->
---
description: 'Python FastAPI development standards and best practices'
applyTo: '**/*.py'
---

# Python FastAPI Development Guidelines

Apply the [general coding guidelines](../copilot-instructions.md) to all Python code.

## Python Code Standards

### Code Style and Formatting
- Follow **PEP 8** style guide strictly
- Use **Black** for automated code formatting (line length: 88 characters)
- Use **flake8** or **pylint** for linting; address all reported issues
- Maintain proper indentation using 4 spaces for each level
- Use blank lines to separate functions, classes, and code blocks appropriately

### Type Hints and Documentation
- Include type hints for **all** function signatures and complex variables using the `typing` module
- Enable `strict` mode in mypy configuration for maximum type safety
- Write clear, concise docstrings following **Google** or **NumPy** style conventions
- Provide docstrings for all public modules, classes, functions, and methods explaining purpose, arguments, and return values
- Use `typing.Optional`, `List[str]`, `Dict[str, int]` and other specific type annotations

### Example of Proper Documentation
```python
from typing import Optional, List
from pydantic import BaseModel

def calculate_user_score(
    user_id: int, 
    activities: List[str], 
    weight_factor: Optional[float] = None
) -> float:
    """
    Calculate a user's activity score based on their activities.
    
    Args:
        user_id (int): The unique identifier for the user
        activities (List[str]): List of activity names to score
        weight_factor (Optional[float]): Multiplier for score calculation
        
    Returns:
        float: The calculated score between 0.0 and 100.0
        
    Raises:
        ValueError: If user_id is negative or activities list is empty
    """
    if user_id < 0:
        raise ValueError("User ID must be non-negative")
    if not activities:
        raise ValueError("Activities list cannot be empty")
        
    # Implementation logic here
    return 85.5
```

## FastAPI Specific Guidelines

### API Route Design
- Use consistent REST patterns for endpoint design
- Implement proper HTTP status codes (200, 201, 400, 404, 422, 500)
- Use FastAPI's automatic OpenAPI documentation generation
- Group related endpoints using `APIRouter` and include them in main app
- Use descriptive endpoint names and consistent URL patterns

### Pydantic Schemas
- Create separate request/response schemas even if similar
- Use Pydantic models for all data validation and serialization
- Implement proper validation rules (Field validators, root validators)
- Use meaningful model names ending with appropriate suffixes (`CreateUserRequest`, `UserResponse`)
- Leverage Pydantic's `Config` class for model configuration

### Database Integration
- Use SQLAlchemy with declarative models in `models/` directory
- Implement repository pattern for data access in `repositories/` directory
- Use Alembic for database migrations
- Always use parameterized queries to prevent SQL injection
- Implement proper database session management and cleanup

### Error Handling
- Use FastAPI's `HTTPException` for API errors
- Create custom exception classes for business logic errors
- Implement global exception handlers for consistent error responses
- Log errors appropriately with contextual information
- Return meaningful error messages without exposing internal details

### Dependency Injection
- Use FastAPI's dependency injection system for shared resources
- Create dependencies for database sessions, authentication, configuration
- Implement proper scope management for dependencies
- Use `Depends()` for reusable dependency injection patterns

## Architecture Patterns

### Layered Architecture
Follow the established pattern:
```
app/
├── api/          # API routes and endpoints
├── core/         # Configuration, database setup, logging
├── models/       # SQLAlchemy database models  
├── repositories/ # Data access layer
├── schemas/      # Pydantic request/response models
└── services/     # Business logic layer
```

### Service Layer Pattern
- Implement business logic in service classes
- Keep services independent of HTTP concerns
- Use dependency injection for service dependencies
- Make services easily testable with mocked dependencies

### Repository Pattern
- Abstract database operations behind repository interfaces
- Implement CRUD operations consistently across repositories
- Use repositories in services, not directly in API routes
- Make repositories easily mockable for testing

## Security Best Practices

### Authentication and Authorization
- Implement JWT-based authentication with proper token validation
- Use FastAPI's security utilities (`OAuth2PasswordBearer`, `Security`)
- Implement role-based access control where needed
- Validate user permissions at the service layer

### Input Validation
- Use Pydantic schemas for **all** request validation
- Implement additional business rule validation in services
- Sanitize user inputs, especially for database queries
- Validate file uploads for type, size, and content

### Environment Configuration
- Use `pydantic-settings` for configuration management
- Load all configuration from environment variables
- Never commit secrets or sensitive configuration
- Provide clear `.env.example` file with all required variables

## Testing Standards

### Unit Testing
- Write unit tests for all service layer functions
- Use `pytest` with proper fixtures and parameterization
- Mock external dependencies (database, APIs, file system)
- Test both success and failure scenarios
- Achieve high test coverage for critical business logic

### Integration Testing
- Test API endpoints with `TestClient` from FastAPI
- Use separate test database or in-memory database
- Test complete request/response cycles
- Validate proper HTTP status codes and response schemas
- Test error conditions and edge cases

### Test Organization
```python
# tests/backend/test_user_service.py
import pytest
from unittest.mock import Mock
from app.services.user import UserService
from app.schemas.user import CreateUserRequest

@pytest.fixture
def mock_user_repository():
    return Mock()

def test_create_user_success(mock_user_repository):
    # Test implementation
    pass

def test_create_user_duplicate_email(mock_user_repository):
    # Test error scenario
    pass
```

## Performance Optimization

### Database Performance
- Use database indexes appropriately
- Implement database query optimization
- Use connection pooling for database connections
- Consider read replicas for read-heavy operations

### API Performance
- Implement response caching where appropriate
- Use background tasks for long-running operations
- Implement proper pagination for large datasets
- Monitor and optimize slow endpoints

### Async Programming
- Use `async`/`await` for I/O operations
- Use `asyncio` compatible database drivers
- Implement proper exception handling in async code
- Avoid blocking operations in async functions

## Code Quality Rules

### Function and Class Design
- Keep functions small and focused on single responsibility
- Use descriptive, unambiguous names for functions, classes, and variables
- Break down complex functions into smaller, manageable pieces
- Avoid deep nesting; use early returns and guard clauses
- Handle edge cases explicitly with clear error messages

### Import Organization
```python
# Standard library imports
import os
from typing import Optional, List

# Third-party imports
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
import pytest

# Local application imports
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserResponse
```

### Error Handling Patterns
```python
# Good: Specific exception handling
try:
    user = await user_service.get_user(user_id)
    return UserResponse.from_orm(user)
except UserNotFoundError:
    raise HTTPException(status_code=404, detail="User not found")
except ValidationError as e:
    raise HTTPException(status_code=422, detail=str(e))
```

## Common Anti-Patterns to Avoid

- Don't put business logic directly in API route functions
- Don't use global variables for shared state
- Don't ignore type hints or use `Any` without justification
- Don't mix async and sync code inappropriately
- Don't skip input validation or rely only on frontend validation
- Don't expose internal error details to API consumers
- Don't use string concatenation for SQL queries