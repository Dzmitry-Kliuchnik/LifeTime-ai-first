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


class TestWeekCalculationAPIEndpoints:
    """Test cases for week calculation API endpoints."""

    def test_get_total_weeks_valid_request(self, client):
        """Test GET /weeks/total endpoint with valid parameters."""
        response = client.get(
            "/api/v1/weeks/total?date_of_birth=1990-01-15&lifespan_years=80"
        )

        assert response.status_code == 200
        data = response.json()

        assert "date_of_birth" in data
        assert "lifespan_years" in data
        assert "total_weeks" in data
        assert data["date_of_birth"] == "1990-01-15"
        assert data["lifespan_years"] == 80
        assert data["total_weeks"] > 0
        assert isinstance(data["total_weeks"], int)

    def test_get_total_weeks_default_lifespan(self, client):
        """Test GET /weeks/total endpoint with default lifespan parameter."""
        response = client.get("/api/v1/weeks/total?date_of_birth=1990-01-15")

        assert response.status_code == 200
        data = response.json()

        assert data["lifespan_years"] == 80  # Default value
        assert data["total_weeks"] > 0

    def test_get_total_weeks_invalid_date_format(self, client):
        """Test GET /weeks/total endpoint with invalid date format."""
        response = client.get(
            "/api/v1/weeks/total?date_of_birth=invalid-date&lifespan_years=80"
        )

        assert response.status_code == 422  # Validation error

    def test_get_total_weeks_future_date(self, client):
        """Test GET /weeks/total endpoint with future date of birth."""
        from datetime import date, timedelta

        future_date = (date.today() + timedelta(days=365)).isoformat()

        response = client.get(
            f"/api/v1/weeks/total?date_of_birth={future_date}&lifespan_years=80"
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Date of birth cannot be in the future" in data["message"]

    def test_get_total_weeks_invalid_lifespan(self, client):
        """Test GET /weeks/total endpoint with invalid lifespan values."""
        # Test zero lifespan
        response = client.get(
            "/api/v1/weeks/total?date_of_birth=1990-01-15&lifespan_years=0"
        )
        assert response.status_code == 422

        # Test negative lifespan
        response = client.get(
            "/api/v1/weeks/total?date_of_birth=1990-01-15&lifespan_years=-5"
        )
        assert response.status_code == 422

        # Test excessive lifespan
        response = client.get(
            "/api/v1/weeks/total?date_of_birth=1990-01-15&lifespan_years=200"
        )
        assert response.status_code == 422

    def test_get_total_weeks_old_date(self, client):
        """Test GET /weeks/total endpoint with very old date of birth."""
        response = client.get(
            "/api/v1/weeks/total?date_of_birth=1899-01-15&lifespan_years=80"
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Date of birth must be after year 1900" in data["message"]

    def test_get_current_week_valid_request(self, client):
        """Test GET /weeks/current endpoint with valid parameters."""
        response = client.get(
            "/api/v1/weeks/current?date_of_birth=1990-01-15&timezone=UTC"
        )

        assert response.status_code == 200
        data = response.json()

        assert "date_of_birth" in data
        assert "timezone" in data
        assert "current_week_index" in data
        assert "weeks_lived" in data
        assert data["date_of_birth"] == "1990-01-15"
        assert data["timezone"] == "UTC"
        assert data["current_week_index"] >= 0
        assert data["weeks_lived"] > 0
        assert isinstance(data["current_week_index"], int)
        assert isinstance(data["weeks_lived"], int)
        # weeks_lived should be current_week_index + 1
        assert data["weeks_lived"] == data["current_week_index"] + 1

    def test_get_current_week_default_timezone(self, client):
        """Test GET /weeks/current endpoint with default timezone."""
        response = client.get("/api/v1/weeks/current?date_of_birth=1990-01-15")

        assert response.status_code == 200
        data = response.json()

        assert data["timezone"] == "UTC"  # Default value

    def test_get_current_week_different_timezones(self, client):
        """Test GET /weeks/current endpoint with different timezones."""
        dob = "1990-01-15"
        timezones = ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]
        results = []

        for timezone in timezones:
            response = client.get(
                f"/api/v1/weeks/current?date_of_birth={dob}&timezone={timezone}"
            )
            assert response.status_code == 200

            data = response.json()
            assert data["timezone"] == timezone
            assert data["current_week_index"] >= 0
            results.append(data["current_week_index"])

        # Results should be close (within 1 week due to timezone differences)
        assert max(results) - min(results) <= 1

    def test_get_current_week_invalid_timezone(self, client):
        """Test GET /weeks/current endpoint with invalid timezone."""
        response = client.get(
            "/api/v1/weeks/current?date_of_birth=1990-01-15&timezone=Invalid/Timezone"
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "InvalidTimezoneError" in data["error"]

    def test_get_current_week_future_date(self, client):
        """Test GET /weeks/current endpoint with future date of birth."""
        from datetime import date, timedelta

        future_date = (date.today() + timedelta(days=365)).isoformat()

        response = client.get(
            f"/api/v1/weeks/current?date_of_birth={future_date}&timezone=UTC"
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Date of birth cannot be in the future" in data["message"]

    def test_get_current_week_old_date(self, client):
        """Test GET /weeks/current endpoint with very old date of birth."""
        response = client.get(
            "/api/v1/weeks/current?date_of_birth=1899-01-15&timezone=UTC"
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Date of birth must be after year 1900" in data["message"]

    def test_get_current_week_today_birth(self, client):
        """Test GET /weeks/current endpoint with today as date of birth."""
        from datetime import date

        today = date.today().isoformat()

        response = client.get(
            f"/api/v1/weeks/current?date_of_birth={today}&timezone=UTC"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["current_week_index"] == 0
        assert data["weeks_lived"] == 1

    def test_endpoints_consistency(self, client):
        """Test that both GET endpoints return consistent data."""
        dob = "1990-01-15"
        lifespan = 80

        # Get total weeks
        total_response = client.get(
            f"/api/v1/weeks/total?date_of_birth={dob}&lifespan_years={lifespan}"
        )
        assert total_response.status_code == 200
        total_data = total_response.json()

        # Get current week
        current_response = client.get(
            f"/api/v1/weeks/current?date_of_birth={dob}&timezone=UTC"
        )
        assert current_response.status_code == 200
        current_data = current_response.json()

        # Both should have same date of birth
        assert total_data["date_of_birth"] == current_data["date_of_birth"]

        # Current week should be less than total weeks
        assert current_data["current_week_index"] < total_data["total_weeks"]

    def test_missing_required_parameters(self, client):
        """Test endpoints with missing required parameters."""
        # Test total weeks without date_of_birth
        response = client.get("/api/v1/weeks/total?lifespan_years=80")
        assert response.status_code == 422

        # Test current week without date_of_birth
        response = client.get("/api/v1/weeks/current?timezone=UTC")
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "dob,lifespan",
        [
            ("1950-01-01", 90),
            ("1980-06-15", 75),
            ("2000-02-29", 80),  # Leap day
            ("1970-12-31", 85),  # Year end
        ],
    )
    def test_get_total_weeks_various_scenarios(self, client, dob, lifespan):
        """Test GET /weeks/total endpoint with various scenarios."""
        response = client.get(
            f"/api/v1/weeks/total?date_of_birth={dob}&lifespan_years={lifespan}"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["date_of_birth"] == dob
        assert data["lifespan_years"] == lifespan
        assert data["total_weeks"] > 0
        # Rough sanity check
        assert abs(data["total_weeks"] - (lifespan * 52)) < (lifespan * 2)

    @pytest.mark.parametrize(
        "dob,timezone",
        [
            ("1990-01-15", "UTC"),
            ("1985-06-20", "America/New_York"),
            ("2000-02-29", "Europe/London"),
            ("1975-12-25", "Asia/Tokyo"),
        ],
    )
    def test_get_current_week_various_scenarios(self, client, dob, timezone):
        """Test GET /weeks/current endpoint with various scenarios."""
        response = client.get(
            f"/api/v1/weeks/current?date_of_birth={dob}&timezone={timezone}"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["date_of_birth"] == dob
        assert data["timezone"] == timezone
        assert data["current_week_index"] >= 0
        assert data["weeks_lived"] > 0
        # Reasonable upper bound check
        assert data["current_week_index"] < 3000


class TestWeekCalculationAPIDocumentation:
    """Test OpenAPI documentation for week calculation endpoints."""

    def test_openapi_schema_generation(self, client):
        """Test that OpenAPI schema is generated correctly."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "paths" in schema

        # Check that our endpoints are in the schema
        paths = schema["paths"]
        assert "/api/v1/weeks/total" in paths
        assert "/api/v1/weeks/current" in paths

        # Check GET method exists for both endpoints
        assert "get" in paths["/api/v1/weeks/total"]
        assert "get" in paths["/api/v1/weeks/current"]

    def test_total_weeks_endpoint_documentation(self, client):
        """Test GET /weeks/total endpoint documentation."""
        response = client.get("/openapi.json")
        schema = response.json()

        total_endpoint = schema["paths"]["/api/v1/weeks/total"]["get"]

        # Check basic documentation fields
        assert "summary" in total_endpoint
        assert "description" in total_endpoint
        assert "parameters" in total_endpoint
        assert "responses" in total_endpoint

        # Check parameters
        params = total_endpoint["parameters"]
        param_names = [p["name"] for p in params]
        assert "date_of_birth" in param_names
        assert "lifespan_years" in param_names

        # Check responses
        responses = total_endpoint["responses"]
        assert "200" in responses
        assert "400" in responses
        assert "422" in responses

    def test_current_week_endpoint_documentation(self, client):
        """Test GET /weeks/current endpoint documentation."""
        response = client.get("/openapi.json")
        schema = response.json()

        current_endpoint = schema["paths"]["/api/v1/weeks/current"]["get"]

        # Check basic documentation fields
        assert "summary" in current_endpoint
        assert "description" in current_endpoint
        assert "parameters" in current_endpoint
        assert "responses" in current_endpoint

        # Check parameters
        params = current_endpoint["parameters"]
        param_names = [p["name"] for p in params]
        assert "date_of_birth" in param_names
        assert "timezone" in param_names

        # Check responses
        responses = current_endpoint["responses"]
        assert "200" in responses
        assert "400" in responses
        assert "422" in responses

    def test_response_models_in_schema(self, client):
        """Test that response models are properly defined in schema."""
        response = client.get("/openapi.json")
        schema = response.json()

        # Check that our response models are in components
        components = schema.get("components", {})
        schemas = components.get("schemas", {})

        assert "TotalWeeksResponse" in schemas
        assert "CurrentWeekResponse" in schemas
        assert "ErrorResponse" in schemas

        # Check TotalWeeksResponse properties
        total_schema = schemas["TotalWeeksResponse"]
        assert "properties" in total_schema
        props = total_schema["properties"]
        assert "date_of_birth" in props
        assert "lifespan_years" in props
        assert "total_weeks" in props

        # Check CurrentWeekResponse properties
        current_schema = schemas["CurrentWeekResponse"]
        assert "properties" in current_schema
        props = current_schema["properties"]
        assert "date_of_birth" in props
        assert "timezone" in props
        assert "current_week_index" in props
        assert "weeks_lived" in props


class TestWeekCalculationAPIErrorHandling:
    """Test comprehensive error handling for week calculation API endpoints."""

    def test_total_weeks_comprehensive_error_handling(self, client):
        """Test comprehensive error handling for GET /weeks/total."""
        # Test with malformed query parameters
        test_cases = [
            ("/api/v1/weeks/total", 422),  # No parameters
            ("/api/v1/weeks/total?date_of_birth=", 422),  # Empty date
            (
                "/api/v1/weeks/total?date_of_birth=not-a-date",
                422,
            ),  # Invalid date format
            (
                "/api/v1/weeks/total?date_of_birth=1990-13-50",
                422,
            ),  # Invalid date values
            (
                "/api/v1/weeks/total?date_of_birth=1990-01-15&lifespan_years=abc",
                422,
            ),  # Non-numeric lifespan
        ]

        for url, expected_status in test_cases:
            response = client.get(url)
            assert response.status_code == expected_status, f"Failed for URL: {url}"

    def test_current_week_comprehensive_error_handling(self, client):
        """Test comprehensive error handling for GET /weeks/current."""
        # Test with malformed query parameters
        test_cases = [
            ("/api/v1/weeks/current", 422),  # No parameters
            ("/api/v1/weeks/current?date_of_birth=", 422),  # Empty date
            (
                "/api/v1/weeks/current?date_of_birth=not-a-date",
                422,
            ),  # Invalid date format
            (
                "/api/v1/weeks/current?date_of_birth=1990-13-50",
                422,
            ),  # Invalid date values
        ]

        for url, expected_status in test_cases:
            response = client.get(url)
            assert response.status_code == expected_status, f"Failed for URL: {url}"

    def test_error_response_format(self, client):
        """Test that error responses follow the correct format."""
        response = client.get(
            "/api/v1/weeks/total?date_of_birth=2050-01-01&lifespan_years=80"
        )

        assert response.status_code == 400
        data = response.json()

        # Check error response structure
        assert "error" in data
        assert "message" in data
        assert "details" in data

        assert isinstance(data["error"], str)
        assert isinstance(data["message"], str)
        assert len(data["error"]) > 0
        assert len(data["message"]) > 0
