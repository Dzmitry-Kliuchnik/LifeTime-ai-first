"""
User model for authentication and user management.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .note import Note


class User(Base):
    """User model for storing user account information."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Basic user information
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="Unique username for login",
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
        comment="User email address (optional for name-based users)",
    )
    hashed_password: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Bcrypt hashed password (optional for name-based users)",
    )

    # User status and metadata
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the user account is active",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the user email is verified",
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the user has admin privileges",
    )

    # Optional profile information
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="User's full display name"
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="User biography or description"
    )

    # Life management profile fields
    date_of_birth: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="User's date of birth for life calculations"
    )
    lifespan: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Expected lifespan in years (default: 80)"
    )
    theme: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="light",
        comment="UI theme preference (light/dark)",
    )
    font_size: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=14, comment="UI font size preference"
    )

    # Soft delete functionality
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Soft delete flag for user account",
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, comment="Timestamp when user was soft deleted"
    )

    # Account timestamps
    last_login: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, comment="Last login timestamp"
    )
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, comment="Email verification timestamp"
    )

    # Relationships
    notes: Mapped[list["Note"]] = relationship(
        "Note", back_populates="owner", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
