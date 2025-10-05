# LifeTime AI - Personal Life Management Assistant

A comprehensive AI-powered platform for managing and optimizing personal life aspects including health, finances, career, and relationships.

## Project Overview

LifeTime AI is designed to be your personal assistant for life management, providing insights, recommendations, and automation for various aspects of daily life.

## Project Structure

```
LifeTime-ai-first/
├── backend/                 # FastAPI backend application
│   ├── app/                # Main application code
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Backend-specific documentation
├── frontend/               # Frontend application (to be implemented)
├── docs/                   # Project documentation
├── tests/                  # Test suites
│   └── backend/           # Backend tests
└── README.md              # This file
```

## Components

### Backend (FastAPI)

- **Framework**: FastAPI with Python 3.11+
- **Features**: RESTful API, authentication, database integration
- **Database**: SQLAlchemy ORM with SQLite (development) / PostgreSQL (production)
- **Testing**: Comprehensive test suite with pytest
- **Documentation**: Auto-generated API docs with Swagger UI

### Frontend (Planned)

- Modern web application for user interaction
- Responsive design for desktop and mobile
- Real-time updates and notifications

## Quick Start

### Backend Setup

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
   copy .env.template .env
   # Edit .env file with your configuration
   ```

5. **Run the development server**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Testing

Run the complete test suite:

```bash
# From the project root
cd backend
pytest

# Run with coverage
pytest --cov=app

# Run specific test categories
pytest tests/backend/test_app.py
pytest tests/backend/test_config.py
pytest tests/backend/test_cors.py
```

## Development Status

- ✅ Backend project structure and configuration
- ✅ FastAPI application with CORS and middleware
- ✅ Environment-based configuration management
- ✅ Comprehensive test suite
- ✅ Error handling and logging
- 🚧 Database models and migrations
- 🚧 Authentication system
- 🚧 API endpoints for core features
- 🚧 Frontend application
- 🚧 Deployment configuration

## Key Features (Planned)

- **Health Management**: Track fitness, nutrition, and wellness metrics
- **Financial Planning**: Budget tracking, expense analysis, investment insights
- **Career Development**: Goal setting, skill tracking, networking management
- **Relationship Management**: Contact organization, event reminders, communication tracking
- **AI Insights**: Personalized recommendations based on data analysis
- **Automation**: Smart reminders, routine optimization, habit tracking

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server
- **Pytest**: Testing framework
- **Loguru**: Advanced logging

### Development Tools
- **Black**: Code formatting
- **MyPy**: Static type checking
- **Flake8**: Code linting
- **Pre-commit**: Git hooks for code quality

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with appropriate tests
4. Run quality checks and tests
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Documentation

- [Backend Documentation](backend/README.md)
- [API Documentation](http://localhost:8000/docs) (when server is running)
- Additional docs in the `/docs` directory

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or suggestions, please open an issue in the GitHub repository.