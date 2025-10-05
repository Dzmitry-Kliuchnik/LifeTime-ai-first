"""
Pydantic schemas for week calculation API endpoints.
"""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# Constants for field descriptions and validation messages
DOB_DESCRIPTION = "Date of birth in YYYY-MM-DD format"
DOB_ISO_DESCRIPTION = "Date of birth (ISO format)"
LIFESPAN_DESCRIPTION = "Expected lifespan in years"
TIMEZONE_EXAMPLE = "America/New_York"
TIMEZONE_DESCRIPTION = "Timezone for calculations"
FUTURE_DOB_ERROR = "Date of birth cannot be in the future"
MIN_YEAR_ERROR = "Date of birth must be after year 1900"


class WeekTypeSchema(str, Enum):
    """Week type enumeration for API responses."""

    NORMAL = "normal"
    BIRTHDAY = "birthday"
    YEAR_START = "year_start"
    LEAP_DAY = "leap_day"
    DST_TRANSITION = "dst_transition"


def validate_dob_common(v):
    """Common DOB validation logic."""
    if v > date.today():
        raise ValueError(FUTURE_DOB_ERROR)
    if v.year < 1900:
        raise ValueError(MIN_YEAR_ERROR)
    return v


class WeekCalculationRequest(BaseModel):
    """Request schema for week calculations."""

    date_of_birth: date = Field(
        ..., description=DOB_DESCRIPTION, json_schema_extra={"example": "1990-01-15"}
    )
    lifespan_years: int = Field(
        80,
        ge=1,
        le=150,
        description=LIFESPAN_DESCRIPTION,
        json_schema_extra={"example": 80},
    )
    timezone: str = Field(
        "UTC",
        description="Timezone for calculations (e.g., 'America/New_York')",
        json_schema_extra={"example": TIMEZONE_EXAMPLE},
    )

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v):
        """Validate date of birth is not in the future."""
        return validate_dob_common(v)


class CurrentWeekRequest(BaseModel):
    """Request schema for current week calculation."""

    date_of_birth: date = Field(
        ..., description=DOB_DESCRIPTION, json_schema_extra={"example": "1990-01-15"}
    )
    timezone: str = Field(
        "UTC",
        description=TIMEZONE_DESCRIPTION,
        json_schema_extra={"example": TIMEZONE_EXAMPLE},
    )

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v):
        """Validate date of birth is not in the future."""
        return validate_dob_common(v)


class WeekSummaryRequest(BaseModel):
    """Request schema for specific week summary."""

    date_of_birth: date = Field(
        ..., description=DOB_DESCRIPTION, json_schema_extra={"example": "1990-01-15"}
    )
    week_index: int = Field(
        ...,
        ge=0,
        description="Week index (0-based) since birth",
        json_schema_extra={"example": 1742},
    )
    timezone: str = Field(
        "UTC",
        description=TIMEZONE_DESCRIPTION,
        json_schema_extra={"example": TIMEZONE_EXAMPLE},
    )

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v):
        """Validate date of birth is not in the future."""
        return validate_dob_common(v)


class AgeInfo(BaseModel):
    """Schema for age information."""

    years: int = Field(..., description="Years lived")
    months: int = Field(..., description="Additional months")
    days: int = Field(..., description="Additional days")


class WeekSummaryResponse(BaseModel):
    """Response schema for week summary."""

    week_index: int = Field(..., description="Week index (0-based) since birth")
    week_start: str = Field(..., description="Start date of the week (ISO format)")
    week_end: str = Field(..., description="End date of the week (ISO format)")
    week_type: WeekTypeSchema = Field(..., description="Type of week")
    age_years: int = Field(..., description="Age in years at this week")
    age_months: int = Field(..., description="Additional months")
    age_days: int = Field(..., description="Additional days")
    days_lived: int = Field(..., description="Total days lived at start of this week")
    is_current_week: bool = Field(..., description="Whether this is the current week")


class LifeProgressResponse(BaseModel):
    """Response schema for life progress calculation."""

    date_of_birth: str = Field(..., description=DOB_ISO_DESCRIPTION)
    lifespan_years: int = Field(..., description=LIFESPAN_DESCRIPTION)
    timezone: str = Field(..., description="Timezone used for calculations")
    total_weeks: int = Field(..., description="Total weeks in expected lifespan")
    current_week_index: int = Field(..., description="Current week index (0-based)")
    weeks_lived: int = Field(..., description="Number of weeks lived")
    weeks_remaining: int = Field(
        ..., description="Weeks remaining in expected lifespan"
    )
    progress_percentage: float = Field(..., description="Life progress as percentage")
    current_age: AgeInfo = Field(..., description="Current age information")
    days_lived: int = Field(..., description="Total days lived")
    current_week_info: WeekSummaryResponse = Field(
        ..., description="Current week information"
    )


class TotalWeeksResponse(BaseModel):
    """Response schema for total weeks calculation."""

    date_of_birth: str = Field(..., description=DOB_ISO_DESCRIPTION)
    lifespan_years: int = Field(..., description=LIFESPAN_DESCRIPTION)
    total_weeks: int = Field(..., description="Total weeks in expected lifespan")


class CurrentWeekResponse(BaseModel):
    """Response schema for current week calculation."""

    date_of_birth: str = Field(..., description=DOB_ISO_DESCRIPTION)
    timezone: str = Field(..., description="Timezone used for calculations")
    current_week_index: int = Field(..., description="Current week index (0-based)")
    weeks_lived: int = Field(..., description="Number of weeks lived")


class ErrorResponse(BaseModel):
    """Response schema for API errors."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
