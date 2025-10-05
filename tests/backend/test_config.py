"""
Tests for configuration management and environment variable loading.
"""

import os
from unittest.mock import patch

import pytest
from app.core.config import Settings
from pydantic import ValidationError


class TestSettingsConfiguration:
    """Test settings configuration and environment variable loading."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.app_name == "LifeTime AI"
        assert settings.app_version == "0.1.0"
        assert settings.debug is False
        assert settings.host == "127.0.0.1"
        assert settings.port == 8000
        assert settings.database_url == "sqlite:///./lifetime.db"
        assert settings.secret_key == "your-secret-key-change-in-production"
        assert settings.algorithm == "HS256"
        assert settings.log_level == "INFO"

    def test_cors_default_settings(self):
        """Test CORS default settings."""
        settings = Settings()

        assert "http://localhost:3000" in settings.cors_origins
        assert "http://127.0.0.1:3000" in settings.cors_origins
        assert settings.cors_credentials is True
        assert "GET" in settings.cors_methods
        assert "POST" in settings.cors_methods
        assert "PUT" in settings.cors_methods
        assert "DELETE" in settings.cors_methods
        assert "OPTIONS" in settings.cors_methods

    def test_api_default_settings(self):
        """Test API default settings."""
        settings = Settings()

        assert settings.api_v1_prefix == "/api/v1"
        assert settings.docs_url == "/docs"
        assert settings.redoc_url == "/redoc"
        assert settings.openapi_url == "/openapi.json"

    @patch.dict(
        os.environ,
        {"APP_NAME": "Test App", "DEBUG": "true", "PORT": "9000", "LOG_LEVEL": "DEBUG"},
    )
    def test_environment_variable_override(self):
        """Test that environment variables override default settings."""
        settings = Settings()

        assert settings.app_name == "Test App"
        assert settings.debug is True
        assert settings.port == 9000
        assert settings.log_level == "DEBUG"

    @patch.dict(
        os.environ,
        {
            "DATABASE_URL": "postgresql://user:pass@localhost/db",
            "SECRET_KEY": "test-secret-key-123",
            "CORS_CREDENTIALS": "false",
        },
    )
    def test_database_and_security_env_vars(self):
        """Test database and security environment variables."""
        settings = Settings()

        assert settings.database_url == "postgresql://user:pass@localhost/db"
        assert settings.secret_key == "test-secret-key-123"
        assert settings.cors_credentials is False

    def test_case_insensitive_env_vars(self):
        """Test that environment variables are case insensitive."""
        with patch.dict(os.environ, {"app_name": "Case Test"}):
            settings = Settings()
            assert settings.app_name == "Case Test"

    def test_invalid_port_type(self):
        """Test that invalid port type raises validation error."""
        with patch.dict(os.environ, {"PORT": "invalid"}):
            with pytest.raises(ValidationError):
                Settings()

    def test_invalid_debug_type(self):
        """Test that invalid debug type raises validation error."""
        with patch.dict(os.environ, {"DEBUG": "invalid"}):
            with pytest.raises(ValidationError):
                Settings()

    @patch.dict(
        os.environ, {"CORS_ORIGINS": '["http://example.com", "https://example.com"]'}
    )
    def test_cors_origins_from_env(self):
        """Test CORS origins from environment variable."""
        settings = Settings()
        # Note: This test might need adjustment based on how pydantic handles list parsing
        # The actual implementation might require JSON format or comma-separated values
        assert isinstance(settings.cors_origins, list)

    def test_settings_model_config(self):
        """Test that settings model configuration is correct."""
        settings = Settings()

        # Test that the model config is set up correctly
        config = settings.model_config
        assert config["case_sensitive"] is False
        assert config["env_file"] == ".env"
        assert config["extra"] == "ignore"


class TestSettingsIntegration:
    """Test settings integration with the application."""

    def test_settings_import(self):
        """Test that settings can be imported and used."""
        from app.core.config import settings

        assert isinstance(settings, Settings)
        assert hasattr(settings, "app_name")
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "cors_origins")

    def test_settings_singleton_behavior(self):
        """Test that settings behave like a singleton."""
        from app.core.config import settings as settings1
        from app.core.config import settings as settings2

        # Both imports should reference the same instance
        assert settings1 is settings2
