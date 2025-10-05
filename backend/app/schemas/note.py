"""
Pydantic schemas for Note model validation and serialization.
"""

from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class NoteEditHistoryEntry(BaseModel):
    """Schema for individual edit history entries."""

    timestamp: datetime = Field(..., description="When the edit was made")
    field_name: str = Field(..., description="Name of the field that was edited")
    old_value: Optional[str] = Field(
        None, description="Previous value (truncated if too long)"
    )
    new_value: Optional[str] = Field(
        None, description="New value (truncated if too long)"
    )
    edit_type: str = Field(
        ..., description="Type of edit: 'create', 'update', 'delete'"
    )


class NoteBase(BaseModel):
    """Base schema for Note with common fields."""

    title: str = Field(
        ..., min_length=1, max_length=500, description="Note title or subject"
    )
    content: str = Field(..., min_length=1, description="Main note content")
    category: Optional[str] = Field(None, max_length=100, description="Note category")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    is_favorite: bool = Field(
        False, description="Whether the note is marked as favorite"
    )
    is_archived: bool = Field(False, description="Whether the note is archived")
    note_date: Optional[date] = Field(
        None, description="Date when the note was written"
    )
    week_number: Optional[int] = Field(
        None, ge=0, description="Week number since user's birth (0-based)"
    )

    @validator("tags", pre=True)
    def validate_tags(cls, v):
        """Validate and clean tags format."""
        if v is None:
            return v
        # Clean up tags: remove extra spaces, duplicates
        if isinstance(v, str):
            tags = [tag.strip() for tag in v.split(",") if tag.strip()]
            return ",".join(sorted(set(tags)))
        return v


class NoteCreate(NoteBase):
    """Schema for creating a new note."""

    # All fields from NoteBase are available
    pass


class NoteUpdate(BaseModel):
    """Schema for updating an existing note."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=500, description="Note title or subject"
    )
    content: Optional[str] = Field(None, min_length=1, description="Main note content")
    category: Optional[str] = Field(None, max_length=100, description="Note category")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    is_favorite: Optional[bool] = Field(
        None, description="Whether the note is marked as favorite"
    )
    is_archived: Optional[bool] = Field(
        None, description="Whether the note is archived"
    )
    note_date: Optional[date] = Field(
        None, description="Date when the note was written"
    )
    week_number: Optional[int] = Field(
        None, ge=0, description="Week number since user's birth (0-based)"
    )

    @validator("tags", pre=True)
    def validate_tags(cls, v):
        """Validate and clean tags format."""
        if v is None:
            return v
        # Clean up tags: remove extra spaces, duplicates
        if isinstance(v, str):
            tags = [tag.strip() for tag in v.split(",") if tag.strip()]
            return ",".join(sorted(set(tags)))
        return v


class NoteResponse(NoteBase):
    """Schema for note responses."""

    id: int = Field(..., description="Note ID")
    owner_id: int = Field(..., description="ID of the user who owns this note")
    summary: Optional[str] = Field(None, description="AI-generated summary of the note")
    word_count: Optional[int] = Field(None, description="Number of words in the note")
    reading_time: Optional[int] = Field(
        None, description="Estimated reading time in minutes"
    )
    is_deleted: bool = Field(False, description="Soft delete flag")
    deleted_at: Optional[datetime] = Field(None, description="Soft deletion timestamp")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")
    edit_history: Optional[List[NoteEditHistoryEntry]] = Field(
        None, description="Edit history entries"
    )

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """Schema for paginated note list responses."""

    notes: List[NoteResponse] = Field(..., description="List of notes")
    total: int = Field(..., description="Total number of notes matching criteria")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class NoteSearchRequest(BaseModel):
    """Schema for note search requests."""

    query: Optional[str] = Field(None, description="Search query for title and content")
    category: Optional[str] = Field(None, description="Filter by category")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (OR operation)")
    week_number: Optional[int] = Field(
        None, ge=0, description="Filter by specific week number"
    )
    week_range_start: Optional[int] = Field(
        None, ge=0, description="Start of week range filter"
    )
    week_range_end: Optional[int] = Field(
        None, ge=0, description="End of week range filter"
    )
    date_from: Optional[date] = Field(None, description="Filter notes from this date")
    date_to: Optional[date] = Field(None, description="Filter notes to this date")
    is_favorite: Optional[bool] = Field(None, description="Filter by favorite status")
    is_archived: Optional[bool] = Field(None, description="Filter by archived status")
    include_deleted: bool = Field(False, description="Include soft-deleted notes")

    @validator("week_range_end")
    def validate_week_range(cls, v, values):
        """Validate that week range end is not less than start."""
        if (
            v is not None
            and "week_range_start" in values
            and values["week_range_start"] is not None
        ):
            if v < values["week_range_start"]:
                raise ValueError(
                    "week_range_end must be greater than or equal to week_range_start"
                )
        return v

    @validator("date_to")
    def validate_date_range(cls, v, values):
        """Validate that date_to is not before date_from."""
        if v is not None and "date_from" in values and values["date_from"] is not None:
            if v < values["date_from"]:
                raise ValueError("date_to must be greater than or equal to date_from")
        return v


class WeekNotesResponse(BaseModel):
    """Schema for getting notes for a specific week."""

    week_number: int = Field(..., description="Week number")
    week_start_date: date = Field(..., description="Start date of the week")
    week_end_date: date = Field(..., description="End date of the week")
    notes: List[NoteResponse] = Field(..., description="Notes for this week")
    total_notes: int = Field(..., description="Total number of notes in this week")


class NoteStatistics(BaseModel):
    """Schema for note statistics."""

    total_notes: int = Field(..., description="Total number of notes")
    notes_this_week: int = Field(..., description="Number of notes created this week")
    notes_this_month: int = Field(..., description="Number of notes created this month")
    favorite_notes: int = Field(..., description="Number of favorite notes")
    archived_notes: int = Field(..., description="Number of archived notes")
    categories: Dict[str, int] = Field(..., description="Note count by category")
    notes_by_week: Dict[int, int] = Field(..., description="Note count by week number")
    average_word_count: Optional[float] = Field(
        None, description="Average word count per note"
    )
    total_reading_time: Optional[int] = Field(
        None, description="Total reading time in minutes"
    )
