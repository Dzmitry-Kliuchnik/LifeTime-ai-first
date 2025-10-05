"""
API v1 router configuration.
"""

from fastapi import APIRouter

# Create the main API router
api_router = APIRouter()


# Health endpoint for API
@api_router.get("/health", tags=["health"])
async def api_health():
    """API health check endpoint."""
    return {"status": "healthy", "api_version": "v1"}


# Placeholder for future routes
@api_router.get("/", tags=["api"])
async def api_root():
    """API root endpoint."""
    return {"message": "LifeTime AI API v1", "status": "active"}
