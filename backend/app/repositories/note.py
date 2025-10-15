"""
Note repository for database abstraction and complex queries with week-based access controls.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from app.models.note import Note
from app.schemas.note import NoteSearchRequest


class NoteRepository:
    """Repository class for Note model database operations with week-based functionality."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create(self, note_data: dict, owner_id: int) -> Note:
        """
        Create a new note.

        Args:
            note_data: Note data dictionary
            owner_id: ID of the note owner

        Returns:
            Created note instance
        """
        note = Note(**note_data, owner_id=owner_id)
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def get_by_id(
        self, note_id: int, owner_id: int, include_deleted: bool = False
    ) -> Optional[Note]:
        """
        Get a note by ID and owner.

        Args:
            note_id: Note ID
            owner_id: Owner user ID
            include_deleted: Whether to include soft-deleted notes

        Returns:
            Note instance or None if not found
        """
        query = self.db.query(Note).filter(
            and_(Note.id == note_id, Note.owner_id == owner_id)
        )

        if not include_deleted:
            query = query.filter(Note.is_deleted == False)

        return query.first()

    def get_by_week(
        self, owner_id: int, week_number: int, include_deleted: bool = False
    ) -> List[Note]:
        """
        Get all notes for a specific week.

        Args:
            owner_id: Owner user ID
            week_number: Week number since user's birth
            include_deleted: Whether to include soft-deleted notes

        Returns:
            List of notes for the specified week
        """
        query = self.db.query(Note).filter(
            and_(Note.owner_id == owner_id, Note.week_number == week_number)
        )

        if not include_deleted:
            query = query.filter(Note.is_deleted == False)

        return query.order_by(desc(Note.created_at)).all()

    def get_by_date_range(
        self,
        owner_id: int,
        start_date: date,
        end_date: date,
        include_deleted: bool = False,
    ) -> List[Note]:
        """
        Get notes within a date range.

        Args:
            owner_id: Owner user ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            include_deleted: Whether to include soft-deleted notes

        Returns:
            List of notes within the date range
        """
        query = self.db.query(Note).filter(
            and_(
                Note.owner_id == owner_id,
                Note.note_date >= start_date,
                Note.note_date <= end_date,
            )
        )

        if not include_deleted:
            query = query.filter(Note.is_deleted == False)

        return query.order_by(desc(Note.note_date), desc(Note.created_at)).all()

    def get_by_week_range(
        self,
        owner_id: int,
        start_week: int,
        end_week: int,
        include_deleted: bool = False,
    ) -> List[Note]:
        """
        Get notes within a week range.

        Args:
            owner_id: Owner user ID
            start_week: Start week number (inclusive)
            end_week: End week number (inclusive)
            include_deleted: Whether to include soft-deleted notes

        Returns:
            List of notes within the week range
        """
        query = self.db.query(Note).filter(
            and_(
                Note.owner_id == owner_id,
                Note.week_number >= start_week,
                Note.week_number <= end_week,
            )
        )

        if not include_deleted:
            query = query.filter(Note.is_deleted == False)

        return query.order_by(desc(Note.week_number), desc(Note.created_at)).all()

    def search(
        self, owner_id: int, search_request: NoteSearchRequest
    ) -> Tuple[List[Note], int]:
        """
        Search notes with various filters.

        Args:
            owner_id: Owner user ID
            search_request: Search parameters

        Returns:
            Tuple of (notes list, total count)
        """
        query = self.db.query(Note).filter(Note.owner_id == owner_id)

        # Apply soft delete filter
        if not search_request.include_deleted:
            query = query.filter(Note.is_deleted == False)

        # Text search in title and content
        if search_request.query:
            search_term = f"%{search_request.query}%"
            search_conditions = [
                Note.title.ilike(search_term),
                Note.content.ilike(search_term),
            ]
            # Only add summary search if summary column is not None
            search_conditions.append(
                and_(Note.summary.isnot(None), Note.summary.ilike(search_term))
            )
            query = query.filter(or_(*search_conditions))

        # Tags filter (OR operation)
        if search_request.tags:
            tag_conditions = []
            for tag in search_request.tags:
                tag_conditions.append(Note.tags.ilike(f"%{tag}%"))
            query = query.filter(or_(*tag_conditions))

        # Week number filters
        if search_request.week_number is not None:
            query = query.filter(Note.week_number == search_request.week_number)
        elif (
            search_request.week_range_start is not None
            or search_request.week_range_end is not None
        ):
            if search_request.week_range_start is not None:
                query = query.filter(
                    Note.week_number >= search_request.week_range_start
                )
            if search_request.week_range_end is not None:
                query = query.filter(Note.week_number <= search_request.week_range_end)

        # Date range filters
        if search_request.date_from:
            query = query.filter(Note.note_date >= search_request.date_from)
        if search_request.date_to:
            query = query.filter(Note.note_date <= search_request.date_to)

        # Status filters
        if search_request.is_favorite is not None:
            query = query.filter(Note.is_favorite == search_request.is_favorite)
        if search_request.is_archived is not None:
            query = query.filter(Note.is_archived == search_request.is_archived)

        # Get total count
        total_count = query.count()

        # Order results
        query = query.order_by(desc(Note.created_at))

        return query.all(), total_count

    def get_paginated(
        self,
        owner_id: int,
        page: int = 1,
        size: int = 20,
        include_deleted: bool = False,
        week_number: Optional[int] = None,
    ) -> Tuple[List[Note], int]:
        """
        Get paginated notes for a user with optional week filtering.

        Args:
            owner_id: Owner user ID
            page: Page number (1-based)
            size: Number of items per page
            include_deleted: Whether to include soft-deleted notes
            week_number: Optional filter by specific week number (0-based week since birth)

        Returns:
            Tuple of (notes list, total count)
        """
        query = self.db.query(Note).filter(Note.owner_id == owner_id)

        if not include_deleted:
            query = query.filter(Note.is_deleted == False)

        if week_number is not None:
            query = query.filter(Note.week_number == week_number)

        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * size
        notes = query.order_by(desc(Note.created_at)).offset(offset).limit(size).all()

        return notes, total_count

    def update(self, note: Note, update_data: dict) -> Note:
        """
        Update a note.

        Args:
            note: Note instance to update
            update_data: Fields to update

        Returns:
            Updated note instance
        """
        for field, value in update_data.items():
            if hasattr(note, field):
                setattr(note, field, value)

        self.db.commit()
        self.db.refresh(note)
        return note

    def soft_delete(self, note: Note) -> Note:
        """
        Soft delete a note.

        Args:
            note: Note instance to delete

        Returns:
            Updated note instance
        """
        note.is_deleted = True
        note.deleted_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(note)
        return note

    def restore(self, note: Note) -> Note:
        """
        Restore a soft-deleted note.

        Args:
            note: Note instance to restore

        Returns:
            Updated note instance
        """
        note.is_deleted = False
        note.deleted_at = None
        self.db.commit()
        self.db.refresh(note)
        return note

    def hard_delete(self, note: Note) -> None:
        """
        Permanently delete a note.

        Args:
            note: Note instance to delete
        """
        self.db.delete(note)
        self.db.commit()

    def get_statistics(self, owner_id: int) -> Dict:
        """
        Get note statistics for a user.

        Args:
            owner_id: Owner user ID

        Returns:
            Dictionary with various note statistics
        """
        # Base query for active notes
        base_query = self.db.query(Note).filter(
            and_(Note.owner_id == owner_id, Note.is_deleted == False)
        )

        # Total notes
        total_notes = base_query.count()

        # Current week and month (simplified - in real app would use user's birth date)
        now = datetime.utcnow()
        current_week_start = now.date() - timedelta(days=now.weekday())
        current_month_start = now.date().replace(day=1)

        notes_this_week = base_query.filter(
            Note.created_at >= current_week_start
        ).count()
        notes_this_month = base_query.filter(
            Note.created_at >= current_month_start
        ).count()

        # Status counts
        favorite_notes = base_query.filter(Note.is_favorite == True).count()
        archived_notes = base_query.filter(Note.is_archived == True).count()

        # Week distribution
        week_stats = (
            self.db.query(Note.week_number, func.count(Note.id))
            .filter(
                and_(
                    Note.owner_id == owner_id,
                    Note.is_deleted == False,
                    Note.week_number.isnot(None),
                )
            )
            .group_by(Note.week_number)
            .all()
        )

        notes_by_week = {week: count for week, count in week_stats}

        # Word count and reading time averages
        word_count_avg = (
            self.db.query(func.avg(Note.word_count))
            .filter(
                and_(
                    Note.owner_id == owner_id,
                    Note.is_deleted == False,
                    Note.word_count.isnot(None),
                )
            )
            .scalar()
        )

        total_reading_time = (
            self.db.query(func.sum(Note.reading_time))
            .filter(
                and_(
                    Note.owner_id == owner_id,
                    Note.is_deleted == False,
                    Note.reading_time.isnot(None),
                )
            )
            .scalar()
        )

        return {
            "total_notes": total_notes,
            "notes_this_week": notes_this_week,
            "notes_this_month": notes_this_month,
            "favorite_notes": favorite_notes,
            "archived_notes": archived_notes,
            "notes_by_week": notes_by_week,
            "average_word_count": float(word_count_avg) if word_count_avg else None,
            "total_reading_time": int(total_reading_time)
            if total_reading_time
            else None,
        }

    def get_tags(self, owner_id: int) -> List[str]:
        """
        Get all unique tags for a user.

        Args:
            owner_id: Owner user ID

        Returns:
            List of unique tag names
        """
        # Get all tag strings
        tag_strings = (
            self.db.query(Note.tags)
            .filter(
                and_(
                    Note.owner_id == owner_id,
                    Note.is_deleted == False,
                    Note.tags.isnot(None),
                )
            )
            .all()
        )

        # Extract individual tags
        all_tags = set()
        for tag_string in tag_strings:
            if tag_string[0]:
                tags = [tag.strip() for tag in tag_string[0].split(",") if tag.strip()]
                all_tags.update(tags)

        return sorted(list(all_tags))

    def exists(self, note_id: int, owner_id: int) -> bool:
        """
        Check if a note exists for the given owner.

        Args:
            note_id: Note ID
            owner_id: Owner user ID

        Returns:
            True if note exists, False otherwise
        """
        return (
            self.db.query(Note)
            .filter(
                and_(
                    Note.id == note_id,
                    Note.owner_id == owner_id,
                    Note.is_deleted == False,
                )
            )
            .first()
            is not None
        )
