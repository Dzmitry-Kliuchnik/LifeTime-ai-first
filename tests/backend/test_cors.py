"""
Tests for CORS configuration and middleware.
"""

from unittest.mock import patch

from app.core.config import Settings
from fastapi.testclient import TestClient


class TestCORSConfiguration:
    """Test CORS middleware configuration and behavior."""

    def test_cors_preflight_request(self, client):
        """Test CORS preflight request handling."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_cors_simple_request(self, client):
        """Test CORS simple request handling."""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_allowed_origin(self, client):
        """Test that allowed origins receive CORS headers."""
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        cors_origin = response.headers.get("access-control-allow-origin")
        assert cors_origin == "http://localhost:3000"

    def test_cors_credentials_allowed(self, client):
        """Test that credentials are allowed in CORS requests."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )

        assert response.status_code == 200
        credentials = response.headers.get("access-control-allow-credentials")
        assert credentials == "true"

    def test_cors_allowed_methods(self, client):
        """Test that configured methods are allowed in CORS."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )

        assert response.status_code == 200
        allowed_methods = response.headers.get("access-control-allow-methods")

        # Check that standard methods are included
        assert "GET" in allowed_methods
        assert "POST" in allowed_methods
        assert "PUT" in allowed_methods
        assert "DELETE" in allowed_methods
        assert "OPTIONS" in allowed_methods

    def test_cors_allowed_headers(self, client):
        """Test that headers are properly handled in CORS."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization",
            },
        )

        assert response.status_code == 200
        allowed_headers = response.headers.get("access-control-allow-headers")
        assert allowed_headers is not None

    def test_cors_custom_origins(self):
        """Test CORS with custom origins configuration."""
        # Create custom test settings
        custom_settings = Settings(
            app_name="Test App",
            app_version="0.1.0",
            debug=True,
            cors_origins=["https://example.com", "https://app.example.com"],
            cors_credentials=True,
            cors_methods=["GET", "POST"],
            cors_headers=["Content-Type"],
        )

        with patch("app.main.settings", custom_settings):
            from app.main import create_app

            app = create_app()
            client = TestClient(app)

            response = client.get("/", headers={"Origin": "https://example.com"})

            assert response.status_code == 200
            cors_origin = response.headers.get("access-control-allow-origin")
            assert cors_origin == "https://example.com"

    def test_cors_disallowed_origin(self, client):
        """Test behavior with non-allowed origin."""
        response = client.get("/", headers={"Origin": "https://malicious-site.com"})

        # The request should still succeed, but CORS headers should not allow the origin
        assert response.status_code == 200
        cors_origin = response.headers.get("access-control-allow-origin")
        assert cors_origin != "https://malicious-site.com"

    def test_cors_no_origin_header(self, client):
        """Test request without Origin header (same-origin request)."""
        response = client.get("/")

        assert response.status_code == 200
        # No CORS headers should be present for same-origin requests
        assert "access-control-allow-origin" not in response.headers


class TestCORSIntegration:
    """Test CORS integration with different endpoints."""

    def test_cors_with_api_endpoints(self, client):
        """Test CORS with API endpoints."""
        response = client.get(
            "/api/v1/health", headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_with_root_endpoint(self, client):
        """Test CORS with root endpoint."""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_with_health_endpoint(self, client):
        """Test CORS with health endpoint."""
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
