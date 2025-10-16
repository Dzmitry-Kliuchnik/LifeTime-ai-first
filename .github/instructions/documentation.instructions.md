<!-- Based on/Inspired by: https://github.com/github/awesome-copilot/blob/main/instructions/markdown.instructions.md -->
---
applyTo: "**/*.md,**/*.rst,**/*.txt"
description: "Documentation standards and best practices for LifeTime-ai-first project"
---

# Documentation Standards

Apply these documentation guidelines to maintain consistent, high-quality documentation across the LifeTime-ai-first project.

## Documentation Types

### API Documentation
- Use FastAPI's automatic OpenAPI generation for REST endpoints
- Include comprehensive docstrings for all Python functions and classes
- Document request/response schemas with Pydantic models
- Provide usage examples for complex endpoints

### Component Documentation
- Document Vue.js components with clear prop and event descriptions
- Use TypeScript interfaces to document component APIs
- Include usage examples and common patterns
- Document composables and their return values

### Architecture Documentation
- Maintain high-level system architecture diagrams
- Document data flow between backend and frontend
- Explain database schema and relationships
- Keep deployment and configuration guides up to date

## Formatting Standards

### Markdown Guidelines
- Use `##` for main sections and `###` for subsections
- Limit line length to 100 characters for readability
- Use fenced code blocks with language specification
- Include meaningful alt text for images
- Use descriptive link text, not "click here" or raw URLs

### Code Documentation
- Write clear, concise docstrings for all public functions
- Use type hints consistently in Python code
- Document complex algorithms and business logic
- Keep comments focused on "why" not "what"

### README Structure
Follow this structure for README files:
1. Project title and brief description
2. Installation and setup instructions
3. Usage examples and common workflows
4. API reference or component documentation links
5. Contributing guidelines
6. License information

## Content Guidelines

### Writing Style
- Use clear, concise language suitable for technical audiences
- Write in active voice when possible
- Be specific and avoid vague terms
- Include practical examples and use cases

### Code Examples
- Provide complete, runnable examples
- Use realistic data in examples
- Include error handling in code samples
- Show both basic and advanced usage patterns

### Technical Accuracy
- Test all code examples before including them
- Keep documentation synchronized with code changes
- Update examples when APIs change
- Validate external links and resources

## Documentation Tools

### Backend Documentation
- Use Python docstrings (Google or NumPy style)
- Generate API documentation with FastAPI's built-in tools
- Document database models and relationships
- Include migration guides for schema changes

### Frontend Documentation
- Use JSDoc comments for TypeScript functions
- Document Vue component props, events, and slots
- Create style guides for UI components
- Maintain component library documentation

### Project Documentation
- Keep README files updated with current setup instructions
- Maintain changelog with version history
- Document deployment processes and requirements
- Create troubleshooting guides for common issues

## Quality Standards

### Documentation Review
- Include documentation updates in code reviews
- Verify examples work with current codebase
- Check for spelling and grammar errors
- Ensure consistency with existing documentation

### Maintenance
- Update documentation with each release
- Remove outdated information promptly
- Monitor and fix broken links
- Review and update examples regularly

### Accessibility
- Use semantic HTML in documentation sites
- Provide alt text for all images
- Ensure proper heading hierarchy
- Use sufficient color contrast in diagrams

## Documentation Workflow

### Development Process
1. Write documentation alongside code development
2. Include documentation changes in pull requests
3. Review documentation for accuracy and completeness
4. Update related documentation when making changes

### Publishing Process
- Keep internal documentation in the repository
- Generate and publish API documentation automatically
- Maintain public-facing documentation for users
- Version documentation alongside code releases

## Best Practices

### For Developers
- Document design decisions and trade-offs
- Explain non-obvious code patterns and solutions
- Keep documentation close to the code it describes
- Use consistent terminology throughout the project

### For Users
- Provide clear setup and installation instructions
- Include common use cases and workflows
- Offer troubleshooting guides for typical problems
- Maintain FAQ sections for frequently asked questions

### For Contributors
- Document contribution guidelines and coding standards
- Explain the development workflow and tools
- Provide templates for common documentation types
- Include guidelines for testing and validation