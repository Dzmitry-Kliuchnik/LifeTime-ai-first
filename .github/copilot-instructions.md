# GitHub Copilot Instructions for LifeTime-ai-first

This repository contains a fullstack web application built with Python FastAPI backend and Vue.js 3 frontend with TypeScript.

## Project Overview

**Technology Stack:**
- **Backend**: Python 3.11+ with FastAPI, SQLAlchemy, Alembic migrations
- **Frontend**: Vue.js 3 with TypeScript, Vite, Pinia state management
- **Database**: SQLite with optional encryption support
- **Testing**: pytest (backend), Vitest + Cypress (frontend)
- **Code Quality**: Black, mypy, flake8 (Python), ESLint, Prettier (TypeScript/Vue)

**Architecture:**
- Layered backend architecture (API → Services → Repositories → Models)
- Component-based frontend with Composition API
- RESTful API design with OpenAPI documentation
- Reactive state management with Pinia stores

## Development Guidelines

### Code Quality Standards
- Follow the established patterns in existing codebase
- Maintain type safety with TypeScript and Python type hints
- Write comprehensive tests for all new functionality
- Follow security best practices for user data and authentication
- Optimize for performance and maintainability

### File Organization
```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Configuration and database
│   ├── models/          # SQLAlchemy models
│   ├── repositories/    # Data access layer
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
frontend/
├── src/
│   ├── components/      # Vue components
│   ├── views/          # Page components
│   ├── stores/         # Pinia stores
│   ├── composables/    # Composition functions
│   └── types/          # TypeScript definitions
```

## Specialized Instructions

Apply these domain-specific guidelines:

### Backend Development
Apply guidelines from [python.instructions.md](instructions/python.instructions.md):
- Use FastAPI best practices for API development
- Follow SQLAlchemy patterns for database operations
- Implement proper error handling and validation
- Use async/await for database operations

### Frontend Development  
Apply guidelines from [vue.instructions.md](instructions/vue.instructions.md):
- Use Vue 3 Composition API consistently
- Implement proper TypeScript typing
- Follow component design principles
- Use Pinia for state management

### Testing Standards
Apply guidelines from [testing.instructions.md](instructions/testing.instructions.md):
- Write unit tests for all business logic
- Create integration tests for API endpoints
- Implement component tests for Vue components
- Add E2E tests for critical user flows

### Security Requirements
Apply guidelines from [security.instructions.md](instructions/security.instructions.md):
- Validate all user inputs
- Implement proper authentication and authorization
- Prevent SQL injection and XSS attacks
- Handle sensitive data securely

### Performance Optimization
Apply guidelines from [performance.instructions.md](instructions/performance.instructions.md):
- Optimize database queries and indexes
- Implement caching strategies
- Use lazy loading for components and routes
- Monitor and measure performance metrics

### Code Review Process
Apply guidelines from [code-review.instructions.md](instructions/code-review.instructions.md):
- Review for functionality, security, and performance
- Check test coverage and documentation
- Validate architectural decisions
- Ensure consistency with existing patterns

### Documentation Standards
Apply guidelines from [documentation.instructions.md](instructions/documentation.instructions.md):
- Maintain comprehensive API documentation
- Document components and their interfaces
- Keep architecture diagrams up to date
- Write clear README files and setup guides

## Available Assistance

### Specialized Prompts
Use these prompts for specific development tasks:

- `#setup-component` - Generate new components or modules
- `#write-tests` - Create comprehensive test suites  
- `#code-review` - Get detailed code review feedback
- `#refactor-code` - Refactor code while maintaining functionality
- `#generate-docs` - Create API and component documentation
- `#debug-issue` - Get systematic debugging assistance

### Chat Modes
Switch to specialized modes for different types of work:

- `/architect` - Architecture planning and feature design
- `/reviewer` - Comprehensive code review assistance  
- `/debugger` - Systematic debugging and troubleshooting

## Development Workflow

1. **Planning**: Use architect mode for feature planning
2. **Implementation**: Follow language-specific guidelines
3. **Testing**: Write tests using testing guidelines
4. **Review**: Use reviewer mode for code review
5. **Debugging**: Use debugger mode for issue resolution
6. **Documentation**: Generate docs with generate-docs prompt

## Key Principles

- **Type Safety**: Use TypeScript strict mode and Python type hints
- **Security First**: Validate inputs, sanitize outputs, secure authentication
- **Performance**: Optimize queries, implement caching, minimize bundle size  
- **Maintainability**: Clear code structure, comprehensive tests, good documentation
- **Consistency**: Follow established patterns and conventions throughout the codebase

## Getting Help

When asking for assistance:
1. **Provide Context**: Reference relevant files and current implementation
2. **Be Specific**: Describe exactly what you're trying to accomplish
3. **Include Error Details**: Share error messages and stack traces
4. **Mention Constraints**: Note any technical or business constraints

The GitHub Copilot configuration will help you maintain code quality, follow best practices, and accelerate development while ensuring security and performance standards are met.