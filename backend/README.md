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
│   │       └── router.py    # API v1 routes
│   ├── core/                # Core application components
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration management
│   │   ├── exceptions.py    # Custom exception handlers
│   │   └── logging.py       # Logging configuration
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   └── services/            # Business logic services
├── requirements.txt         # Python dependencies
├── .env.template           # Environment variables template
├── .gitignore              # Git ignore rules
└── pyproject.toml          # Project configuration
```

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Configuration Management**: Environment-based configuration with Pydantic
- **CORS Support**: Configurable CORS middleware for frontend integration
- **Error Handling**: Custom exception handlers with structured error responses
- **Logging**: Structured logging with Loguru
- **Testing**: Comprehensive test suite with pytest
- **Type Safety**: Full type annotations with mypy support
- **Code Quality**: Black formatting and linting configuration

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

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
   copy .env.template .env
   ```
   Edit the `.env` file with your specific configuration.

## Configuration

The application uses environment variables for configuration. Copy `.env.template` to `.env` and modify as needed:

### Key Configuration Options

- `APP_NAME`: Application name (default: "LifeTime AI")
- `DEBUG`: Enable debug mode (default: false)
- `HOST`: Server host (default: "127.0.0.1")
- `PORT`: Server port (default: 8000)
- `DATABASE_URL`: Database connection URL
- `SECRET_KEY`: Secret key for JWT tokens (change in production!)
- `CORS_ORIGINS`: Allowed CORS origins (JSON array format)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Running the Application

### Development Server

```bash
# From the backend directory
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
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
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app

# Run specific test file
pytest tests/backend/test_app.py

# Run tests with verbose output
pytest -v
```

### Test Categories

- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test component interactions
- **API Tests**: Test HTTP endpoints and responses

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

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation and settings
- **Loguru**: Logging library

### Development Dependencies

- **Pytest**: Testing framework
- **Black**: Code formatter
- **MyPy**: Static type checker
- **Flake8**: Linting

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | "LifeTime AI" | No |
| `DEBUG` | Enable debug mode | false | No |
| `HOST` | Server host | "127.0.0.1" | No |
| `PORT` | Server port | 8000 | No |
| `DATABASE_URL` | Database connection | "sqlite:///./lifetime.db" | No |
| `SECRET_KEY` | JWT secret key | - | Yes (production) |
| `CORS_ORIGINS` | Allowed origins | ["http://localhost:3000"] | No |
| `LOG_LEVEL` | Logging level | "INFO" | No |

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