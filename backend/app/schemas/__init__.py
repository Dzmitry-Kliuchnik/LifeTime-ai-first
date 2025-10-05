"""
Pydantic schemas for LifeTime AI application.
"""

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
