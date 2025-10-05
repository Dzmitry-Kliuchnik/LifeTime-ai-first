"""
Note service layer for business logic and CRUD operations with week-based restrictions.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.note import Note
from app.models.user import User
from app.repositories.note import NoteRepository
from app.schemas.note import (
    NoteCreate,
    NoteListResponse,
    NoteResponse,
    NoteSearchRequest,
    NoteStatistics,
    NoteUpdate,
    WeekNotesResponse,
)
from app.services.week_calculation import WeekCalculationService

logger = logging.getLogger(__name__)


class NoteService:
    """Service class for note-related business logic and database operations."""

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
        self.repository = NoteRepository(db)
        self.week_service = WeekCalculationService()

    def _calculate_text_metadata(self, content: str) -> Dict[str, int]:
        """
        Calculate word count and estimated reading time for content.

        Args:
            content: Text content to analyze

        Returns:
            Dictionary with word_count and reading_time
        """
        if not content:
            return {"word_count": 0, "reading_time": 0}

        # Simple word count (can be enhanced with better tokenization)
        word_count = len(content.split())

        # Estimated reading time (average 200 words per minute)
        reading_time = max(1, round(word_count / 200))

        return {"word_count": word_count, "reading_time": reading_time}

    def _validate_week_number(self, user: User, week_number: Optional[int]) -> None:
        """
        Validate that week number is not in the future.

        Args:
            user: User instance
            week_number: Week number to validate

        Raises:
            ValidationError: If week number is invalid or in the future
        """
        if week_number is None:
            return

        if week_number < 0:
            raise ValidationError("Week number cannot be negative")

        # Check user has date of birth to calculate current week
        if not user.date_of_birth:
            raise ValidationError(
                "User must have date of birth set to use week-based notes"
            )

        # Get current week index for the user
        try:
            current_week = self.week_service.calculate_current_week_index(
                user.date_of_birth, "UTC"
            )
        except Exception as e:
            logger.error(f"Error calculating current week for user {user.id}: {e}")
            raise ValidationError("Unable to calculate current week")

        # Prevent future week notes (business rule)
        if week_number > current_week:
            raise ValidationError(
                f"Cannot create notes for future weeks. Current week: {current_week}, "
                f"requested week: {week_number}"
            )

    def _create_edit_history_entry(
        self,
        field_name: str,
        old_value: Optional[str],
        new_value: Optional[str],
        edit_type: str,
    ) -> Dict:
        """
        Create an edit history entry.

        Args:
            field_name: Name of the field that was edited
            old_value: Previous value
            new_value: New value
            edit_type: Type of edit ('create', 'update', 'delete')

        Returns:
            Edit history entry dictionary
        """
        # Truncate long values for history
        max_length = 100
        if old_value and len(str(old_value)) > max_length:
            old_value = str(old_value)[:max_length] + "..."
        if new_value and len(str(new_value)) > max_length:
            new_value = str(new_value)[:max_length] + "..."

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "field_name": field_name,
            "old_value": str(old_value) if old_value is not None else None,
            "new_value": str(new_value) if new_value is not None else None,
            "edit_type": edit_type,
        }

    def _add_to_edit_history(
        self, note: Note, field_name: str, old_value, new_value, edit_type: str
    ) -> None:
        """
        Add an entry to the note's edit history.

        Args:
            note: Note instance
            field_name: Name of the field that was edited
            old_value: Previous value
            new_value: New value
            edit_type: Type of edit
        """
        history_entry = self._create_edit_history_entry(
            field_name, old_value, new_value, edit_type
        )

        if note.edit_history is None:
            note.edit_history = []
        elif isinstance(note.edit_history, str):
            # Handle case where edit_history might be stored as JSON string
            try:
                note.edit_history = json.loads(note.edit_history)
            except (json.JSONDecodeError, TypeError):
                note.edit_history = []

        # Keep only last 50 history entries to prevent unbounded growth
        if len(note.edit_history) >= 50:
            note.edit_history = note.edit_history[-49:]

        note.edit_history.append(history_entry)

    def create_note(self, user_id: int, note_data: NoteCreate) -> NoteResponse:
        """
        Create a new note with business rule validation.

        Args:
            user_id: ID of the note owner
            note_data: Note creation data

        Returns:
            Created note response

        Raises:
            NotFoundError: If user not found
            ValidationError: If validation fails (e.g., future week)
        """
        # Get user to validate week restrictions
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        # Validate week number if provided
        self._validate_week_number(user, note_data.week_number)

        # Calculate text metadata
        text_metadata = self._calculate_text_metadata(note_data.content)

        # Prepare note data
        note_dict = note_data.model_dump(exclude_unset=True)
        note_dict.update(text_metadata)

        # Set note_date if not provided and week_number is provided
        if (
            note_data.week_number is not None
            and note_data.note_date is None
            and user.date_of_birth
        ):
            try:
                week_start_date = self.week_service.get_week_start_date(
                    user.date_of_birth, note_data.week_number
                )
                note_dict["note_date"] = week_start_date
            except Exception as e:
                logger.warning(f"Could not calculate week start date: {e}")

        # Create the note
        note = self.repository.create(note_dict, user_id)

        # Add creation to edit history
        self._add_to_edit_history(note, "note", None, note.title, "create")

        # Save the updated edit history
        self.db.commit()
        self.db.refresh(note)

        logger.info(f"Created note {note.id} for user {user_id}")
        return NoteResponse.model_validate(note)

    def get_note(self, user_id: int, note_id: int) -> NoteResponse:
        """
        Get a note by ID.

        Args:
            user_id: ID of the note owner
            note_id: Note ID

        Returns:
            Note response

        Raises:
            NotFoundError: If note not found
        """
        note = self.repository.get_by_id(note_id, user_id)
        if not note:
            raise NotFoundError(f"Note with ID {note_id} not found")

        return NoteResponse.model_validate(note)

    def update_note(
        self, user_id: int, note_id: int, note_data: NoteUpdate
    ) -> NoteResponse:
        """
        Update an existing note.

        Args:
            user_id: ID of the note owner
            note_id: Note ID
            note_data: Note update data

        Returns:
            Updated note response

        Raises:
            NotFoundError: If note not found
            ValidationError: If validation fails
        """
        # Get existing note
        note = self.repository.get_by_id(note_id, user_id)
        if not note:
            raise NotFoundError(f"Note with ID {note_id} not found")

        # Get user for week validation
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        # Validate week number if being updated
        if note_data.week_number is not None:
            self._validate_week_number(user, note_data.week_number)

        # Track changes for edit history
        update_dict = note_data.model_dump(exclude_unset=True)

        # Update text metadata if content changed
        if "content" in update_dict:
            text_metadata = self._calculate_text_metadata(update_dict["content"])
            update_dict.update(text_metadata)

        # Set note_date if week_number is updated but note_date is not
        if (
            "week_number" in update_dict
            and "note_date" not in update_dict
            and update_dict["week_number"] is not None
            and user.date_of_birth
        ):
            try:
                week_start_date = self.week_service.get_week_start_date(
                    user.date_of_birth, update_dict["week_number"]
                )
                update_dict["note_date"] = week_start_date
            except Exception as e:
                logger.warning(f"Could not calculate week start date: {e}")

        # Record changes in edit history before updating
        # Track only core fields that should be in edit history
        trackable_fields = [
            "title",
            "content",
            "category",
            "tags",
            "week_number",
            "note_date",
        ]
        for field, new_value in update_dict.items():
            if field in trackable_fields and hasattr(note, field):
                old_value = getattr(note, field)
                if old_value != new_value:
                    self._add_to_edit_history(
                        note, field, old_value, new_value, "update"
                    )

        # Add the updated edit history to the update dict so it gets saved
        if note.edit_history is not None:
            update_dict["edit_history"] = note.edit_history

        # Update the note
        updated_note = self.repository.update(note, update_dict)

        logger.info(f"Updated note {note_id} for user {user_id}")
        return NoteResponse.model_validate(updated_note)

    def delete_note(self, user_id: int, note_id: int) -> None:
        """
        Soft delete a note.

        Args:
            user_id: ID of the note owner
            note_id: Note ID

        Raises:
            NotFoundError: If note not found
        """
        note = self.repository.get_by_id(note_id, user_id)
        if not note:
            raise NotFoundError(f"Note with ID {note_id} not found")

        # Add deletion to edit history
        self._add_to_edit_history(note, "note", note.title, None, "delete")

        # Soft delete
        self.repository.soft_delete(note)

        logger.info(f"Deleted note {note_id} for user {user_id}")

    def restore_note(self, user_id: int, note_id: int) -> NoteResponse:
        """
        Restore a soft-deleted note.

        Args:
            user_id: ID of the note owner
            note_id: Note ID

        Returns:
            Restored note response

        Raises:
            NotFoundError: If note not found
        """
        note = self.repository.get_by_id(note_id, user_id, include_deleted=True)
        if not note or not note.is_deleted:
            raise NotFoundError(f"Deleted note with ID {note_id} not found")

        # Add restoration to edit history
        self._add_to_edit_history(note, "note", None, note.title, "restore")

        # Restore the note
        restored_note = self.repository.restore(note)

        logger.info(f"Restored note {note_id} for user {user_id}")
        return NoteResponse.model_validate(restored_note)

    def get_week_notes(self, user_id: int, week_number: int) -> WeekNotesResponse:
        """
        Get all notes for a specific week.

        Args:
            user_id: ID of the note owner
            week_number: Week number since user's birth

        Returns:
            Week notes response

        Raises:
            NotFoundError: If user not found
            ValidationError: If week calculation fails
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        if not user.date_of_birth:
            raise ValidationError(
                "User must have date of birth set to use week-based notes"
            )

        # Calculate week dates
        try:
            week_start_date = self.week_service.get_week_start_date(
                user.date_of_birth, week_number
            )
            week_end_date = week_start_date + timedelta(days=6)
        except Exception as e:
            logger.error(f"Error calculating week dates: {e}")
            raise ValidationError("Unable to calculate week dates")

        # Get notes for the week
        notes = self.repository.get_by_week(user_id, week_number)
        note_responses = [NoteResponse.model_validate(note) for note in notes]

        return WeekNotesResponse(
            week_number=week_number,
            week_start_date=week_start_date,
            week_end_date=week_end_date,
            notes=note_responses,
            total_notes=len(note_responses),
        )

    def search_notes(
        self,
        user_id: int,
        search_request: NoteSearchRequest,
        page: int = 1,
        size: int = 20,
    ) -> NoteListResponse:
        """
        Search notes with various filters.

        Args:
            user_id: ID of the note owner
            search_request: Search parameters
            page: Page number (1-based)
            size: Number of items per page

        Returns:
            Paginated note list response
        """
        notes, total_count = self.repository.search(user_id, search_request)

        # Apply pagination
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_notes = notes[start_idx:end_idx]

        note_responses = [NoteResponse.model_validate(note) for note in paginated_notes]

        pages = (total_count + size - 1) // size  # Ceiling division

        return NoteListResponse(
            notes=note_responses,
            total=total_count,
            page=page,
            size=size,
            pages=pages,
        )

    def get_paginated_notes(
        self, user_id: int, page: int = 1, size: int = 20, include_deleted: bool = False
    ) -> NoteListResponse:
        """
        Get paginated notes for a user.

        Args:
            user_id: ID of the note owner
            page: Page number (1-based)
            size: Number of items per page
            include_deleted: Whether to include soft-deleted notes

        Returns:
            Paginated note list response
        """
        notes, total_count = self.repository.get_paginated(
            user_id, page, size, include_deleted
        )
        note_responses = [NoteResponse.model_validate(note) for note in notes]

        pages = (total_count + size - 1) // size  # Ceiling division

        return NoteListResponse(
            notes=note_responses,
            total=total_count,
            page=page,
            size=size,
            pages=pages,
        )

    def get_note_statistics(self, user_id: int) -> NoteStatistics:
        """
        Get note statistics for a user.

        Args:
            user_id: ID of the note owner

        Returns:
            Note statistics
        """
        stats = self.repository.get_statistics(user_id)
        return NoteStatistics(**stats)

    def get_categories(self, user_id: int) -> List[str]:
        """
        Get all unique categories for a user.

        Args:
            user_id: ID of the note owner

        Returns:
            List of unique category names
        """
        return self.repository.get_categories(user_id)

    def get_tags(self, user_id: int) -> List[str]:
        """
        Get all unique tags for a user.

        Args:
            user_id: ID of the note owner

        Returns:
            List of unique tag names
        """
        return self.repository.get_tags(user_id)
