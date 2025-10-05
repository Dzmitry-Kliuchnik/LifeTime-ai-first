"""
Tests for FastAPI application initialization and basic functionality.
"""

from unittest.mock import patch

from app.main import create_app
from fastapi import FastAPI


class TestAppInitialization:
    """Test FastAPI application initialization."""

    def test_create_app_returns_fastapi_instance(self, test_settings):
        """Test that create_app returns a FastAPI instance."""
        with patch("app.core.config.settings", test_settings):
            app = create_app()
            assert isinstance(app, FastAPI)

    def test_app_configuration(self, test_settings):
        """Test that app is configured with correct settings."""
        with patch("app.main.settings", test_settings):
            app = create_app()

            assert app.title == test_settings.app_name
            assert app.version == test_settings.app_version
            assert app.debug == test_settings.debug

    def test_app_has_required_endpoints(self, client):
        """Test that app has required endpoints."""
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "healthy"

        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data

    def test_api_v1_endpoints(self, client):
        """Test API v1 endpoints."""
        # Test API root endpoint
        response = client.get("/api/v1/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data

        # Test API health endpoint
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["api_version"] == "v1"


class TestMiddleware:
    """Test middleware configuration."""

    def test_cors_middleware_configured(self, client):
        """Test that CORS middleware is properly configured."""
        # Make a preflight request
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Check CORS headers are present
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_configured_origins(self, client):
        """Test that CORS allows configured origins."""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_trusted_host_middleware(self, app, test_settings):
        """Test that trusted host middleware is configured appropriately."""
        # In debug mode, TrustedHostMiddleware should not be present
        middleware_classes = [
            cls.__class__.__name__ for cls in [m.cls for m in app.user_middleware]
        ]

        if test_settings.debug:
            assert "TrustedHostMiddleware" not in middleware_classes
        else:
            # In production mode, it should be present
            assert "TrustedHostMiddleware" in middleware_classes


class TestExceptionHandling:
    """Test custom exception handling."""

    def test_404_error_handling(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data

    def test_validation_error_handling(self, client):
        """Test validation error handling."""
        # This would test validation errors when we have endpoints that require validation
        # For now, we'll test that the app handles invalid JSON gracefully
        response = client.post(
            "/api/v1/", json=None, headers={"Content-Type": "application/json"}
        )
        # Should return method not allowed (405) since we only have GET endpoints
        assert response.status_code in [405, 422]
