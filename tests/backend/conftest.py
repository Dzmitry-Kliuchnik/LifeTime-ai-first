"""
Test configuration and fixtures.
"""

import os
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from app.core.config import Settings
from app.main import create_app


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
def app(test_settings):
    """Create FastAPI app instance for testing."""
    with patch("app.core.config.settings", test_settings):
        return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["TESTING"] = "true"
    yield
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
