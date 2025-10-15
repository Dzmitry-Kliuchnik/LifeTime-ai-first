"""
Pydantic schemas for User model validation and serialization.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserByNameCreate(BaseModel):
    """Schema for creating a user with just a name."""

    full_name: str = Field(
        ..., min_length=1, max_length=255, description="User's full name"
    )
    date_of_birth: Optional[date] = Field(None, description="User's date of birth")
    lifespan: Optional[int] = Field(
        80, ge=1, le=150, description="Expected lifespan in years"
    )
    theme: Optional[str] = Field("light", description="UI theme preference")
    font_size: Optional[int] = Field(
        14, ge=8, le=72, description="UI font size preference"
    )

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: Optional[date]) -> Optional[date]:
        """Validate date of birth is not in the future."""
        if v is None:
            return v

        today = date.today()

        if v > today:
            raise ValueError(
                f"Invalid date of birth: '{v}' is in the future. "
                f"Please provide a date on or before today ({today})."
            )

        # Check if date is reasonable (not more than 150 years ago)
        max_age_years = 150
        min_birth_date = date(today.year - max_age_years, today.month, today.day)
        if v < min_birth_date:
            raise ValueError(
                f"Invalid date of birth: '{v}' is too old (more than {max_age_years} years ago). "
                f"Please provide a date after {min_birth_date}."
            )
        return v

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v: Optional[str]) -> Optional[str]:
        """Validate theme selection."""
        if v is None:
            return v
        allowed_themes = {"light", "dark", "auto"}
        if v not in allowed_themes:
            raise ValueError(f'Theme must be one of: {", ".join(allowed_themes)}')
        return v


class UserBase(BaseModel):
    """Base schema for User with common fields."""

    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique username"
    )
    email: Optional[EmailStr] = Field(None, description="User email address (optional)")
    full_name: Optional[str] = Field(
        None, max_length=255, description="User's full display name"
    )
    bio: Optional[str] = Field(None, description="User biography or description")


class UserProfile(BaseModel):
    """Schema for user profile settings."""

    date_of_birth: Optional[date] = Field(None, description="User's date of birth")
    lifespan: Optional[int] = Field(
        80, ge=1, le=150, description="Expected lifespan in years"
    )
    theme: Optional[str] = Field("light", description="UI theme preference")
    font_size: Optional[int] = Field(
        14, ge=8, le=72, description="UI font size preference"
    )

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v: Optional[str]) -> Optional[str]:
        """Validate theme selection."""
        if v is None:
            return v
        allowed_themes = {"light", "dark", "auto"}
        if v not in allowed_themes:
            raise ValueError(f'Theme must be one of: {", ".join(allowed_themes)}')
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: Optional[date]) -> Optional[date]:
        """Validate date of birth is not in the future."""
        if v is None:
            return v

        today = date.today()

        if v > today:
            raise ValueError(
                f"Invalid date of birth: '{v}' is in the future. "
                f"Please provide a date on or before today ({today})."
            )

        # Check if date is reasonable (not more than 150 years ago)
        max_age_years = 150
        min_birth_date = date(today.year - max_age_years, today.month, today.day)
        if v < min_birth_date:
            raise ValueError(
                f"Invalid date of birth: '{v}' is too old (more than {max_age_years} years ago). "
                f"Please provide a date after {min_birth_date}."
            )
        return v


class UserCreate(UserBase, UserProfile):
    """Schema for creating a new user."""

    password: Optional[str] = Field(
        None, min_length=8, description="User password (optional for name-based users)"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for at least one uppercase, one lowercase, and one digit
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
            )

        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    date_of_birth: Optional[date] = None
    lifespan: Optional[int] = Field(None, ge=1, le=150)
    theme: Optional[str] = None
    font_size: Optional[int] = Field(None, ge=8, le=72)
    is_active: Optional[bool] = None

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v: Optional[str]) -> Optional[str]:
        """Validate theme selection."""
        if v is None:
            return v
        allowed_themes = {"light", "dark", "auto"}
        if v not in allowed_themes:
            raise ValueError(f'Theme must be one of: {", ".join(allowed_themes)}')
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: Optional[date]) -> Optional[date]:
        """Validate date of birth is not in the future."""
        if v is None:
            return v

        today = date.today()

        if v > today:
            raise ValueError(
                f"Invalid date of birth: '{v}' is in the future. "
                f"Please provide a date on or before today ({today})."
            )

        # Check if date is reasonable (not more than 150 years ago)
        max_age_years = 150
        min_birth_date = date(today.year - max_age_years, today.month, today.day)
        if v < min_birth_date:
            raise ValueError(
                f"Invalid date of birth: '{v}' is too old (more than {max_age_years} years ago). "
                f"Please provide a date after {min_birth_date}."
            )
        return v


class UserResponse(UserBase, UserProfile):
    """Schema for user response with all public fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Whether user account is active")
    is_verified: bool = Field(..., description="Whether user email is verified")
    is_superuser: bool = Field(..., description="Whether user has admin privileges")
    is_deleted: bool = Field(False, description="Soft delete flag")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    email_verified_at: Optional[datetime] = Field(
        None, description="Email verification timestamp"
    )
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last account update timestamp")
    deleted_at: Optional[datetime] = Field(None, description="Soft delete timestamp")


class UserInDB(UserResponse):
    """Schema for user as stored in database (includes sensitive fields)."""

    hashed_password: str = Field(..., description="Hashed password")
    is_deleted: bool = Field(False, description="Soft delete flag")
    deleted_at: Optional[datetime] = Field(None, description="Soft delete timestamp")


class UserProfileUpdate(UserProfile):
    """Schema for updating only profile settings."""

    # Override to make all fields optional for partial updates
    date_of_birth: Optional[date] = None
    lifespan: Optional[int] = Field(None, ge=1, le=150)
    theme: Optional[str] = None
    font_size: Optional[int] = Field(None, ge=8, le=72)


class UserSummary(BaseModel):
    """Schema for user summary information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime


class PasswordChange(BaseModel):
    """Schema for password change request."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for at least one uppercase, one lowercase, and one digit
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
            )

        return v

    def model_validate(self, values):
        """Validate that passwords match."""
        if values.get("new_password") != values.get("confirm_password"):
            raise ValueError("Passwords do not match")
        return values
