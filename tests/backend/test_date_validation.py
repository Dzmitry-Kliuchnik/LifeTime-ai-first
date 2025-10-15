"""
Test for date of birth validation in user schemas.
"""

from datetime import date, timedelta

import pytest

from backend.app.schemas.user import UserByNameCreate, UserCreate, UserUpdate


class TestDateOfBirthValidation:
    """Test date of birth validation across all user schemas."""

    def test_user_by_name_create_rejects_future_date(self):
        """Test that UserByNameCreate rejects future dates."""
        future_date = date.today() + timedelta(days=1)

        with pytest.raises(ValueError) as exc_info:
            UserByNameCreate(full_name="Test User", date_of_birth=future_date)

        error_msg = str(exc_info.value)
        assert "Invalid date of birth:" in error_msg
        assert "is in the future" in error_msg
        assert "Please provide a date on or before today" in error_msg

    def test_user_by_name_create_rejects_very_old_date(self):
        """Test that UserByNameCreate rejects dates more than 150 years ago."""
        very_old_date = date.today() - timedelta(days=365 * 151)

        with pytest.raises(ValueError) as exc_info:
            UserByNameCreate(full_name="Test User", date_of_birth=very_old_date)

        error_msg = str(exc_info.value)
        assert "Invalid date of birth:" in error_msg
        assert "is too old" in error_msg
        assert "Please provide a date after" in error_msg

    def test_user_by_name_create_accepts_valid_date(self):
        """Test that UserByNameCreate accepts valid past dates."""
        valid_date = date.today() - timedelta(days=365 * 25)  # 25 years ago

        user_data = UserByNameCreate(full_name="Test User", date_of_birth=valid_date)

        assert user_data.date_of_birth == valid_date

    def test_user_by_name_create_accepts_none(self):
        """Test that UserByNameCreate accepts None date."""
        user_data = UserByNameCreate(full_name="Test User", date_of_birth=None)

        assert user_data.date_of_birth is None

    def test_user_create_rejects_future_date(self):
        """Test that UserCreate rejects future dates."""
        future_date = date.today() + timedelta(days=1)

        with pytest.raises(ValueError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="ValidPass123",
                date_of_birth=future_date,
            )

        error_msg = str(exc_info.value)
        assert "Invalid date of birth:" in error_msg
        assert "is in the future" in error_msg
        assert "Please provide a date on or before today" in error_msg

    def test_user_update_rejects_future_date(self):
        """Test that UserUpdate rejects future dates."""
        future_date = date.today() + timedelta(days=1)

        with pytest.raises(ValueError) as exc_info:
            UserUpdate(date_of_birth=future_date)

        error_msg = str(exc_info.value)
        assert "Invalid date of birth:" in error_msg
        assert "is in the future" in error_msg
        assert "Please provide a date on or before today" in error_msg

    def test_all_schemas_consistent_validation(self):
        """Test that all schemas apply consistent validation rules."""
        future_date = date.today() + timedelta(days=1)
        very_old_date = date.today() - timedelta(days=365 * 151)
        valid_date = date.today() - timedelta(days=365 * 30)

        # Test future date rejection
        schemas_to_test = [
            (
                "UserByNameCreate",
                lambda: UserByNameCreate(
                    full_name="Test User", date_of_birth=future_date
                ),
            ),
            (
                "UserCreate",
                lambda: UserCreate(
                    username="testuser",
                    email="test@example.com",
                    password="ValidPass123",
                    date_of_birth=future_date,
                ),
            ),
            ("UserUpdate", lambda: UserUpdate(date_of_birth=future_date)),
        ]

        for schema_name, schema_factory in schemas_to_test:
            with pytest.raises(ValueError) as exc_info:
                schema_factory()
            error_msg = str(exc_info.value)
            assert (
                "Invalid date of birth:" in error_msg
            ), f"{schema_name} should show informative error"
            assert (
                "is in the future" in error_msg
            ), f"{schema_name} should reject future dates"
            assert (
                "Please provide a date on or before today" in error_msg
            ), f"{schema_name} should provide guidance"

        # Test very old date rejection
        schemas_to_test_old = [
            (
                "UserByNameCreate",
                lambda: UserByNameCreate(
                    full_name="Test User", date_of_birth=very_old_date
                ),
            ),
            (
                "UserCreate",
                lambda: UserCreate(
                    username="testuser",
                    email="test@example.com",
                    password="ValidPass123",
                    date_of_birth=very_old_date,
                ),
            ),
            ("UserUpdate", lambda: UserUpdate(date_of_birth=very_old_date)),
        ]

        for schema_name, schema_factory in schemas_to_test_old:
            with pytest.raises(ValueError) as exc_info:
                schema_factory()
            error_msg = str(exc_info.value)
            assert (
                "Invalid date of birth:" in error_msg
            ), f"{schema_name} should show informative error"
            assert (
                "is too old" in error_msg
            ), f"{schema_name} should reject very old dates"
            assert (
                "Please provide a date after" in error_msg
            ), f"{schema_name} should provide guidance"

        # Test valid date acceptance
        valid_schemas = [
            UserByNameCreate(full_name="Test User", date_of_birth=valid_date),
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="ValidPass123",
                date_of_birth=valid_date,
            ),
            UserUpdate(date_of_birth=valid_date),
        ]

        for schema in valid_schemas:
            assert schema.date_of_birth == valid_date
