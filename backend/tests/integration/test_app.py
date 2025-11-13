"""
Integration tests for FastAPI application
"""
import pytest
from fastapi.testclient import TestClient

from main import app


class TestFastAPIApplication:
    """Test suite for FastAPI application setup"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client"""
        return TestClient(app)

    def test_health_check(self, client: TestClient) -> None:
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "service" in data

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"

    def test_cors_headers(self, client: TestClient) -> None:
        """Test CORS headers are configured"""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_value_error_handler(self, client: TestClient) -> None:
        """Test ValueError exception handler"""

        @app.get("/test-value-error")
        def trigger_value_error():
            raise ValueError("Test validation error")

        response = client.get("/test-value-error")
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Validation error"
        assert "Test validation error" in data["message"]
        assert "path" in data

    def test_openapi_docs_available(self, client: TestClient) -> None:
        """Test OpenAPI documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200

        response = client.get("/openapi.json")
        assert response.status_code == 200
        openapi_schema = response.json()
        assert openapi_schema["info"]["title"] == "Social Comment Scraper API"
        assert openapi_schema["info"]["version"] == "0.1.0"

    def test_app_metadata(self, client: TestClient) -> None:
        """Test application metadata is correctly set"""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "Social Comment Scraper" in schema["info"]["title"]
        assert "description" in schema["info"]
        assert len(schema["info"]["description"]) > 0
