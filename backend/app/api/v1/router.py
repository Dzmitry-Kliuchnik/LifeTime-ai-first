"""
API v1 router configuration.
"""

from fastapi import APIRouter

from .notes import note_router
from .users import user_router
from .week_calculation import week_router

# Create the main API router
api_router = APIRouter()

# Include user routes
api_router.include_router(user_router)

# Include week calculation routes
api_router.include_router(week_router)

# Include note routes
api_router.include_router(note_router)


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
