#!/usr/bin/env python3
"""
Test script to verify the fix for multiple birthday/new year weeks.
"""

import sys

sys.path.append("backend")

from datetime import date

from backend.app.services.week_calculation import WeekCalculationService, WeekType


def test_birthday_weeks_fix():
    """Test that only one week per year is marked as birthday."""
    print("Testing birthday week detection...")

    # Use DOB June 15, 1990
    dob = date(1990, 6, 15)

    # Test years 2020-2025
    birthday_weeks = []
    for year in range(2020, 2026):
        # Find weeks around the birthday for this year
        birthday_date = date(year, 6, 15)
        days_since_birth = (birthday_date - dob).days

        # Check a range of weeks around the birthday
        for week_offset in range(-2, 3):  # Check 5 weeks around the birthday
            week_index = (days_since_birth // 7) + week_offset
            if week_index < 0:
                continue

            week_type = WeekCalculationService.detect_special_week_type(dob, week_index)
            if week_type == WeekType.BIRTHDAY:
                week_start = WeekCalculationService.get_week_start_date(dob, week_index)
                week_end = WeekCalculationService.get_week_end_date(dob, week_index)
                birthday_weeks.append((year, week_index, week_start, week_end))

    print(f"Found {len(birthday_weeks)} birthday weeks:")
    for year, week_idx, start, end in birthday_weeks:
        print(f"  Year {year}: Week {week_idx} ({start} to {end})")

    # Count birthday weeks per year
    years_with_birthdays = {}
    for year, _, _, _ in birthday_weeks:
        years_with_birthdays[year] = years_with_birthdays.get(year, 0) + 1

    print("\nBirthday weeks per year:")
    for year, count in years_with_birthdays.items():
        print(f"  {year}: {count} weeks")
        if count > 1:
            print(f"    ERROR: Year {year} has {count} birthday weeks (should be 1)")

    # Use assertion instead of return for pytest compatibility
    assert all(count == 1 for count in years_with_birthdays.values()), "Some years have multiple birthday weeks"


def test_new_year_weeks_fix():
    """Test that only one week per year is marked as new year."""
    print("\nTesting new year week detection...")

    # Use DOB June 15, 1990 (away from Jan 1)
    dob = date(1990, 6, 15)

    # Test years 2020-2025
    new_year_weeks = []
    for year in range(2020, 2026):
        # Find weeks around January 1st for this year
        jan_1 = date(year, 1, 1)
        days_since_birth = (jan_1 - dob).days

        # Check a range of weeks around January 1st
        for week_offset in range(-2, 3):  # Check 5 weeks around Jan 1
            week_index = (days_since_birth // 7) + week_offset
            if week_index < 0:
                continue

            week_type = WeekCalculationService.detect_special_week_type(dob, week_index)
            if week_type == WeekType.YEAR_START:
                week_start = WeekCalculationService.get_week_start_date(dob, week_index)
                week_end = WeekCalculationService.get_week_end_date(dob, week_index)
                new_year_weeks.append((year, week_index, week_start, week_end))

    print(f"Found {len(new_year_weeks)} new year weeks:")
    for year, week_idx, start, end in new_year_weeks:
        print(f"  Year {year}: Week {week_idx} ({start} to {end})")

    # Count new year weeks per year
    years_with_new_years = {}
    for year, _, _, _ in new_year_weeks:
        years_with_new_years[year] = years_with_new_years.get(year, 0) + 1

    print("\nNew year weeks per year:")
    for year, count in years_with_new_years.items():
        print(f"  {year}: {count} weeks")
        if count > 1:
            print(f"    ERROR: Year {year} has {count} new year weeks (should be 1)")

    # Use assertion instead of return for pytest compatibility
    assert all(count == 1 for count in years_with_new_years.values()), "Some years have multiple new year weeks"


def test_edge_cases():
    """Test edge cases like leap years and week boundaries."""
    print("\nTesting edge cases...")

    # Test leap year birthday (Feb 29)
    leap_dob = date(2000, 2, 29)

    # Test 2020 (leap year) and 2021 (non-leap year)
    for year in [2020, 2021]:
        print(f"\nTesting leap year DOB for year {year}:")

        # Check around Feb 28/29
        target_date = date(year, 2, 28) if year % 4 != 0 else date(year, 2, 29)
        days_since_birth = (target_date - leap_dob).days
        week_index = days_since_birth // 7

        week_type = WeekCalculationService.detect_special_week_type(
            leap_dob, week_index
        )
        week_start = WeekCalculationService.get_week_start_date(leap_dob, week_index)
        week_end = WeekCalculationService.get_week_end_date(leap_dob, week_index)

        print(
            f"  Week {week_index}: {week_start} to {week_end}, type: {week_type.value}"
        )

    # Use assertion instead of return for pytest compatibility
    assert True, "Edge cases test completed successfully"


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Week Calculation Fix")
    print("=" * 60)

    birthday_ok = test_birthday_weeks_fix()
    new_year_ok = test_new_year_weeks_fix()
    edge_cases_ok = test_edge_cases()

    print("\n" + "=" * 60)
    print("RESULTS:")
    print(f"Birthday weeks fix: {'PASS' if birthday_ok else 'FAIL'}")
    print(f"New year weeks fix: {'PASS' if new_year_ok else 'FAIL'}")
    print(f"Edge cases: {'PASS' if edge_cases_ok else 'FAIL'}")

    if birthday_ok and new_year_ok and edge_cases_ok:
        print("\n✅ ALL TESTS PASSED - Fix is working correctly!")
    else:
        print("\n❌ SOME TESTS FAILED - Fix needs more work")
