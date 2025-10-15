# LifeTime AI - Personal Life Management Assistant

A comprehensive AI-powered platform for managing and optimizing personal life aspects including health, finances, career, and relationships.

## Project Overview

LifeTime AI is designed to be your personal assistant for life management, providing insights, recommendations, and automation for various aspects of daily life.

## Project Structure

```
LifeTime-ai-first/
├── backend/                 # FastAPI backend application
│   ├── app/                # Main application code
│   │   ├── api/           # API routes (v1: users, notes, week_calculation)
│   │   ├── core/          # Core components (config, database, logging)
│   │   ├── models/        # SQLAlchemy database models (User, Note)
│   │   ├── repositories/  # Data access layer
│   │   ├── schemas/       # Pydantic schemas for validation
│   │   └── services/      # Business logic layer
│   ├── migrations/        # Alembic database migrations
│   ├── requirements.txt   # Python dependencies
│   └── README.md         # Backend-specific documentation
├── frontend/              # Vue 3 + TypeScript frontend application
│   ├── src/              # Source code
│   │   ├── components/   # Vue components
│   │   ├── views/        # Page views
│   │   ├── stores/       # Pinia state management
│   │   ├── router/       # Vue Router configuration
│   │   └── utils/        # Utility functions
│   ├── cypress/          # End-to-end tests
│   ├── package.json      # Node.js dependencies
│   └── README.md        # Frontend-specific documentation
├── docs/                 # Project documentation
├── tests/                # Test suites
│   └── backend/         # Backend tests (242 tests)
├── start.sh             # Unix startup script
├── start.bat            # Windows startup script
└── README.md            # This file
```

## Components

### Backend (FastAPI)

- **Framework**: FastAPI with Python 3.11+ (Compatible with Python 3.12)
- **Features**: RESTful API, user management, notes system, week-based calculations
- **Database**: SQLAlchemy ORM with SQLite (development) / PostgreSQL (production)
- **Encryption**: Optional SQLCipher database encryption support
- **Migrations**: Alembic for database schema management (5 migrations implemented)
- **Testing**: Comprehensive test suite with pytest (242 tests)
- **Documentation**: Auto-generated API docs with Swagger UI and ReDoc

### Frontend (Vue 3 + TypeScript)

- **Framework**: Vue 3 with Composition API
- **Language**: TypeScript with full type safety
- **Build Tool**: Vite for fast development and optimized builds
- **State Management**: Pinia for reactive state management
- **Routing**: Vue Router for navigation
- **HTTP Client**: Axios for API communication
- **Testing**: Vitest for unit tests, Cypress for E2E tests
- **Code Quality**: ESLint, Prettier for formatting
- **Development Server**: Hot module replacement (HMR) on http://localhost:5173

## Quick Start

### Using the Startup Scripts (Recommended)

The easiest way to start both backend and frontend:

**Windows:**
```bash
start.bat
```

**macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

This will:
- Create and activate virtual environments
- Install all dependencies
- Start the backend server on http://localhost:8000
- Start the frontend dev server on http://localhost:5173

### Manual Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   # Windows
   copy .env.template .env
   # macOS/Linux
   cp .env.template .env
   # Edit .env file with your configuration
   ```

5. **Initialize the database**:
   ```bash
   python init_db.py --init
   ```

6. **Run the development server**:
   ```bash
   python run.py
   # Or using uvicorn directly:
   uvicorn app.main:app --reload
   ```

7. **Access the API**:
   - API: http://localhost:8000
   - Interactive Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Manual Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```

4. **Access the application**:
   - Frontend: http://localhost:5173
   - The frontend will automatically connect to the backend at http://localhost:8000

## Testing

### Backend Tests

Run the complete backend test suite:

```bash
# From the project root
pytest tests/backend/

# Run with coverage
pytest tests/backend/ --cov=app

# Run with verbose output
pytest tests/backend/ -v

# Run specific test categories
pytest tests/backend/test_app.py
pytest tests/backend/test_config.py
pytest tests/backend/test_cors.py
pytest tests/backend/test_user.py
pytest tests/backend/test_notes.py
```

### Frontend Tests

Run frontend tests:

```bash
# From the frontend directory
cd frontend

# Run unit tests
npm run test:unit

# Run E2E tests (development mode)
npm run test:e2e:dev

# Run E2E tests (production build)
npm run build
npm run test:e2e
```

## Development Status

### Backend ✅
- ✅ FastAPI application structure with middleware
- ✅ Environment-based configuration management
- ✅ CORS configuration for frontend integration
- ✅ Error handling and structured logging
- ✅ Database models (User, Note) with SQLAlchemy
- ✅ Database migrations with Alembic (5 migrations)
- ✅ Optional SQLCipher encryption support
- ✅ Repository pattern for data access
- ✅ Service layer for business logic
- ✅ Comprehensive test suite (242 tests, 218 passing)
- ✅ User management API (CRUD, soft delete, profile management)
- ✅ Notes system API (CRUD, search, tags, week-based)
- ✅ Week calculation utilities (life weeks tracking)

### Frontend ✅
- ✅ Vue 3 with TypeScript setup
- ✅ Vite build configuration
- ✅ Pinia state management
- ✅ Vue Router navigation
- ✅ Axios API client integration
- ✅ Component library structure
- ✅ Unit and E2E testing setup (Vitest, Cypress)
- ✅ ESLint and Prettier configuration
- ✅ Development and production builds

### In Progress / Planned 🚧
- 🚧 Authentication and authorization (JWT infrastructure exists)
- 🚧 Password reset and email verification
- 🚧 Advanced search and filtering features
- 🚧 Data export and backup functionality
- 🚧 Deployment configuration (Docker, CI/CD)
- 🚧 Performance optimization and caching
- 🚧 API rate limiting implementation

## Key Features

### Current Features ✅

#### User Management
- User registration and profile management
- Optional email and password (supports name-only users)
- Soft delete functionality (users can be restored)
- Date of birth tracking for life week calculations
- Profile customization (theme, lifespan, font size)
- User statistics and filtering

#### Notes System
- Create, read, update, and delete notes
- Week-based organization (tied to user's life weeks)
- Tagging system for categorization
- Search and filtering capabilities
- Edit history tracking
- Soft delete with restore functionality
- Validation preventing future week entries

#### Life Week Tracking
- Calculate current life week based on date of birth
- Week-based data organization
- Life progress visualization support

### Planned Features 🚧

- **Health Management**: Track fitness, nutrition, and wellness metrics
- **Financial Planning**: Budget tracking, expense analysis, investment insights
- **Career Development**: Goal setting, skill tracking, networking management
- **Relationship Management**: Contact organization, event reminders, communication tracking
- **AI Insights**: Personalized recommendations based on data analysis
- **Automation**: Smart reminders, routine optimization, habit tracking

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework (v0.104.1)
- **SQLAlchemy**: Database ORM (v2.0.23)
- **Alembic**: Database migration tool (v1.12.1)
- **Pydantic**: Data validation and serialization (v2.5.0)
- **Uvicorn**: ASGI server (v0.24.0)
- **Pytest**: Testing framework (v7.4.3)
- **Loguru**: Advanced logging (v0.7.2)
- **Python-Jose**: JWT token handling (v3.3.0)
- **Passlib**: Password hashing (v1.7.4) with Argon2
- **Cryptography**: Encryption support (v41.0.7)

### Frontend
- **Vue 3**: Progressive JavaScript framework (v3.5.22)
- **TypeScript**: Static type checking (v5.9.0)
- **Vite**: Next-generation build tool (v7.1.7)
- **Pinia**: State management (v3.0.3)
- **Vue Router**: Official routing library (v4.5.1)
- **Axios**: HTTP client (v1.12.2)
- **Vitest**: Unit testing framework (v3.2.4)
- **Cypress**: E2E testing framework (v15.3.0)

### Development Tools
- **Black**: Python code formatter (v23.11.0)
- **MyPy**: Static type checker for Python (v1.7.1)
- **Flake8**: Python code linting (v6.1.0)
- **ESLint**: JavaScript/TypeScript linting (v9.33.0)
- **Prettier**: Code formatter (v3.6.2)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with appropriate tests
4. Run quality checks and tests
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Documentation

- [Backend Documentation](backend/README.md) - FastAPI backend setup and API details
- [Frontend Documentation](frontend/README.md) - Vue 3 frontend setup and development
- [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI (when server is running)
- [Alternative API Documentation](http://localhost:8000/redoc) - ReDoc format
- [Additional Documentation](docs/README.md) - Architecture and development guides

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or suggestions, please open an issue in the GitHub repository.