# LifeTime AI - Project Documentation

This directory contains comprehensive documentation for the LifeTime AI project.

## Documentation Structure

- **API Documentation**: Auto-generated from FastAPI application
- **Architecture Documentation**: System design and component interactions
- **Development Guide**: Setup, development workflows, and contribution guidelines
- **Deployment Guide**: Production deployment instructions

## Quick Links

### Development
- [Backend Setup](../backend/README.md) - FastAPI backend installation and configuration
- [Frontend Setup](../frontend/README.md) - Vue 3 frontend installation and configuration
- [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI (when server is running)
- [Alternative API Docs](http://localhost:8000/redoc) - ReDoc format

### Testing
- Backend test files: `/tests/backend/` (242 tests)
- Frontend test files: `/frontend/src/__tests__/` and `/frontend/cypress/`
- Run backend tests: `pytest tests/backend/` from project root
- Run frontend tests: `npm run test:unit` from frontend directory

### Configuration
- Backend environment: `/backend/.env.template`
- Frontend environment: `/frontend/.env.development` and `/frontend/.env.production`
- Application settings: `/backend/app/core/config.py`
- Database migrations: `/backend/migrations/versions/`

## Getting Started

1. Follow the setup instructions in the main [README](../README.md)
2. Use the startup scripts (`start.sh` or `start.bat`) for automatic setup, or:
   - Set up and start the backend development server (see [Backend Setup](../backend/README.md))
   - Set up and start the frontend development server (see [Frontend Setup](../frontend/README.md))
3. Visit the API documentation at http://localhost:8000/docs
4. Access the frontend application at http://localhost:5173
5. Explore the test suite in `/tests/backend/`

## Project Status

### Completed Features ✅

**Backend:**
- ✅ FastAPI application structure with clean architecture
- ✅ Configuration management with environment variables
- ✅ CORS and middleware setup for frontend integration
- ✅ Error handling and structured logging
- ✅ Database models (User, Note) with SQLAlchemy
- ✅ Database migrations with Alembic (5 migrations)
- ✅ Repository pattern for data access
- ✅ Service layer for business logic
- ✅ Comprehensive test suite (242 tests, all passing)
- ✅ User management API (CRUD, soft delete, profile)
- ✅ Notes system API (CRUD, search, tags, week-based)
- ✅ Week calculation utilities
- ✅ Optional database encryption support

**Frontend:**
- ✅ Vue 3 with TypeScript and Composition API
- ✅ Vite build configuration
- ✅ Pinia state management
- ✅ Vue Router navigation
- ✅ Axios API client
- ✅ Component library structure
- ✅ Unit and E2E testing setup (Vitest, Cypress)
- ✅ ESLint and Prettier configuration

### In Progress / Planned 🚧

- 🚧 JWT authentication and authorization implementation
- 🚧 Password reset and email verification
- 🚧 Advanced search and filtering
- 🚧 Data export and backup functionality
- 🚧 Deployment configuration (Docker, CI/CD)
- 🚧 Performance optimization and caching
- 🚧 API rate limiting
- 🚧 Additional feature modules (health, finance, career tracking)