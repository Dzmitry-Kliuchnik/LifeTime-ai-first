"""
REST API endpoints for note management with week-based organization.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.note import (
    NoteCreate,
    NoteListResponse,
    NoteResponse,
    NoteSearchRequest,
    NoteStatistics,
    NoteUpdate,
    WeekNotesResponse,
)
from app.services.note import NoteService

logger = logging.getLogger(__name__)

# Create router for note endpoints
note_router = APIRouter(prefix="/notes", tags=["notes"])


def get_note_service(db: Session = Depends(get_db)) -> NoteService:
    """Dependency to get NoteService instance."""
    return NoteService(db)


@note_router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    user_id: int = Query(..., description="ID of the note owner"),
    note_service: NoteService = Depends(get_note_service),
):
    """
    Create a new note.

    Args:
        note_data: Note creation data
        user_id: ID of the note owner
        note_service: Note service instance

    Returns:
        Created note response

    Raises:
        HTTP 404: If user not found
        HTTP 422: If validation fails (e.g., future week notes)
    """
    try:
        return note_service.create_note(user_id, note_data)
    except NotFoundError as e:
        logger.warning(f"User not found when creating note: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error when creating note: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating note",
        )


@note_router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    user_id: int = Query(..., description="ID of the note owner"),
    note_service: NoteService = Depends(get_note_service),
):
    """
    Get a note by ID.

    Args:
        note_id: Note ID
        user_id: ID of the note owner
        note_service: Note service instance

    Returns:
        Note response

    Raises:
        HTTP 404: If note not found
    """
    try:
        return note_service.get_note(user_id, note_id)
    except NotFoundError as e:
        logger.warning(f"Note not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error retrieving note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving note",
        )


@note_router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    user_id: int = Query(..., description="ID of the note owner"),
    note_service: NoteService = Depends(get_note_service),
):
    """
    Update an existing note.

    Args:
        note_id: Note ID
        note_data: Note update data
        user_id: ID of the note owner
        note_service: Note service instance

    Returns:
        Updated note response

    Raises:
        HTTP 404: If note not found
        HTTP 422: If validation fails
    """
    try:
        return note_service.update_note(user_id, note_id, note_data)
    except NotFoundError as e:
        logger.warning(f"Note not found for update: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error when updating note: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error updating note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating note",
        )


@note_router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    user_id: int = Query(..., description="ID of the note owner"),
    note_service: NoteService = Depends(get_note_service),
):
    """
    Soft delete a note.

    Args:
        note_id: Note ID
        user_id: ID of the note owner
        note_service: Note service instance

    Raises:
        HTTP 404: If note not found
    """
    try:
        note_service.delete_note(user_id, note_id)
    except NotFoundError as e:
        logger.warning(f"Note not found for deletion: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error deleting note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting note",
        )


@note_router.post("/{note_id}/restore", response_model=NoteResponse)
async def restore_note(
    note_id: int,
    user_id: int = Query(..., description="ID of the note owner"),
    note_service: NoteService = Depends(get_note_service),
):
    """
    Restore a soft-deleted note.

    Args:
        note_id: Note ID
        user_id: ID of the note owner
        note_service: Note service instance

    Returns:
        Restored note response

    Raises:
        HTTP 404: If note not found
    """
    try:
        return note_service.restore_note(user_id, note_id)
    except NotFoundError as e:
        logger.warning(f"Deleted note not found for restoration: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error restoring note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while restoring note",
        )


@note_router.get("/", response_model=NoteListResponse)
async def get_notes(
    user_id: int = Query(..., description="ID of the note owner"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    include_deleted: bool = Query(False, description="Include soft-deleted notes"),
    note_service: NoteService = Depends(get_note_service),
):
    """
    Get paginated notes for a user.

    Args:
        user_id: ID of the note owner
        page: Page number (1-based)
        size: Number of items per page
        include_deleted: Include soft-deleted notes
        note_service: Note service instance

    Returns:
        Paginated note list response
    """
    try:
        return note_service.get_paginated_notes(user_id, page, size, include_deleted)
    except Exception as e:
        logger.error(f"Unexpected error retrieving notes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving notes",
        )


@note_router.post("/search", response_model=NoteListResponse)
async def search_notes(
    search_request: NoteSearchRequest,
    user_id: int = Query(..., description="ID of the note owner"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    note_service: NoteService = Depends(get_note_service),
):
    """
    Search notes with various filters.

    Args:
        search_request: Search parameters
        user_id: ID of the note owner
        page: Page number (1-based)
        size: Number of items per page
        note_service: Note service instance

    Returns:
        Paginated note list response
    """
    try:
        return note_service.search_notes(user_id, search_request, page, size)
    except Exception as e:
        logger.error(f"Unexpected error searching notes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while searching notes",
        )


@note_router.get("/week/{week_number}", response_model=WeekNotesResponse)
async def get_week_notes(
    week_number: int,
    user_id: int = Query(..., description="ID of the note owner"),
    note_service: NoteService = Depends(get_note_service),
):
    """
    Get all notes for a specific week.

    Args:
        week_number: Week number since user's birth (0-based)
        user_id: ID of the note owner
        note_service: Note service instance

    Returns:
        Week notes response

    Raises:
        HTTP 404: If user not found
        HTTP 422: If week calculation fails
    """
    try:
        return note_service.get_week_notes(user_id, week_number)
    except NotFoundError as e:
        logger.warning(f"User not found when getting week notes: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error when getting week notes: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting week notes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving week notes",
        )


@note_router.get("/stats/summary", response_model=NoteStatistics)
async def get_note_statistics(
    user_id: int = Query(..., description="ID of the note owner"),
    note_service: NoteService = Depends(get_note_service),
):
    """
    Get note statistics for a user.

    Args:
        user_id: ID of the note owner
        note_service: Note service instance

    Returns:
        Note statistics
    """
    try:
        return note_service.get_note_statistics(user_id)
    except Exception as e:
        logger.error(f"Unexpected error getting note statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving note statistics",
        )


@note_router.get("/meta/categories", response_model=List[str])
async def get_categories(
    user_id: int = Query(..., description="ID of the note owner"),
    note_service: NoteService = Depends(get_note_service),
):
    """
    Get all unique categories for a user.

    Args:
        user_id: ID of the note owner
        note_service: Note service instance

    Returns:
        List of unique category names
    """
    try:
        return note_service.get_categories(user_id)
    except Exception as e:
        logger.error(f"Unexpected error getting categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving categories",
        )


@note_router.get("/meta/tags", response_model=List[str])
async def get_tags(
    user_id: int = Query(..., description="ID of the note owner"),
    note_service: NoteService = Depends(get_note_service),
):
    """
    Get all unique tags for a user.

    Args:
        user_id: ID of the note owner
        note_service: Note service instance

    Returns:
        List of unique tag names
    """
    try:
        return note_service.get_tags(user_id)
    except Exception as e:
        logger.error(f"Unexpected error getting tags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving tags",
        )
