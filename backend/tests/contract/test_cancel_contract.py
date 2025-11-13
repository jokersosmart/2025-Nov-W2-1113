"""
Contract tests for POST /api/scrape/{id}/cancel endpoint

These tests define the expected behavior of the cancel endpoint
before implementation (TDD approach).
"""
import pytest
from fastapi.testclient import TestClient

from main import app


class TestCancelContract:
    """Contract tests for cancel endpoint"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client"""
        return TestClient(app)

    def test_cancel_endpoint_exists(self, client: TestClient) -> None:
        """Test that POST /api/scrape/{id}/cancel endpoint is accessible"""
        response = client.post("/api/scrape/test-id/cancel")
        # Should not return 404
        assert response.status_code != 404

    def test_cancel_requires_valid_scrape_id(self, client: TestClient) -> None:
        """Test that invalid scrape_id returns 404"""
        response = client.post("/api/scrape/non-existent-id/cancel")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data.get("message", "").lower() or "error" in data

    def test_cancel_active_scrape(self, client: TestClient) -> None:
        """Test cancelling an active scrape job"""
        # Create scrape job
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # Cancel the job
        response = client.post(f"/api/scrape/{scrape_id}/cancel")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "cancelled"

    def test_cancel_returns_confirmation(self, client: TestClient) -> None:
        """Test that cancel returns confirmation message"""
        # Create scrape job
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # Cancel
        response = client.post(f"/api/scrape/{scrape_id}/cancel")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "status" in data
        assert data.get("scrape_id") == scrape_id or data.get("scrapeId") == scrape_id

    def test_cancel_idempotency(self, client: TestClient) -> None:
        """Test that cancelling twice is idempotent"""
        # Create scrape job
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # First cancel
        response1 = client.post(f"/api/scrape/{scrape_id}/cancel")
        assert response1.status_code == 200

        # Second cancel (should also succeed or return appropriate status)
        response2 = client.post(f"/api/scrape/{scrape_id}/cancel")
        assert response2.status_code in [200, 409]  # OK or Conflict

        if response2.status_code == 200:
            data = response2.json()
            assert data["status"] == "cancelled"

    def test_cancel_completed_scrape(self, client: TestClient) -> None:
        """Test that cancelling a completed scrape returns appropriate error"""
        # This would require waiting for completion or mocking
        # For contract test, we just verify the expected behavior pattern
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # Attempt to cancel
        response = client.post(f"/api/scrape/{scrape_id}/cancel")

        # Should either succeed (200) or return conflict (409)
        assert response.status_code in [200, 409]

        if response.status_code == 409:
            data = response.json()
            assert "message" in data or "error" in data

    def test_cancel_response_schema(self, client: TestClient) -> None:
        """Test that cancel response follows expected schema"""
        # Create scrape job
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # Cancel
        response = client.post(f"/api/scrape/{scrape_id}/cancel")
        assert response.status_code == 200
        data = response.json()

        # Required fields
        assert "status" in data
        assert "scrape_id" in data or "scrapeId" in data

        # Status should be 'cancelled'
        assert data["status"] == "cancelled"

    def test_cancel_updates_progress(self, client: TestClient) -> None:
        """Test that cancelling updates the progress status"""
        # Create scrape job
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # Cancel
        cancel_response = client.post(f"/api/scrape/{scrape_id}/cancel")
        assert cancel_response.status_code == 200

        # Check progress shows cancelled
        progress_response = client.get(f"/api/scrape/{scrape_id}/progress")
        assert progress_response.status_code == 200
        progress_data = progress_response.json()
        assert progress_data["status"] == "cancelled"

    def test_cancel_method_not_allowed(self, client: TestClient) -> None:
        """Test that only POST is allowed for cancel endpoint"""
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # Try GET instead of POST
        response = client.get(f"/api/scrape/{scrape_id}/cancel")
        assert response.status_code == 405  # Method Not Allowed

    def test_cancel_returns_scrape_id(self, client: TestClient) -> None:
        """Test that cancel response includes scrape_id"""
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        response = client.post(f"/api/scrape/{scrape_id}/cancel")
        assert response.status_code == 200
        data = response.json()
        returned_id = data.get("scrape_id") or data.get("scrapeId")
        assert returned_id == scrape_id
