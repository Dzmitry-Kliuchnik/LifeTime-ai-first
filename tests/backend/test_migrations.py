"""
Tests for database migrations using Alembic.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from app.core.config import Settings


class TestDatabaseMigrations:
    """Test database migration functionality."""

    @pytest.fixture
    def temp_database(self):
        """Create a temporary database for migration testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        yield db_path

        # Clean up
        if os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except PermissionError:
                # On Windows, sometimes we need to wait a bit
                import time

                time.sleep(0.1)
                try:
                    os.unlink(db_path)
                except PermissionError:
                    pass  # File will be cleaned up by OS eventually

    def test_migration_status_check(self, temp_database):
        """Test checking migration status."""
        test_settings = Settings(
            database_url=f"sqlite:///{temp_database}", database_encrypt=False
        )

        with patch("app.core.database.settings", test_settings):
            # Get backend directory
            backend_dir = Path(__file__).parent.parent.parent / "backend"

            # Test alembic current command
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "current"],
                cwd=backend_dir,
                capture_output=True,
                text=True,
                env={**os.environ, "DATABASE_URL": test_settings.database_url},
            )

            # Should not fail (might be empty if no migrations applied)
            assert result.returncode == 0

    def test_migration_upgrade(self, temp_database):
        """Test applying migrations."""
        test_settings = Settings(
            database_url=f"sqlite:///{temp_database}", database_encrypt=False
        )

        with patch("app.core.database.settings", test_settings):
            # Get backend directory
            backend_dir = Path(__file__).parent.parent.parent / "backend"

            # Apply migrations
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd=backend_dir,
                capture_output=True,
                text=True,
                env={**os.environ, "DATABASE_URL": test_settings.database_url},
            )

            # Migration should succeed
            assert result.returncode == 0

            # Verify tables were created
            from sqlalchemy import create_engine, inspect

            engine = create_engine(test_settings.database_url)
            inspector = inspect(engine)
            tables = inspector.get_table_names()

            assert "users" in tables
            assert "notes" in tables
            assert "alembic_version" in tables

    def test_migration_downgrade(self, temp_database):
        """Test downgrading migrations."""
        test_settings = Settings(
            database_url=f"sqlite:///{temp_database}", database_encrypt=False
        )

        with patch("app.core.database.settings", test_settings):
            # Get backend directory
            backend_dir = Path(__file__).parent.parent.parent / "backend"

            # First apply migrations
            subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd=backend_dir,
                capture_output=True,
                text=True,
                env={**os.environ, "DATABASE_URL": test_settings.database_url},
            )

            # Then downgrade
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "downgrade", "base"],
                cwd=backend_dir,
                capture_output=True,
                text=True,
                env={**os.environ, "DATABASE_URL": test_settings.database_url},
            )

            # Downgrade should succeed
            assert result.returncode == 0

            # Verify tables were removed
            from sqlalchemy import create_engine, inspect

            engine = create_engine(test_settings.database_url)
            inspector = inspect(engine)
            tables = inspector.get_table_names()

            # Only alembic_version should remain
            assert "users" not in tables
            assert "notes" not in tables
            assert "alembic_version" in tables  # Alembic keeps its version table
