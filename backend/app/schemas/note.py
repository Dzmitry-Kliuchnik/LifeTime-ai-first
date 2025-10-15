"""
Pydantic schemas for Note model validation and serialization.
"""

from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)


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

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v):
        """Validate and clean tags format with enhanced empty value handling."""
        if v is None:
            return None

        # Handle array input from frontend
        if isinstance(v, list):
            # Convert array to comma-separated string
            tags = [str(tag).strip() for tag in v if str(tag).strip()]
            return ",".join(sorted(set(tags))) if tags else None

        # Handle string input (existing functionality)
        if isinstance(v, str):
            # Handle empty string or whitespace-only string
            if not v.strip():
                return None
            tags = [tag.strip() for tag in v.split(",") if tag.strip()]
            return ",".join(sorted(set(tags))) if tags else None

        # For any other type, convert to string and try to process
        if v:
            return cls.validate_tags(str(v))

        return None


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

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v):
        """Validate and clean tags format with enhanced empty value handling."""
        if v is None:
            return None

        # Handle array input from frontend
        if isinstance(v, list):
            # Convert array to comma-separated string
            tags = [str(tag).strip() for tag in v if str(tag).strip()]
            return ",".join(sorted(set(tags))) if tags else None

        # Handle string input (existing functionality)
        if isinstance(v, str):
            # Handle empty string or whitespace-only string
            if not v.strip():
                return None
            tags = [tag.strip() for tag in v.split(",") if tag.strip()]
            return ",".join(sorted(set(tags))) if tags else None

        # For any other type, convert to string and try to process
        if v:
            return cls.validate_tags(str(v))

        return None


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

    @field_serializer("tags")
    def serialize_tags(self, value: Optional[str]) -> Optional[List[str]]:
        """Convert comma-separated tags string to array for frontend."""
        if not value:
            return None
        return [tag.strip() for tag in value.split(",") if tag.strip()]

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

    @model_validator(mode="after")
    def validate_ranges(self):
        """Validate that range end values are not less than start values."""
        # Validate week range
        if (
            self.week_range_end is not None
            and self.week_range_start is not None
            and self.week_range_end < self.week_range_start
        ):
            raise ValueError(
                "week_range_end must be greater than or equal to week_range_start"
            )

        # Validate date range
        if (
            self.date_to is not None
            and self.date_from is not None
            and self.date_to < self.date_from
        ):
            raise ValueError("date_to must be greater than or equal to date_from")

        return self


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
    notes_by_week: Dict[int, int] = Field(..., description="Note count by week number")
    average_word_count: Optional[float] = Field(
        None, description="Average word count per note"
    )
    total_reading_time: Optional[int] = Field(
        None, description="Total reading time in minutes"
    )
