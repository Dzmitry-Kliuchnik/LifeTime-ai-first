"""
Main FastAPI application factory and configuration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import add_exception_handlers
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    setup_logging()
    startup_database()
    yield
    # Shutdown - placeholder for cleanup tasks


def startup_database():
    """Initialize database connection and verify setup."""
    import logging

    from app.core.database import get_database_info, verify_database_connection

    logger = logging.getLogger(__name__)

    # Verify database connection
    if verify_database_connection():
        logger.info("Database connection verified successfully")

        # Log database configuration
        db_info = get_database_info()
        logger.info(f"Database configuration: {db_info}")
    else:
        logger.error("Database connection failed during startup")
        raise RuntimeError("Database connection failed")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="LifeTime AI - Personal Life Management Assistant",
        debug=settings.debug,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        lifespan=lifespan,
    )

    # Add middleware
    setup_middleware(app)

    # Add exception handlers
    add_exception_handlers(app)

    # Include routers
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint with basic API information."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs_url": settings.docs_url,
            "status": "healthy",
        }

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        from app.core.database import verify_database_connection

        db_healthy = verify_database_connection()
        overall_status = "healthy" if db_healthy else "unhealthy"

        return {
            "status": overall_status,
            "service": settings.app_name,
            "version": settings.app_version,
            "database": "healthy" if db_healthy else "unhealthy",
        }

    return app


def setup_middleware(app: FastAPI) -> None:
    """
    Configure middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )

    # Trusted host middleware for security (allow testserver in tests)
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", settings.host, "testserver"],
        )


# Create the application instance
app = create_app()
