"""
API endpoints for week calculation functionality.
"""

from datetime import date

from fastapi import APIRouter, Query, status
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

# Constants for error messages
FUTURE_DATE_ERROR = "Date of birth cannot be in the future"
MIN_YEAR_ERROR = "Date of birth must be after year 1900"


def handle_week_calculation_error(error: Exception) -> JSONResponse:
    """Handle week calculation service errors and return appropriate HTTP responses."""
    if isinstance(error, FutureDateError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "FutureDateError",
                "message": str(error),
                "details": FUTURE_DATE_ERROR,
            },
        )
    elif isinstance(error, InvalidDateError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "InvalidDateError",
                "message": str(error),
                "details": MIN_YEAR_ERROR,
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


@week_router.get(
    "/life-progress",
    response_model=LifeProgressResponse,
    summary="Calculate complete life progress (GET)",
    description="Calculate comprehensive life progress information using query parameters. "
    "This endpoint provides the same functionality as POST /life-progress but uses query parameters for easier integration.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    tags=["week-calculation"],
    openapi_extra={
        "examples": {
            "basic": {
                "summary": "Basic life progress",
                "description": "Calculate life progress for someone born in 1990 with 80-year lifespan",
                "value": {
                    "date_of_birth": "1990-01-15",
                    "lifespan_years": 80,
                    "timezone": "UTC",
                },
            },
            "with_timezone": {
                "summary": "With timezone",
                "description": "Calculate life progress with specific timezone",
                "value": {
                    "date_of_birth": "1985-06-20",
                    "lifespan_years": 90,
                    "timezone": "America/New_York",
                },
            },
        }
    },
)
async def get_life_progress(
    date_of_birth: date = Query(
        ..., description="Date of birth in YYYY-MM-DD format", example="1990-01-15"
    ),
    lifespan_years: int = Query(
        80, ge=1, le=150, description="Expected lifespan in years", example=80
    ),
    timezone: str = Query(
        "UTC",
        description="Timezone for current time calculation (e.g., 'America/New_York', 'Europe/London')",
        example="UTC",
    ),
) -> LifeProgressResponse:
    """
    Calculate comprehensive life progress information using query parameters.

    This endpoint calculates complete life progress including current week, progress percentage,
    and detailed statistics. It combines functionality from current week and total weeks
    calculations to provide a comprehensive view of life progress.

    Parameters:
    - **date_of_birth**: Date of birth (YYYY-MM-DD format)
    - **lifespan_years**: Expected lifespan in years (1-150)
    - **timezone**: Timezone identifier (e.g., 'UTC', 'America/New_York', 'Europe/London')

    Returns comprehensive life progress information including:
    - Current week index and total weeks lived
    - Total expected weeks in lifespan
    - Progress percentage and time remaining
    - Detailed statistics and milestones
    """
    try:
        # Validate date of birth
        if date_of_birth > date.today():
            raise ValueError(FUTURE_DATE_ERROR)
        if date_of_birth.year < 1900:
            raise ValueError(MIN_YEAR_ERROR)

        progress = WeekCalculationService.calculate_life_progress(
            date_of_birth, lifespan_years, timezone
        )

        return LifeProgressResponse(**progress)
    except Exception as e:
        return handle_week_calculation_error(e)


# GET endpoints with query parameters


@week_router.get(
    "/total",
    response_model=TotalWeeksResponse,
    summary="Calculate total weeks in lifespan (GET)",
    description="Calculate the total number of weeks in a person's expected lifespan using query parameters. "
    "This endpoint provides the same functionality as POST /total-weeks but uses query parameters for easier integration.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    tags=["week-calculation"],
    openapi_extra={
        "examples": {
            "basic": {
                "summary": "Basic calculation",
                "description": "Calculate total weeks for someone born in 1990 with 80-year lifespan",
                "value": {"date_of_birth": "1990-01-15", "lifespan_years": 80},
            },
            "different_lifespan": {
                "summary": "Different lifespan",
                "description": "Calculate with a different expected lifespan",
                "value": {"date_of_birth": "1985-06-20", "lifespan_years": 90},
            },
        }
    },
)
async def get_total_weeks(
    date_of_birth: date = Query(
        ..., description="Date of birth in YYYY-MM-DD format", example="1990-01-15"
    ),
    lifespan_years: int = Query(
        80, ge=1, le=150, description="Expected lifespan in years", example=80
    ),
) -> TotalWeeksResponse:
    """
    Calculate total weeks in expected lifespan using query parameters.

    This endpoint calculates the total number of weeks a person is expected to live
    based on their date of birth and expected lifespan in years. It properly handles
    leap years using dateutil's relativedelta for accurate calculations.

    Parameters:
    - **date_of_birth**: Date of birth (YYYY-MM-DD format)
    - **lifespan_years**: Expected lifespan in years (1-150)

    Returns comprehensive information including:
    - Original date of birth
    - Expected lifespan years
    - Total weeks calculated
    """
    try:
        # Validate date of birth
        if date_of_birth > date.today():
            raise ValueError(FUTURE_DATE_ERROR)
        if date_of_birth.year < 1900:
            raise ValueError(MIN_YEAR_ERROR)

        total_weeks = WeekCalculationService.calculate_total_weeks(
            date_of_birth, lifespan_years
        )

        return TotalWeeksResponse(
            date_of_birth=date_of_birth.isoformat(),
            lifespan_years=lifespan_years,
            total_weeks=total_weeks,
        )
    except Exception as e:
        return handle_week_calculation_error(e)


@week_router.get(
    "/current",
    response_model=CurrentWeekResponse,
    summary="Calculate current week index (GET)",
    description="Calculate the current week index since birth using query parameters with timezone support. "
    "This endpoint provides the same functionality as POST /current-week but uses query parameters for easier integration.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    tags=["week-calculation"],
    openapi_extra={
        "examples": {
            "utc": {
                "summary": "UTC timezone",
                "description": "Calculate current week using UTC timezone",
                "value": {"date_of_birth": "1990-01-15", "timezone": "UTC"},
            },
            "new_york": {
                "summary": "New York timezone",
                "description": "Calculate current week using America/New_York timezone",
                "value": {
                    "date_of_birth": "1990-01-15",
                    "timezone": "America/New_York",
                },
            },
            "europe": {
                "summary": "European timezone",
                "description": "Calculate current week using Europe/London timezone",
                "value": {"date_of_birth": "1985-06-20", "timezone": "Europe/London"},
            },
        }
    },
)
async def get_current_week(
    date_of_birth: date = Query(
        ..., description="Date of birth in YYYY-MM-DD format", example="1990-01-15"
    ),
    timezone: str = Query(
        "UTC",
        description="Timezone for current time calculation (e.g., 'America/New_York', 'Europe/London')",
        example="UTC",
    ),
) -> CurrentWeekResponse:
    """
    Calculate current week index since birth with timezone support.

    This endpoint calculates which week of life a person is currently in,
    starting from week 0 (birth week). It supports timezone-aware calculations
    to provide accurate results regardless of the user's location.

    Parameters:
    - **date_of_birth**: Date of birth (YYYY-MM-DD format)
    - **timezone**: Timezone identifier (e.g., 'UTC', 'America/New_York', 'Europe/London')

    Returns comprehensive information including:
    - Original date of birth
    - Timezone used for calculation
    - Current week index (0-based)
    - Total weeks lived (1-based)
    """
    try:
        # Validate date of birth
        if date_of_birth > date.today():
            raise ValueError(FUTURE_DATE_ERROR)
        if date_of_birth.year < 1900:
            raise ValueError(MIN_YEAR_ERROR)

        current_week_index = WeekCalculationService.calculate_current_week_index(
            date_of_birth, timezone
        )

        return CurrentWeekResponse(
            date_of_birth=date_of_birth.isoformat(),
            timezone=timezone,
            current_week_index=current_week_index,
            weeks_lived=current_week_index + 1,  # +1 because index is 0-based
        )
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
