# LifeTime AI - Project Documentation

This directory contains comprehensive documentation for the LifeTime AI project.

## Documentation Structure

- **API Documentation**: Auto-generated from FastAPI application
- **Architecture Documentation**: System design and component interactions
- **Development Guide**: Setup, development workflows, and contribution guidelines
- **Deployment Guide**: Production deployment instructions

## Quick Links

### Development
- [Backend Setup](../backend/README.md)
- [API Documentation](http://localhost:8000/docs) (when server is running)

### Testing
- Test files are located in `/tests/backend/`
- Run tests with: `pytest` from the backend directory

### Configuration
- Environment variables: `/backend/.env.template`
- Application settings: `/backend/app/core/config.py`

## Getting Started

1. Follow the setup instructions in the main [README](../README.md)
2. Start the backend development server
3. Visit the API documentation at http://localhost:8000/docs
4. Explore the test suite in `/tests/backend/`

## Project Status

The backend foundation is complete with:
- ✅ FastAPI application structure
- ✅ Configuration management
- ✅ CORS and middleware setup
- ✅ Error handling and logging
- ✅ Comprehensive test suite

Next steps include implementing:
- Database models and migrations
- Authentication system
- Core API endpoints
- Frontend application