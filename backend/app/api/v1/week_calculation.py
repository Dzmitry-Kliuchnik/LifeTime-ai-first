"""
API endpoints for week calculation functionality.
"""

from datetime import date

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.schemas.week_calculation import (
    CurrentWeekRequest,
    CurrentWeekResponse,
    ErrorResponse,
    LifeProgressResponse,
    TotalWeeksResponse,
    WeekCalculationRequest,
    WeekSummaryRequest,
    WeekSummaryResponse,
)
from app.services.week_calculation import (
    FutureDateError,
    InvalidDateError,
    InvalidTimezoneError,
    WeekCalculationService,
)

# Create router for week calculation endpoints
week_router = APIRouter(prefix="/weeks", tags=["week-calculation"])


def handle_week_calculation_error(error: Exception) -> JSONResponse:
    """Handle week calculation service errors and return appropriate HTTP responses."""
    if isinstance(error, FutureDateError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "FutureDateError",
                "message": str(error),
                "details": "Date of birth cannot be in the future",
            },
        )
    elif isinstance(error, InvalidDateError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "InvalidDateError",
                "message": str(error),
                "details": "Date of birth is invalid or before year 1900",
            },
        )
    elif isinstance(error, InvalidTimezoneError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "InvalidTimezoneError",
                "message": str(error),
                "details": "Invalid timezone provided",
            },
        )
    elif isinstance(error, ValueError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "ValueError",
                "message": str(error),
                "details": "Invalid input value provided",
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "details": str(error),
            },
        )


@week_router.post(
    "/total-weeks",
    response_model=TotalWeeksResponse,
    summary="Calculate total weeks in lifespan",
    description="Calculate the total number of weeks in a person's expected lifespan based on date of birth and expected lifespan years.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def calculate_total_weeks_endpoint(
    request: WeekCalculationRequest,
) -> TotalWeeksResponse:
    """Calculate total weeks in expected lifespan."""
    try:
        total_weeks = WeekCalculationService.calculate_total_weeks(
            request.date_of_birth, request.lifespan_years
        )

        return TotalWeeksResponse(
            date_of_birth=request.date_of_birth.isoformat(),
            lifespan_years=request.lifespan_years,
            total_weeks=total_weeks,
        )
    except Exception as e:
        return handle_week_calculation_error(e)


@week_router.post(
    "/current-week",
    response_model=CurrentWeekResponse,
    summary="Calculate current week index",
    description="Calculate the current week index (0-based) since birth with timezone support.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def calculate_current_week_endpoint(
    request: CurrentWeekRequest,
) -> CurrentWeekResponse:
    """Calculate current week index since birth."""
    try:
        current_week_index = WeekCalculationService.calculate_current_week_index(
            request.date_of_birth, request.timezone
        )

        return CurrentWeekResponse(
            date_of_birth=request.date_of_birth.isoformat(),
            timezone=request.timezone,
            current_week_index=current_week_index,
            weeks_lived=current_week_index + 1,  # +1 because index is 0-based
        )
    except Exception as e:
        return handle_week_calculation_error(e)


@week_router.post(
    "/week-summary",
    response_model=WeekSummaryResponse,
    summary="Get week summary",
    description="Get comprehensive information about a specific week including type, dates, and age information.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_week_summary_endpoint(request: WeekSummaryRequest) -> WeekSummaryResponse:
    """Get comprehensive information about a specific week."""
    try:
        summary = WeekCalculationService.get_week_summary(
            request.date_of_birth, request.week_index, request.timezone
        )

        return WeekSummaryResponse(**summary)
    except Exception as e:
        return handle_week_calculation_error(e)


@week_router.post(
    "/life-progress",
    response_model=LifeProgressResponse,
    summary="Calculate complete life progress",
    description="Calculate comprehensive life progress information including current week, progress percentage, and detailed statistics.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def calculate_life_progress_endpoint(
    request: WeekCalculationRequest,
) -> LifeProgressResponse:
    """Calculate comprehensive life progress information."""
    try:
        progress = WeekCalculationService.calculate_life_progress(
            request.date_of_birth, request.lifespan_years, request.timezone
        )

        return LifeProgressResponse(**progress)
    except Exception as e:
        return handle_week_calculation_error(e)


# Convenience endpoints for quick calculations


@week_router.get(
    "/current-week/{dob}",
    response_model=CurrentWeekResponse,
    summary="Quick current week calculation",
    description="Quick calculation of current week index using URL parameters (UTC timezone).",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid date format"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def quick_current_week(dob: str) -> CurrentWeekResponse:
    """Quick current week calculation using URL parameter."""
    try:
        # Parse date from string
        date_parts = dob.split("-")
        if len(date_parts) != 3:
            raise ValueError("Date must be in YYYY-MM-DD format")

        dob_date = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))

        current_week_index = WeekCalculationService.calculate_current_week_index(
            dob_date, "UTC"
        )

        return CurrentWeekResponse(
            date_of_birth=dob_date.isoformat(),
            timezone="UTC",
            current_week_index=current_week_index,
            weeks_lived=current_week_index + 1,
        )
    except (ValueError, IndexError) as e:
        return handle_week_calculation_error(e)
    except Exception as e:
        return handle_week_calculation_error(e)


@week_router.get(
    "/total-weeks/{dob}/{lifespan}",
    response_model=TotalWeeksResponse,
    summary="Quick total weeks calculation",
    description="Quick calculation of total weeks using URL parameters.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def quick_total_weeks(dob: str, lifespan: int) -> TotalWeeksResponse:
    """Quick total weeks calculation using URL parameters."""
    try:
        # Parse date from string
        date_parts = dob.split("-")
        if len(date_parts) != 3:
            raise ValueError("Date must be in YYYY-MM-DD format")

        dob_date = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))

        total_weeks = WeekCalculationService.calculate_total_weeks(dob_date, lifespan)

        return TotalWeeksResponse(
            date_of_birth=dob_date.isoformat(),
            lifespan_years=lifespan,
            total_weeks=total_weeks,
        )
    except (ValueError, IndexError) as e:
        return handle_week_calculation_error(e)
    except Exception as e:
        return handle_week_calculation_error(e)


# Health check for week calculation service
@week_router.get(
    "/health",
    summary="Week calculation service health check",
    description="Check if the week calculation service is working properly.",
)
async def week_calculation_health():
    """Health check for week calculation service."""
    try:
        # Test basic functionality
        test_dob = date(2000, 1, 1)
        test_weeks = WeekCalculationService.calculate_total_weeks(test_dob, 80)
        test_current = WeekCalculationService.calculate_current_week_index(
            test_dob, "UTC"
        )

        return {
            "service": "week-calculation",
            "status": "healthy",
            "test_total_weeks": test_weeks,
            "test_current_week": test_current,
            "timezone_support": True,
            "leap_year_support": True,
            "dst_support": True,
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "service": "week-calculation",
                "status": "unhealthy",
                "error": str(e),
            },
        )
