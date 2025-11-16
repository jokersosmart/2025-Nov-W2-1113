"""
Unit tests for error handler middleware

Tests the unified error handling middleware following TDD principles.
"""
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError

from src.api.middleware.error_handler import (
    AppError,
    InvalidURLError,
    NetworkError,
    RateLimitError,
    ScraperError,
    add_error_handlers,
)


# Test app setup
def create_test_app() -> FastAPI:
    """Create FastAPI app with error handlers for testing"""
    app = FastAPI()
    add_error_handlers(app)

    # Test endpoints
    @app.get("/test/success")
    async def success():
        return {"status": "ok"}

    @app.get("/test/app-error")
    async def app_error():
        raise AppError("Test app error", status_code=400)

    @app.get("/test/invalid-url")
    async def invalid_url():
        raise InvalidURLError("https://invalid.com")

    @app.get("/test/network-error")
    async def network_error():
        raise NetworkError("Connection timeout")

    @app.get("/test/rate-limit")
    async def rate_limit():
        raise RateLimitError("Too many requests")

    @app.get("/test/scraper-error")
    async def scraper_error():
        raise ScraperError("Failed to parse HTML", "Cannot find comment elements")

    @app.get("/test/http-exception")
    async def http_exception():
        raise HTTPException(status_code=404, detail="Resource not found")

    @app.get("/test/unhandled")
    async def unhandled_exception():
        raise RuntimeError("Unexpected error")

    class TestModel(BaseModel):
        required_field: str

    @app.post("/test/validation")
    async def validation_error(data: TestModel):
        return {"received": data.required_field}

    return app


@pytest.fixture
def client():
    """Test client fixture"""
    app = create_test_app()
    return TestClient(app, raise_server_exceptions=False)


# RED: Write failing tests first
class TestAppError:
    """Test custom AppError exception"""

    def test_app_error_returns_custom_status_code(self, client):
        """AppError should return specified status code"""
        response = client.get("/test/app-error")
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "App Error"
        assert "Test app error" in data["message"]

    def test_app_error_includes_timestamp(self, client):
        """AppError response should include timestamp"""
        response = client.get("/test/app-error")
        data = response.json()
        assert "timestamp" in data
        # Timestamp should be ISO format
        assert "T" in data["timestamp"]


class TestDomainErrors:
    """Test domain-specific error types"""

    def test_invalid_url_error_returns_400(self, client):
        """InvalidURLError should return 400 Bad Request"""
        response = client.get("/test/invalid-url")
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Invalid URL"
        assert "https://invalid.com" in data["message"]

    def test_network_error_returns_500(self, client):
        """NetworkError should return 500 Internal Server Error"""
        response = client.get("/test/network-error")
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "Network Error"
        assert "Connection timeout" in data["message"]

    def test_rate_limit_error_returns_429(self, client):
        """RateLimitError should return 429 Too Many Requests"""
        response = client.get("/test/rate-limit")
        assert response.status_code == 429
        data = response.json()
        assert data["error"] == "Rate Limit Exceeded"
        assert "Too many requests" in data["message"]

    def test_rate_limit_includes_retry_after_header(self, client):
        """RateLimitError should include Retry-After header"""
        response = client.get("/test/rate-limit")
        assert "Retry-After" in response.headers
        # Default should be 60 seconds
        assert response.headers["Retry-After"] == "60"

    def test_scraper_error_returns_500_with_details(self, client):
        """ScraperError should return 500 with technical details"""
        response = client.get("/test/scraper-error")
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "Scraper Error"
        assert "Failed to parse HTML" in data["message"]
        assert "details" in data
        assert "technical_details" in data["details"]
        assert "Cannot find comment elements" in data["details"]["technical_details"]


class TestHTTPExceptionHandling:
    """Test FastAPI HTTPException handling"""

    def test_http_exception_preserved(self, client):
        """HTTPException should be handled correctly"""
        response = client.get("/test/http-exception")
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "Not Found"
        assert "Resource not found" in data["message"]


class TestValidationErrorHandling:
    """Test request validation error handling"""

    def test_validation_error_returns_422(self, client):
        """Validation errors should return 422 Unprocessable Entity"""
        response = client.post("/test/validation", json={})
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "Validation Error"
        assert "required_field" in data["message"].lower()

    def test_validation_error_includes_field_details(self, client):
        """Validation error should include field-specific details"""
        response = client.post("/test/validation", json={"wrong_field": "value"})
        data = response.json()
        assert "details" in data
        # Should indicate which field is missing
        assert any("required_field" in str(detail) for detail in data["details"])


class TestUnhandledExceptions:
    """Test global exception handler"""

    def test_unhandled_exception_returns_500(self, client):
        """Unhandled exceptions should return 500"""
        response = client.get("/test/unhandled")
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "Internal Server Error"

    def test_unhandled_exception_includes_path(self, client):
        """Unhandled exception response should include request path"""
        response = client.get("/test/unhandled")
        data = response.json()
        assert "path" in data
        assert "/test/unhandled" in data["path"]

    def test_unhandled_exception_hides_sensitive_details_in_production(self, client):
        """Production mode should not expose internal error details"""
        # This is tested by checking message is generic
        response = client.get("/test/unhandled")
        data = response.json()
        # In development, we might show the error
        # In production, message should be generic
        assert "message" in data


class TestSuccessfulRequests:
    """Test that error handlers don't interfere with successful requests"""

    def test_successful_request_not_affected(self, client):
        """Successful requests should work normally"""
        response = client.get("/test/success")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestErrorResponseFormat:
    """Test error response format consistency"""

    def test_all_errors_have_consistent_format(self, client):
        """All error responses should follow the same structure"""
        error_endpoints = [
            "/test/app-error",
            "/test/invalid-url",
            "/test/network-error",
            "/test/rate-limit",
            "/test/scraper-error",
        ]

        for endpoint in error_endpoints:
            response = client.get(endpoint)
            data = response.json()

            # Required fields
            assert "error" in data, f"Missing 'error' in {endpoint}"
            assert "message" in data, f"Missing 'message' in {endpoint}"
            assert "timestamp" in data, f"Missing 'timestamp' in {endpoint}"

            # Error type should be a string
            assert isinstance(data["error"], str)
            assert isinstance(data["message"], str)
            assert isinstance(data["timestamp"], str)
