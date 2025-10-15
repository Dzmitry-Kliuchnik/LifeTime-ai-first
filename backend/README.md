# LifeTime AI - Backend

FastAPI backend for the LifeTime AI personal life management assistant.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py    # API v1 main router
│   │       ├── users.py     # User management endpoints
│   │       ├── notes.py     # Notes management endpoints
│   │       └── week_calculation.py  # Week calculation endpoints
│   ├── core/                # Core application components
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration management
│   │   ├── database.py      # Database connection and session
│   │   ├── exceptions.py    # Custom exception handlers
│   │   ├── logging.py       # Logging configuration
│   │   └── rate_limiting.py # Rate limiting utilities
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── base.py          # Base model class
│   │   ├── user.py          # User model
│   │   └── note.py          # Note model
│   ├── repositories/        # Data access layer
│   │   ├── __init__.py
│   │   ├── user.py          # User repository
│   │   └── note.py          # Note repository
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py          # User schemas
│   │   ├── note.py          # Note schemas
│   │   └── week_calculation.py  # Week calculation schemas
│   └── services/            # Business logic services
│       ├── __init__.py
│       ├── user.py          # User service
│       ├── note.py          # Note service
│       └── week_calculation.py  # Week calculation service
├── migrations/              # Alembic database migrations
│   ├── env.py              # Migration environment
│   └── versions/           # Migration version files
├── requirements.txt         # Python dependencies
├── .env.template           # Environment variables template
├── .gitignore              # Git ignore rules
├── alembic.ini             # Alembic configuration
├── pyproject.toml          # Project configuration
├── run.py                  # Application entry point
└── init_db.py              # Database initialization script
```

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Clean Architecture**: Separation of concerns with repositories, services, and API layers
- **User Management**: Complete CRUD operations with soft delete and profile management
- **Notes System**: Week-based notes with tags, search, and edit history
- **Week Calculations**: Life week tracking based on user's date of birth
- **Database Models**: SQLAlchemy ORM with User and Note models
- **Database Migrations**: Alembic for schema versioning (5 migrations implemented)
- **Optional Encryption**: SQLCipher support for database encryption
- **Configuration Management**: Environment-based configuration with Pydantic
- **CORS Support**: Configurable CORS middleware for frontend integration
- **Error Handling**: Custom exception handlers with structured error responses
- **Logging**: Structured logging with Loguru
- **Testing**: Comprehensive test suite with pytest (242 tests)
- **Type Safety**: Full type annotations with mypy support
- **Code Quality**: Black formatting and flake8 linting configuration

## Prerequisites

- Python 3.11 or higher (tested with Python 3.12)
- pip (Python package installer)
- SQLite (included with Python) or PostgreSQL for production

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd LifeTime-ai-first/backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   ```bash
   # Windows
   copy .env.template .env
   # macOS/Linux
   cp .env.template .env
   ```
   Edit the `.env` file with your specific configuration.

6. **Initialize the database**:
   ```bash
   python init_db.py --init
   # Or verify existing setup
   python init_db.py --verify
   ```

## Configuration

The application uses environment variables for configuration. Copy `.env.template` to `.env` and modify as needed:

### Key Configuration Options

- `APP_NAME`: Application name (default: "LifeTime AI")
- `APP_VERSION`: Application version (default: "0.1.0")
- `DEBUG`: Enable debug mode (default: false)
- `HOST`: Server host (default: "127.0.0.1")
- `PORT`: Server port (default: 8000)
- `RELOAD`: Auto-reload on code changes (default: false)
- `DATABASE_URL`: Database connection URL (default: "sqlite:///./lifetime.db")
- `DATABASE_ECHO`: Echo SQL queries to console (default: false)
- `DATABASE_ENCRYPT`: Enable SQLCipher encryption (default: false)
- `DATABASE_KEY`: Encryption key for SQLCipher (required if encryption enabled)
- `SECRET_KEY`: Secret key for JWT tokens (change in production!)
- `ALGORITHM`: JWT algorithm (default: "HS256")
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `CORS_ORIGINS`: Allowed CORS origins (JSON array format)
- `CORS_CREDENTIALS`: Allow credentials (default: true)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Running the Application

### Using the Run Script (Recommended)

```bash
# From the backend directory
python run.py
```

This automatically loads configuration from `.env` and starts the server.

### Development Server

```bash
# From the backend directory
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Or with environment variables
uvicorn app.main:app --reload --host $HOST --port $PORT
```

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Testing

Run the test suite:

```bash
# Run all tests from project root
pytest tests/backend/

# Run tests with coverage
pytest tests/backend/ --cov=app

# Run specific test file
pytest tests/backend/test_app.py
pytest tests/backend/test_user.py
pytest tests/backend/test_notes.py

# Run tests with verbose output
pytest tests/backend/ -v

# Run only unit tests
pytest tests/backend/ -m unit

# Run only integration tests
pytest tests/backend/ -m integration
```

### Test Categories

The test suite includes 242 tests covering:

- **Configuration Tests**: Settings and environment variables
- **Application Tests**: FastAPI app initialization and middleware
- **CORS Tests**: Cross-origin request handling
- **Database Tests**: Connection, models, and encryption
- **User Tests**: User management, authentication, and profile operations
- **Notes Tests**: Notes CRUD, tags, search, and week-based operations
- **Week Calculation Tests**: Life week calculations and date validation
- **API Integration Tests**: End-to-end endpoint testing

## Development

### Code Quality

The project uses several tools for code quality:

```bash
# Format code with Black
black app/ tests/

# Type checking with mypy
mypy app/

# Linting with flake8
flake8 app/
```

### Adding New Features

1. Create new modules in the appropriate directories
2. Add corresponding tests in `tests/backend/`
3. Update documentation as needed
4. Run tests and quality checks before committing

## Project Dependencies

### Core Dependencies

- **FastAPI** (0.104.1): Web framework
- **Uvicorn** (0.24.0): ASGI server
- **SQLAlchemy** (2.0.23): Database ORM
- **Alembic** (1.12.1): Database migrations
- **Pydantic** (2.5.0): Data validation and settings
- **Pydantic-Settings** (2.1.0): Settings management
- **Loguru** (0.7.2): Logging library
- **Python-Jose** (3.3.0): JWT token handling
- **Passlib** (1.7.4): Password hashing
- **Argon2-cffi** (23.1.0): Argon2 password hashing backend
- **Cryptography** (41.0.7): Encryption support
- **Python-Multipart** (0.0.6): Form data parsing
- **Python-Dateutil** (2.8.2): Date utilities

### Development Dependencies

- **Pytest** (7.4.3): Testing framework
- **Pytest-Asyncio** (0.21.1): Async test support
- **HTTPX** (0.25.2): Test client for FastAPI
- **Black** (23.11.0): Code formatter
- **MyPy** (1.7.1): Static type checker
- **Flake8** (6.1.0): Linting

### Optional Dependencies

- **pysqlcipher3**: For SQLCipher database encryption (install separately if needed)

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | "LifeTime AI" | No |
| `APP_VERSION` | Application version | "0.1.0" | No |
| `DEBUG` | Enable debug mode | false | No |
| `HOST` | Server host | "127.0.0.1" | No |
| `PORT` | Server port | 8000 | No |
| `RELOAD` | Auto-reload on changes | false | No |
| `DATABASE_URL` | Database connection | "sqlite:///./lifetime.db" | No |
| `DATABASE_ECHO` | Echo SQL queries | false | No |
| `DATABASE_ENCRYPT` | Enable encryption | false | No |
| `DATABASE_KEY` | Encryption key | - | Yes (if encryption) |
| `SECRET_KEY` | JWT secret key | - | Yes (production) |
| `ALGORITHM` | JWT algorithm | "HS256" | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 | No |
| `CORS_ORIGINS` | Allowed origins | ["http://localhost:3000"] | No |
| `CORS_CREDENTIALS` | Allow credentials | true | No |
| `CORS_METHODS` | Allowed methods | ["GET", "POST", "PUT", "DELETE", "OPTIONS"] | No |
| `CORS_HEADERS` | Allowed headers | ["*"] | No |
| `LOG_LEVEL` | Logging level | "INFO" | No |
| `API_V1_PREFIX` | API v1 prefix | "/api/v1" | No |
| `DOCS_URL` | Swagger UI path | "/docs" | No |
| `REDOC_URL` | ReDoc path | "/redoc" | No |
| `OPENAPI_URL` | OpenAPI JSON path | "/openapi.json" | No |

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the correct directory and virtual environment is activated
2. **Port Already in Use**: Change the PORT environment variable or kill the process using the port
3. **Permission Errors**: Check file permissions and virtual environment activation

### Logging

Logs are output to the console in development mode. In production, logs are also written to `logs/app.log` with rotation.

## Contributing

1. Create a feature branch
2. Make changes with appropriate tests
3. Run quality checks (`black`, `mypy`, `flake8`)
4. Run test suite (`pytest`)
5. Submit a pull request

## License

This project is part of the LifeTime AI application.