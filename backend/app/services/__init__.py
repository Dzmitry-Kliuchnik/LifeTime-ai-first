"""
Services package for LifeTime AI application.

Contains business logic and service layer implementations.
"""

from .user import UserService
from .week_calculation import (
    FutureDateError,
    InvalidDateError,
    InvalidTimezoneError,
    WeekCalculationError,
    WeekCalculationService,
    WeekType,
    calculate_current_week_index,
    calculate_total_weeks,
    get_life_progress,
)

__all__ = [
    # User service
    "UserService",
    # Week calculation services
    "WeekCalculationService",
    "WeekType",
    "WeekCalculationError",
    "InvalidDateError",
    "FutureDateError",
    "InvalidTimezoneError",
    "calculate_total_weeks",
    "calculate_current_week_index",
    "get_life_progress",
]
