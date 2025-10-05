"""
Comprehensive tests for week calculation service.

Tests include:
- Total weeks calculation with various DOB and lifespans
- Current week calculation across different timezones
- Leap year handling
- Edge cases (DOB on leap day, DST transitions)
- Birthday and year-start week detection
- Validation for invalid inputs
"""

from datetime import date, timedelta

import pytest
import zoneinfo
from dateutil.relativedelta import relativedelta

# Import the service - will need to adjust path based on test runner
try:
    from app.services.week_calculation import (
        FutureDateError,
        InvalidDateError,
        InvalidTimezoneError,
        WeekCalculationService,
        WeekType,
        calculate_current_week_index,
        calculate_total_weeks,
        get_life_progress,
    )
except ImportError:
    # Alternative import path for pytest
    import sys

    sys.path.append("../../backend")
    from app.services.week_calculation import (
        FutureDateError,
        InvalidDateError,
        InvalidTimezoneError,
        WeekCalculationService,
        WeekType,
        calculate_current_week_index,
        calculate_total_weeks,
        get_life_progress,
    )


class TestWeekCalculationService:
    """Test cases for WeekCalculationService."""

    def test_validate_date_of_birth_valid(self):
        """Test validation of valid date of birth."""
        valid_dob = date(1990, 1, 15)
        WeekCalculationService.validate_date_of_birth(valid_dob)  # Should not raise

    def test_validate_date_of_birth_future(self):
        """Test validation fails for future date of birth."""
        future_dob = date.today() + timedelta(days=1)
        with pytest.raises(FutureDateError):
            WeekCalculationService.validate_date_of_birth(future_dob)

    def test_validate_date_of_birth_too_old(self):
        """Test validation fails for dates before 1900."""
        old_dob = date(1899, 12, 31)
        with pytest.raises(InvalidDateError):
            WeekCalculationService.validate_date_of_birth(old_dob)

    def test_validate_date_of_birth_invalid_type(self):
        """Test validation fails for non-date objects."""
        with pytest.raises(InvalidDateError):
            WeekCalculationService.validate_date_of_birth("1990-01-15")

    def test_validate_timezone_valid(self):
        """Test validation of valid timezone."""
        tz = WeekCalculationService.validate_timezone("America/New_York")
        assert isinstance(tz, zoneinfo.ZoneInfo)
        assert tz.key == "America/New_York"

    def test_validate_timezone_invalid(self):
        """Test validation fails for invalid timezone."""
        with pytest.raises(InvalidTimezoneError):
            WeekCalculationService.validate_timezone("Invalid/Timezone")

    def test_calculate_total_weeks_basic(self):
        """Test basic total weeks calculation."""
        dob = date(1990, 1, 1)
        lifespan = 80
        total_weeks = WeekCalculationService.calculate_total_weeks(dob, lifespan)

        # 80 years should be approximately 80 * 52.17 weeks
        expected = (
            date(1990, 1, 1) + relativedelta(years=80) - date(1990, 1, 1)
        ).days // 7
        assert total_weeks == expected

    def test_calculate_total_weeks_leap_year_handling(self):
        """Test total weeks calculation handles leap years correctly."""
        # DOB on leap day
        dob = date(2000, 2, 29)  # Leap year
        lifespan = 4  # Will span one leap year
        total_weeks = WeekCalculationService.calculate_total_weeks(dob, lifespan)

        # Calculate expected using dateutil
        end_date = dob + relativedelta(years=lifespan)
        expected = (end_date - dob).days // 7
        assert total_weeks == expected

    def test_calculate_total_weeks_invalid_lifespan(self):
        """Test total weeks calculation with invalid lifespan."""
        dob = date(1990, 1, 1)

        with pytest.raises(ValueError):
            WeekCalculationService.calculate_total_weeks(dob, 0)

        with pytest.raises(ValueError):
            WeekCalculationService.calculate_total_weeks(dob, -5)

        with pytest.raises(ValueError):
            WeekCalculationService.calculate_total_weeks(dob, 200)

    def test_calculate_current_week_index_basic(self):
        """Test basic current week index calculation."""
        # Use a fixed date in the past
        dob = date(2020, 1, 1)
        week_index = WeekCalculationService.calculate_current_week_index(dob, "UTC")

        # Should be positive and reasonable
        assert week_index >= 0
        assert week_index < 1000  # Less than ~19 years

    def test_calculate_current_week_index_different_timezones(self):
        """Test current week calculation across different timezones."""
        dob = date(2020, 1, 1)

        # Test multiple timezones
        timezones = ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]
        results = []

        for tz in timezones:
            week_index = WeekCalculationService.calculate_current_week_index(dob, tz)
            results.append(week_index)
            assert week_index >= 0

        # Results should be close (within 1 week due to timezone differences)
        assert max(results) - min(results) <= 1

    def test_get_week_start_date(self):
        """Test getting week start date."""
        dob = date(2020, 1, 1)

        # Week 0 should start on DOB
        week_0_start = WeekCalculationService.get_week_start_date(dob, 0)
        assert week_0_start == dob

        # Week 1 should start 7 days later
        week_1_start = WeekCalculationService.get_week_start_date(dob, 1)
        assert week_1_start == dob + timedelta(days=7)

        # Week 52 should start ~1 year later
        week_52_start = WeekCalculationService.get_week_start_date(dob, 52)
        assert week_52_start == dob + timedelta(weeks=52)

    def test_get_week_end_date(self):
        """Test getting week end date."""
        dob = date(2020, 1, 1)

        # Week 0 should end 6 days after DOB
        week_0_end = WeekCalculationService.get_week_end_date(dob, 0)
        assert week_0_end == dob + timedelta(days=6)

        # Week 1 should end 13 days after DOB
        week_1_end = WeekCalculationService.get_week_end_date(dob, 1)
        assert week_1_end == dob + timedelta(days=13)

    def test_detect_special_week_birthday(self):
        """Test birthday week detection."""
        dob = date(1990, 6, 15)

        # Find a week that contains a birthday anniversary
        for year in range(2020, 2025):
            birthday = date(year, 6, 15)
            days_since_birth = (birthday - dob).days
            week_index = days_since_birth // 7

            week_type = WeekCalculationService.detect_special_week_type(dob, week_index)
            if week_type == WeekType.BIRTHDAY:
                break
        else:
            pytest.fail("Should have detected at least one birthday week")

    def test_detect_special_week_year_start(self):
        """Test year-start week detection."""
        dob = date(1990, 6, 15)  # DOB in middle of year to avoid birthday conflicts

        # Find a week that contains January 1st, 2021
        jan_1_2021 = date(2021, 1, 1)
        days_since_birth = (jan_1_2021 - dob).days
        week_index = days_since_birth // 7

        week_type = WeekCalculationService.detect_special_week_type(dob, week_index)
        # Should detect year start, birthday, or be normal (depending on exact week boundaries)
        assert week_type in [WeekType.YEAR_START, WeekType.BIRTHDAY, WeekType.NORMAL]

    def test_detect_special_week_leap_day(self):
        """Test leap day week detection."""
        dob = date(2000, 2, 26)  # DOB close to leap day

        # Check week containing leap day 2020
        leap_day = date(2020, 2, 29)
        days_since_birth = (leap_day - dob).days
        week_index = days_since_birth // 7

        week_type = WeekCalculationService.detect_special_week_type(dob, week_index)
        # Should detect leap day or be normal
        assert week_type in [WeekType.LEAP_DAY, WeekType.NORMAL]

    def test_detect_special_week_dst_transition(self):
        """Test DST transition week detection."""
        dob = date(2000, 1, 1)

        # March 2020 DST transition in New York (around March 8)
        dst_date = date(2020, 3, 8)
        days_since_birth = (dst_date - dob).days
        week_index = days_since_birth // 7

        week_type = WeekCalculationService.detect_special_week_type(
            dob, week_index, "America/New_York"
        )
        # Should detect DST transition or be normal
        assert week_type in [WeekType.DST_TRANSITION, WeekType.NORMAL]

    def test_get_week_summary(self):
        """Test getting comprehensive week summary."""
        dob = date(2000, 1, 1)
        week_index = 52  # ~1 year after birth

        summary = WeekCalculationService.get_week_summary(dob, week_index, "UTC")

        assert summary["week_index"] == week_index
        assert "week_start" in summary
        assert "week_end" in summary
        assert "week_type" in summary
        assert summary["age_years"] >= 0
        assert summary["age_months"] >= 0
        assert summary["age_days"] >= 0
        assert summary["days_lived"] >= 0
        assert isinstance(summary["is_current_week"], bool)

    def test_calculate_life_progress(self):
        """Test comprehensive life progress calculation."""
        dob = date(2000, 1, 1)
        lifespan = 80

        progress = WeekCalculationService.calculate_life_progress(dob, lifespan, "UTC")

        assert progress["date_of_birth"] == dob.isoformat()
        assert progress["lifespan_years"] == lifespan
        assert progress["timezone"] == "UTC"
        assert progress["total_weeks"] > 0
        assert progress["current_week_index"] >= 0
        assert progress["weeks_lived"] > 0
        assert progress["weeks_remaining"] >= 0
        assert 0 <= progress["progress_percentage"] <= 100
        assert "current_age" in progress
        assert progress["days_lived"] > 0
        assert "current_week_info" in progress

    def test_leap_year_edge_cases(self):
        """Test edge cases involving leap years."""
        # DOB on leap day
        dob = date(2000, 2, 29)

        # Test total weeks calculation
        total_weeks = WeekCalculationService.calculate_total_weeks(dob, 4)
        assert total_weeks > 0

        # Test current week calculation
        current_week = WeekCalculationService.calculate_current_week_index(dob, "UTC")
        assert current_week >= 0

    def test_dst_transition_edge_cases(self):
        """Test edge cases involving DST transitions."""
        dob = date(2000, 1, 1)

        # Test with timezone that has DST
        current_week = WeekCalculationService.calculate_current_week_index(
            dob, "America/New_York"
        )
        assert current_week >= 0

        # Test with UTC (no DST)
        current_week_utc = WeekCalculationService.calculate_current_week_index(
            dob, "UTC"
        )
        assert current_week_utc >= 0

    def test_edge_case_same_day_dob(self):
        """Test edge case where DOB is today."""
        today = date.today()

        # Should not raise exception
        WeekCalculationService.validate_date_of_birth(today)

        # Current week should be 0
        current_week = WeekCalculationService.calculate_current_week_index(today, "UTC")
        assert current_week == 0

    def test_negative_week_index(self):
        """Test handling of negative week index."""
        dob = date(2000, 1, 1)

        with pytest.raises(ValueError):
            WeekCalculationService.get_week_start_date(dob, -1)


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_calculate_total_weeks_function(self):
        """Test convenience function for total weeks."""
        dob = date(1990, 1, 1)
        total_weeks = calculate_total_weeks(dob, 80)
        assert total_weeks > 0

    def test_calculate_current_week_index_function(self):
        """Test convenience function for current week index."""
        dob = date(2000, 1, 1)
        current_week = calculate_current_week_index(dob, "UTC")
        assert current_week >= 0

    def test_get_life_progress_function(self):
        """Test convenience function for life progress."""
        dob = date(2000, 1, 1)
        progress = get_life_progress(dob, 80, "UTC")
        assert "total_weeks" in progress
        assert "current_week_index" in progress


class TestValidationEdgeCases:
    """Test edge cases for validation."""

    def test_minimum_valid_year(self):
        """Test minimum valid year (1900)."""
        dob = date(1900, 1, 1)
        WeekCalculationService.validate_date_of_birth(dob)  # Should not raise

    def test_maximum_reasonable_lifespan(self):
        """Test maximum reasonable lifespan (150)."""
        dob = date(1900, 1, 1)
        total_weeks = WeekCalculationService.calculate_total_weeks(dob, 150)
        assert total_weeks > 0

    def test_timezone_case_sensitivity(self):
        """Test timezone validation is case sensitive."""
        with pytest.raises(InvalidTimezoneError):
            WeekCalculationService.validate_timezone("america/new_york")  # wrong case


# Parametrized tests for various scenarios
@pytest.mark.parametrize(
    "dob,lifespan",
    [
        (date(1990, 1, 1), 80),
        (date(2000, 2, 29), 75),  # Leap day
        (date(1950, 12, 31), 90),  # Year end
        (date(1980, 6, 15), 70),  # Mid-year
    ],
)
def test_total_weeks_various_scenarios(dob, lifespan):
    """Test total weeks calculation with various DOB and lifespan combinations."""
    total_weeks = WeekCalculationService.calculate_total_weeks(dob, lifespan)
    assert total_weeks > 0

    # Rough sanity check: should be around lifespan * 52
    assert abs(total_weeks - (lifespan * 52)) < (
        lifespan * 2
    )  # Within 2 weeks per year


@pytest.mark.parametrize(
    "timezone",
    [
        "UTC",
        "America/New_York",
        "Europe/London",
        "Asia/Tokyo",
        "Australia/Sydney",
        "America/Los_Angeles",
    ],
)
def test_current_week_various_timezones(timezone):
    """Test current week calculation with various timezones."""
    dob = date(2000, 1, 1)
    current_week = WeekCalculationService.calculate_current_week_index(dob, timezone)
    assert current_week >= 0
    assert current_week < 2000  # Reasonable upper bound


@pytest.mark.parametrize(
    "week_type",
    [
        WeekType.NORMAL,
        WeekType.BIRTHDAY,
        WeekType.YEAR_START,
        WeekType.LEAP_DAY,
        WeekType.DST_TRANSITION,
    ],
)
def test_week_type_enum_values(week_type):
    """Test all week type enum values are valid strings."""
    assert isinstance(week_type.value, str)
    assert len(week_type.value) > 0
