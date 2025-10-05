"""
Note model for storing user notes and content with week-based organization.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, Date, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Note(Base):
    """Note model for storing user notes with full-text search capabilities."""

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Note content
    title: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="Note title or subject"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Main note content"
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="AI-generated summary of the note"
    )

    # Note metadata
    is_favorite: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the note is marked as favorite",
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Whether the note is archived"
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Soft delete flag"
    )

    # Categories and tags
    category: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="Note category"
    )
    tags: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Comma-separated tags"
    )

    # AI and search metadata
    word_count: Mapped[Optional[int]] = mapped_column(
        nullable=True, comment="Number of words in the note"
    )
    reading_time: Mapped[Optional[int]] = mapped_column(
        nullable=True, comment="Estimated reading time in minutes"
    )

    # Week-based organization fields
    week_number: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Week number since user's birth (0-based)"
    )
    note_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Date when the note was written (for weekly organization)",
    )

    # Edit history as JSON field
    edit_history: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="JSON array of edit history entries"
    )

    # Timestamps
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, comment="Soft deletion timestamp"
    )

    # Foreign key to user
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID of the user who owns this note",
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="notes")

    # Add database indexes for performance
    __table_args__ = (
        Index("ix_notes_owner_created", "owner_id", "created_at"),
        Index("ix_notes_owner_favorite", "owner_id", "is_favorite"),
        Index("ix_notes_owner_archived", "owner_id", "is_archived"),
        Index("ix_notes_owner_deleted", "owner_id", "is_deleted"),
        Index(
            "ix_notes_owner_week", "owner_id", "week_number"
        ),  # For week-based queries
        Index(
            "ix_notes_owner_note_date", "owner_id", "note_date"
        ),  # For date-based queries
        Index("ix_notes_category", "category"),
        Index("ix_notes_title_search", "title"),  # For text search
        Index(
            "ix_notes_week_date", "week_number", "note_date"
        ),  # For combined week/date queries
    )

    def __repr__(self) -> str:
        return f"<Note(id={self.id}, title='{self.title[:50]}...', owner_id={self.owner_id})>"
