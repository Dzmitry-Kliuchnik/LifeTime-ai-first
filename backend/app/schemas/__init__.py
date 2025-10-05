"""
Pydantic schemas for LifeTime AI application.
"""

from .user import (
    PasswordChange,
    UserBase,
    UserCreate,
    UserInDB,
    UserProfile,
    UserProfileUpdate,
    UserResponse,
    UserSummary,
    UserUpdate,
)
from .week_calculation import (
    AgeInfo,
    CurrentWeekRequest,
    CurrentWeekResponse,
    ErrorResponse,
    LifeProgressResponse,
    TotalWeeksResponse,
    WeekCalculationRequest,
    WeekSummaryRequest,
    WeekSummaryResponse,
    WeekTypeSchema,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserProfile",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    "UserProfileUpdate",
    "UserSummary",
    "PasswordChange",
    # Week calculation schemas
    "WeekTypeSchema",
    "WeekCalculationRequest",
    "CurrentWeekRequest",
    "WeekSummaryRequest",
    "AgeInfo",
    "WeekSummaryResponse",
    "LifeProgressResponse",
    "TotalWeeksResponse",
    "CurrentWeekResponse",
    "ErrorResponse",
]
