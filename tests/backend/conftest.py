"""
Test configuration and fixtures.
"""

import os
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from app.core.config import Settings
from app.core.database import get_db
from app.main import create_app
from app.models.base import Base


@pytest.fixture
def test_settings():
    """Create test settings with overrides."""
    return Settings(
        app_name="LifeTime AI Test",
        debug=True,
        database_url="sqlite:///./test.db",
        secret_key="test-secret-key",
        cors_origins=["http://localhost:3000"],
        log_level="DEBUG",
    )


@pytest.fixture
def test_engine(test_settings):
    """Create test database engine."""
    from sqlalchemy.pool import StaticPool

    return create_engine(
        test_settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def test_session(test_engine):
    """Create test database session."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)

    testing_session_local = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = testing_session_local()

    yield session

    session.close()
    # Clean up tables after test
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def app(test_settings, test_session):
    """Create FastAPI app instance for testing."""
    with patch("app.core.config.settings", test_settings):
        app = create_app()

        # Override the get_db dependency to use our test session
        def override_get_db():
            try:
                yield test_session
            finally:
                pass  # Don't close the session here as it's managed by the fixture

        app.dependency_overrides[get_db] = override_get_db
        return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_user(test_session):
    """Create a test user."""
    from datetime import date

    from app.models.user import User

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password_here",
        date_of_birth=date(1990, 1, 1),
        full_name="Test User",
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["TESTING"] = "true"
    yield
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
