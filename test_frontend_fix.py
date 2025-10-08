#!/usr/bin/env python3
"""
Test script to verify that the frontend only highlights one week per year for birthdays and new years.
This test simulates the frontend logic.
"""

import math
from datetime import date, datetime


def frontend_is_birthday_week(week_index: int, date_of_birth: date) -> bool:
    """
    Simulate the frontend isBirthdayWeek function from LifetimeGrid.vue
    """
    birth_date = datetime(date_of_birth.year, date_of_birth.month, date_of_birth.day)
    weeks_per_year = 52.1775

    # Calculate which year this week falls in
    estimated_year = math.floor(week_index / weeks_per_year)

    # Check a range of years around the estimated year
    for year_offset in range(estimated_year - 1, estimated_year + 2):
        if year_offset < 0:
            continue

        birthday_this_year = datetime(
            birth_date.year + year_offset, birth_date.month, birth_date.day
        )

        days_diff = math.floor(
            (birthday_this_year.timestamp() - birth_date.timestamp())
            / (1000 * 60 * 60 * 24 / 1000)
        )
        birthday_week = math.floor(days_diff / 7)

        # Check if this week is exactly the birthday week (FIXED: was <= 1, now ==)
        if birthday_week == week_index:
            return True

    return False


def frontend_is_year_start_week(week_index: int, date_of_birth: date) -> bool:
    """
    Simulate the frontend isYearStartWeek function from LifetimeGrid.vue
    """
    birth_date = datetime(date_of_birth.year, date_of_birth.month, date_of_birth.day)
    birth_year = birth_date.year

    weeks_per_year = 52.1775
    estimated_year = math.floor(week_index / weeks_per_year)

    for year_offset in range(estimated_year - 1, estimated_year + 2):
        target_year = birth_year + year_offset
        new_year_date = datetime(target_year, 1, 1)  # January 1st
        days_diff = math.floor(
            (new_year_date.timestamp() - birth_date.timestamp())
            / (1000 * 60 * 60 * 24 / 1000)
        )
        new_year_week = math.floor(days_diff / 7)

        # Check if this week is exactly the new year week (FIXED: was <= 1, now ==)
        if new_year_week == week_index:
            return True

    return False


def test_frontend_fix():
    """Test that the frontend fix only highlights one week per year"""
    print("Testing Frontend Week Highlighting Fix")
    print("=" * 50)

    # Use DOB June 15, 1990
    dob = date(1990, 6, 15)

    # Test birthday weeks
    print("\nTesting Birthday Weeks:")
    birthday_weeks = []

    # Check weeks 1500-2000 (covers several years)
    for week_index in range(1500, 2000):
        if frontend_is_birthday_week(week_index, dob):
            birthday_weeks.append(week_index)

    print(f"Found {len(birthday_weeks)} birthday weeks:")
    for week in birthday_weeks:
        print(f"  Week {week}")

    # Group by approximate year
    birthday_years = {}
    for week in birthday_weeks:
        approx_year = int(week / 52.1775) + 1990
        if approx_year not in birthday_years:
            birthday_years[approx_year] = []
        birthday_years[approx_year].append(week)

    print("\nBirthday weeks per year:")
    birthday_pass = True
    for year, weeks in birthday_years.items():
        print(f"  {year}: {len(weeks)} weeks")
        if len(weeks) > 1:
            print(f"    ERROR: Multiple birthday weeks detected for {year}: {weeks}")
            birthday_pass = False

    # Test new year weeks
    print("\nTesting New Year Weeks:")
    new_year_weeks = []

    # Check weeks 1500-2000 (covers several years)
    for week_index in range(1500, 2000):
        if frontend_is_year_start_week(week_index, dob):
            new_year_weeks.append(week_index)

    print(f"Found {len(new_year_weeks)} new year weeks:")
    for week in new_year_weeks:
        print(f"  Week {week}")

    # Group by approximate year
    new_year_years = {}
    for week in new_year_weeks:
        approx_year = int(week / 52.1775) + 1990
        if approx_year not in new_year_years:
            new_year_years[approx_year] = []
        new_year_years[approx_year].append(week)

    print("\nNew year weeks per year:")
    new_year_pass = True
    for year, weeks in new_year_years.items():
        print(f"  {year}: {len(weeks)} weeks")
        if len(weeks) > 1:
            print(f"    ERROR: Multiple new year weeks detected for {year}: {weeks}")
            new_year_pass = False

    print("\n" + "=" * 50)
    print("RESULTS:")
    print(f"Birthday weeks test: {'PASS' if birthday_pass else 'FAIL'}")
    print(f"New year weeks test: {'PASS' if new_year_pass else 'FAIL'}")

    if birthday_pass and new_year_pass:
        print("✅ Frontend fix is working correctly!")
        return True
    else:
        print("❌ Frontend fix needs more work")
        return False


if __name__ == "__main__":
    test_frontend_fix()
