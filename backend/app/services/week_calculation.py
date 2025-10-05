"""
Week calculation service for LifeTime AI application.

Provides core date arithmetic functions for week calculations with proper
timezone handling, leap year support, and DST transition handling.
"""

import calendar
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict

import zoneinfo
from dateutil.relativedelta import relativedelta


class WeekType(Enum):
    """Enumeration of special week types."""

    NORMAL = "normal"
    BIRTHDAY = "birthday"
    YEAR_START = "year_start"
    LEAP_DAY = "leap_day"
    DST_TRANSITION = "dst_transition"


class WeekCalculationError(Exception):
    """Base exception for week calculation errors."""

    pass


class InvalidDateError(WeekCalculationError):
    """Raised when an invalid date is provided."""

    pass


class FutureDateError(WeekCalculationError):
    """Raised when a future date of birth is provided."""

    pass


class InvalidTimezoneError(WeekCalculationError):
    """Raised when an invalid timezone is provided."""

    pass


class WeekCalculationService:
    """Service for performing week calculations with timezone support."""

    @staticmethod
    def validate_date_of_birth(dob: date) -> None:
        """
        Validate that the date of birth is valid and not in the future.

        Args:
            dob: Date of birth to validate

        Raises:
            InvalidDateError: If the date is invalid
            FutureDateError: If the date is in the future
        """
        if not isinstance(dob, date):
            raise InvalidDateError("Date of birth must be a date object")

        today = date.today()
        if dob > today:
            raise FutureDateError("Date of birth cannot be in the future")

        # Check for reasonable date range (not before 1900)
        if dob.year < 1900:
            raise InvalidDateError("Date of birth must be after year 1900")

    @staticmethod
    def validate_timezone(timezone: str) -> zoneinfo.ZoneInfo:
        """
        Validate and return a timezone object.

        Args:
            timezone: Timezone string (e.g., 'America/New_York')

        Returns:
            ZoneInfo object for the timezone

        Raises:
            InvalidTimezoneError: If the timezone is invalid
        """
        try:
            return zoneinfo.ZoneInfo(timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            raise InvalidTimezoneError(f"Invalid timezone: {timezone}")
        except Exception as e:
            raise InvalidTimezoneError(
                f"Error validating timezone {timezone}: {str(e)}"
            )

    @staticmethod
    def get_timezone_aware_datetime(timezone: str) -> datetime:
        """
        Get current datetime in the specified timezone.

        Args:
            timezone: Timezone string

        Returns:
            Current datetime in the specified timezone
        """
        if timezone.upper() == "UTC":
            from datetime import timezone as dt_timezone

            return datetime.now(dt_timezone.utc)
        else:
            tz_info = WeekCalculationService.validate_timezone(timezone)
            return datetime.now(tz_info)

    @staticmethod
    def calculate_total_weeks(dob: date, lifespan_years: int) -> int:
        """
        Calculate the total number of weeks in a person's expected lifespan.

        Uses dateutil.relativedelta to handle leap years properly.

        Args:
            dob: Date of birth
            lifespan_years: Expected lifespan in years

        Returns:
            Total number of weeks in the lifespan

        Raises:
            InvalidDateError: If date of birth is invalid
            FutureDateError: If date of birth is in the future
            ValueError: If lifespan_years is not positive
        """
        WeekCalculationService.validate_date_of_birth(dob)

        if lifespan_years <= 0:
            raise ValueError("Lifespan years must be positive")

        if lifespan_years > 150:
            raise ValueError("Lifespan years must be reasonable (≤ 150)")

        # Calculate end date using relativedelta to handle leap years
        end_date = dob + relativedelta(years=lifespan_years)

        # Calculate total days and convert to weeks
        total_days = (end_date - dob).days
        total_weeks = total_days // 7

        return total_weeks

    @staticmethod
    def calculate_current_week_index(dob: date, timezone: str = "UTC") -> int:
        """
        Calculate the current week index since birth using ISO 8601 week boundaries.

        Args:
            dob: Date of birth
            timezone: Timezone string for current time calculation

        Returns:
            Current week index (0-based) since birth

        Raises:
            InvalidDateError: If date of birth is invalid
            FutureDateError: If date of birth is in the future
            InvalidTimezoneError: If timezone is invalid
        """
        WeekCalculationService.validate_date_of_birth(dob)

        # Get current date in the specified timezone
        now = WeekCalculationService.get_timezone_aware_datetime(timezone)
        current_date = now.date()

        # Calculate days since birth
        days_since_birth = (current_date - dob).days

        # If current date is before DOB (shouldn't happen due to validation)
        if days_since_birth < 0:
            return 0

        # Calculate week index (0-based)
        week_index = days_since_birth // 7

        return week_index

    @staticmethod
    def get_week_start_date(dob: date, week_index: int) -> date:
        """
        Get the start date of a specific week index since birth.

        Args:
            dob: Date of birth
            week_index: Week index (0-based) since birth

        Returns:
            Start date of the specified week
        """
        WeekCalculationService.validate_date_of_birth(dob)

        if week_index < 0:
            raise ValueError("Week index must be non-negative")

        return dob + timedelta(weeks=week_index)

    @staticmethod
    def get_week_end_date(dob: date, week_index: int) -> date:
        """
        Get the end date of a specific week index since birth.

        Args:
            dob: Date of birth
            week_index: Week index (0-based) since birth

        Returns:
            End date of the specified week
        """
        start_date = WeekCalculationService.get_week_start_date(dob, week_index)
        return start_date + timedelta(days=6)

    @staticmethod
    def detect_special_week_type(
        dob: date, week_index: int, timezone: str = "UTC"
    ) -> WeekType:
        """
        Detect if a specific week is a special week type.

        Args:
            dob: Date of birth
            week_index: Week index to check
            timezone: Timezone for DST transition detection

        Returns:
            WeekType enum indicating the type of week
        """
        WeekCalculationService.validate_date_of_birth(dob)

        # For DST detection, we need the timezone info
        if timezone.upper() == "UTC":
            tz_info = None  # UTC has no DST
        else:
            tz_info = WeekCalculationService.validate_timezone(timezone)

        week_start = WeekCalculationService.get_week_start_date(dob, week_index)
        week_end = WeekCalculationService.get_week_end_date(dob, week_index)

        # Check if it's a birthday week
        if WeekCalculationService._is_birthday_week(dob, week_start, week_end):
            return WeekType.BIRTHDAY

        # Check if it's a year-start week
        if WeekCalculationService._is_year_start_week(week_start, week_end):
            return WeekType.YEAR_START

        # Check if it's a leap day week
        if WeekCalculationService._is_leap_day_week(week_start, week_end):
            return WeekType.LEAP_DAY

        # Check if it's a DST transition week
        if WeekCalculationService._is_dst_transition_week(
            week_start, week_end, tz_info
        ):
            return WeekType.DST_TRANSITION

        return WeekType.NORMAL

    @staticmethod
    def _is_birthday_week(dob: date, week_start: date, week_end: date) -> bool:
        """Check if the week contains a birthday anniversary."""
        for _ in range(1, 200):  # Check up to 200 years
            anniversary = date(week_start.year, dob.month, dob.day)
            if anniversary < week_start:
                continue
            if week_start <= anniversary <= week_end:
                return True
            if anniversary > week_end:
                break
        return False

    @staticmethod
    def _is_year_start_week(week_start: date, week_end: date) -> bool:
        """Check if the week contains January 1st."""
        jan_1 = date(week_start.year, 1, 1)
        if week_start <= jan_1 <= week_end:
            return True
        # Check if year boundary is crossed
        if week_start.year != week_end.year:
            return True
        return False

    @staticmethod
    def _is_leap_day_week(week_start: date, week_end: date) -> bool:
        """Check if the week contains February 29th in a leap year."""
        year = week_start.year
        if calendar.isleap(year):
            leap_day = date(year, 2, 29)
            return week_start <= leap_day <= week_end
        # Check if week spans across leap year boundary
        if week_start.year != week_end.year and calendar.isleap(week_end.year):
            leap_day = date(week_end.year, 2, 29)
            return leap_day <= week_end
        return False

    @staticmethod
    def _is_dst_transition_week(
        week_start: date, week_end: date, tz_info: zoneinfo.ZoneInfo
    ) -> bool:
        """Check if the week contains a DST transition."""
        if tz_info is None or (hasattr(tz_info, "key") and tz_info.key == "UTC"):
            return False  # UTC doesn't have DST transitions

        try:
            # Check each day in the week for DST transitions
            current = week_start
            while current <= week_end:
                # Check if this day has different UTC offset than the next day
                dt1 = datetime.combine(current, datetime.min.time()).replace(
                    tzinfo=tz_info
                )
                dt2 = datetime.combine(
                    current + timedelta(days=1), datetime.min.time()
                ).replace(tzinfo=tz_info)

                if dt1.utcoffset() != dt2.utcoffset():
                    return True

                current += timedelta(days=1)
        except Exception:
            # If we can't determine DST status, assume no transition
            pass

        return False

    @staticmethod
    def get_week_summary(
        dob: date, week_index: int, timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Get comprehensive information about a specific week.

        Args:
            dob: Date of birth
            week_index: Week index (0-based) since birth
            timezone: Timezone for calculations

        Returns:
            Dictionary containing week information
        """
        WeekCalculationService.validate_date_of_birth(dob)

        week_start = WeekCalculationService.get_week_start_date(dob, week_index)
        week_end = WeekCalculationService.get_week_end_date(dob, week_index)
        week_type = WeekCalculationService.detect_special_week_type(
            dob, week_index, timezone
        )

        # Calculate age at this week
        age_at_week = relativedelta(week_start, dob)

        return {
            "week_index": week_index,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "week_type": week_type.value,
            "age_years": age_at_week.years,
            "age_months": age_at_week.months,
            "age_days": age_at_week.days,
            "days_lived": (week_start - dob).days,
            "is_current_week": week_index
            == WeekCalculationService.calculate_current_week_index(dob, timezone),
        }

    @staticmethod
    def calculate_life_progress(
        dob: date, lifespan_years: int, timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive life progress information.

        Args:
            dob: Date of birth
            lifespan_years: Expected lifespan in years
            timezone: Timezone for current calculations

        Returns:
            Dictionary containing life progress information
        """
        total_weeks = WeekCalculationService.calculate_total_weeks(dob, lifespan_years)
        current_week = WeekCalculationService.calculate_current_week_index(
            dob, timezone
        )

        # Calculate progress percentage
        progress_percentage = (
            (current_week / total_weeks) * 100 if total_weeks > 0 else 0
        )
        progress_percentage = min(100.0, progress_percentage)  # Cap at 100%

        # Calculate remaining weeks
        remaining_weeks = max(0, total_weeks - current_week)

        # Calculate current age
        now = WeekCalculationService.get_timezone_aware_datetime(timezone)
        current_age = relativedelta(now.date(), dob)

        return {
            "date_of_birth": dob.isoformat(),
            "lifespan_years": lifespan_years,
            "timezone": timezone,
            "total_weeks": total_weeks,
            "current_week_index": current_week,
            "weeks_lived": current_week + 1,  # +1 because index is 0-based
            "weeks_remaining": remaining_weeks,
            "progress_percentage": round(progress_percentage, 2),
            "current_age": {
                "years": current_age.years,
                "months": current_age.months,
                "days": current_age.days,
            },
            "days_lived": (now.date() - dob).days,
            "current_week_info": WeekCalculationService.get_week_summary(
                dob, current_week, timezone
            ),
        }


# Convenience functions for easy import
def calculate_total_weeks(dob: date, lifespan_years: int) -> int:
    """Convenience function for calculating total weeks."""
    return WeekCalculationService.calculate_total_weeks(dob, lifespan_years)


def calculate_current_week_index(dob: date, timezone: str = "UTC") -> int:
    """Convenience function for calculating current week index."""
    return WeekCalculationService.calculate_current_week_index(dob, timezone)


def get_life_progress(
    dob: date, lifespan_years: int, timezone: str = "UTC"
) -> Dict[str, Any]:
    """Convenience function for getting complete life progress."""
    return WeekCalculationService.calculate_life_progress(dob, lifespan_years, timezone)
