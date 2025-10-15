"""
Comprehensive API tests for Note endpoints with CRUD operations, filtering, pagination, validation, and authorization.
"""

from datetime import date
from typing import Any, Dict

import pytest
from app.models.user import User
from fastapi.testclient import TestClient


class TestNotesAPI:
    """Test Notes API endpoints with comprehensive coverage."""

    @pytest.fixture
    def test_user(self, test_session) -> User:
        """Create a test user with date of birth for week calculations."""
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

    @pytest.fixture
    def sample_note_data(self) -> Dict[str, Any]:
        """Sample note data for testing."""
        return {
            "title": "Test Note",
            "content": "This is a test note content with enough words to test word count calculation functionality.",
            "tags": "test,api,sample",
            "is_favorite": False,
            "is_archived": False,
            "note_date": date.today().isoformat(),
            "week_number": 1800,  # Safe week number from the past
        }

    def test_create_note_success(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test successful note creation."""
        response = client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": test_user.id}
        )

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == sample_note_data["title"]
        assert data["content"] == sample_note_data["content"]
        # Tags are returned as a list from the API, so compare as sets
        expected_tags = set(sample_note_data["tags"].split(","))
        actual_tags = set(data["tags"]) if data["tags"] else set()
        assert actual_tags == expected_tags
        assert data["owner_id"] == test_user.id
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["word_count"] > 0
        assert data["reading_time"] > 0

    def test_create_note_future_week_validation(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test that creating notes for future weeks is rejected."""
        # Set a very high week number (future week)
        sample_note_data["week_number"] = 9999

        response = client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": test_user.id}
        )

        assert response.status_code == 422
        assert (
            "future weeks"
            in response.json().get("error", response.json().get("detail", "")).lower()
        )

    def test_create_note_user_not_found(
        self, client: TestClient, sample_note_data: Dict[str, Any]
    ):
        """Test note creation with non-existent user."""
        response = client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": 99999}
        )

        assert response.status_code == 404
        assert (
            "not found"
            in response.json().get("error", response.json().get("detail", "")).lower()
        )

    def test_create_note_validation_errors(self, client: TestClient, test_user: User):
        """Test note creation with invalid data."""
        invalid_data = {
            "title": "",  # Empty title should fail
            "content": "",  # Empty content should fail
            "week_number": -1,  # Negative week number should fail
        }

        response = client.post(
            "/api/v1/notes/", json=invalid_data, params={"user_id": test_user.id}
        )

        assert response.status_code == 422

    def test_get_note_by_id_success(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test successful note retrieval by ID."""
        # First create a note
        create_response = client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": test_user.id}
        )
        note_id = create_response.json()["id"]

        # Then retrieve it
        response = client.get(
            f"/api/v1/notes/{note_id}", params={"user_id": test_user.id}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == note_id
        assert data["title"] == sample_note_data["title"]

    def test_get_note_by_id_not_found(self, client: TestClient, test_user: User):
        """Test retrieval of non-existent note."""
        response = client.get("/api/v1/notes/99999", params={"user_id": test_user.id})

        assert response.status_code == 404

    def test_get_note_by_id_wrong_owner(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test that users can't access notes they don't own."""
        # Create note with test_user
        create_response = client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": test_user.id}
        )
        note_id = create_response.json()["id"]

        # Try to access with different user_id
        response = client.get(f"/api/v1/notes/{note_id}", params={"user_id": 99999})

        assert response.status_code == 404

    def test_get_notes_pagination(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test notes listing with pagination."""
        # Create multiple notes
        for i in range(5):
            note_data = sample_note_data.copy()
            note_data["title"] = f"Test Note {i+1}"
            client.post(
                "/api/v1/notes/", json=note_data, params={"user_id": test_user.id}
            )

        # Test pagination
        response = client.get(
            "/api/v1/notes/", params={"user_id": test_user.id, "page": 1, "size": 3}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["notes"]) == 3
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["size"] == 3
        assert data["pages"] == 2

    def test_get_notes_week_filter(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test notes listing with week_index filtering."""
        # Create notes with different week numbers
        week_1_data = sample_note_data.copy()
        week_1_data["title"] = "Week 1 Note"
        week_1_data["week_number"] = 1800

        week_2_data = sample_note_data.copy()
        week_2_data["title"] = "Week 2 Note"
        week_2_data["week_number"] = 1801

        client.post(
            "/api/v1/notes/", json=week_1_data, params={"user_id": test_user.id}
        )
        client.post(
            "/api/v1/notes/", json=week_2_data, params={"user_id": test_user.id}
        )

        # Filter by week_index
        response = client.get(
            "/api/v1/notes/", params={"user_id": test_user.id, "week_index": 1800}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["notes"]) == 1
        assert data["notes"][0]["title"] == "Week 1 Note"

    def test_update_note_success(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test successful note update."""
        # Create a note
        create_response = client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": test_user.id}
        )
        note_id = create_response.json()["id"]

        # Update the note
        update_data = {
            "title": "Updated Test Note",
            "content": "Updated content",
            "is_favorite": True,
        }

        response = client.put(
            f"/api/v1/notes/{note_id}",
            json=update_data,
            params={"user_id": test_user.id},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Test Note"
        assert data["content"] == "Updated content"
        assert data["is_favorite"] is True

    def test_update_note_future_week_validation(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test that updating notes to future weeks is rejected."""
        # Create a note
        create_response = client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": test_user.id}
        )
        note_id = create_response.json()["id"]

        # Try to update with future week
        update_data = {"week_number": 9999}

        response = client.put(
            f"/api/v1/notes/{note_id}",
            json=update_data,
            params={"user_id": test_user.id},
        )

        assert response.status_code == 422
        assert (
            "future weeks"
            in response.json().get("error", response.json().get("detail", "")).lower()
        )

    def test_update_note_not_found(self, client: TestClient, test_user: User):
        """Test updating non-existent note."""
        update_data = {"title": "Updated Title"}

        response = client.put(
            "/api/v1/notes/99999", json=update_data, params={"user_id": test_user.id}
        )

        assert response.status_code == 404

    def test_update_note_wrong_owner(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test that users can't update notes they don't own."""
        # Create note with test_user
        create_response = client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": test_user.id}
        )
        note_id = create_response.json()["id"]

        # Try to update with different user_id
        update_data = {"title": "Hacked Title"}

        response = client.put(
            f"/api/v1/notes/{note_id}", json=update_data, params={"user_id": 99999}
        )

        assert response.status_code == 404

    def test_delete_note_success(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test successful note deletion."""
        # Create a note
        create_response = client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": test_user.id}
        )
        note_id = create_response.json()["id"]

        # Delete the note
        response = client.delete(
            f"/api/v1/notes/{note_id}", params={"user_id": test_user.id}
        )

        assert response.status_code == 204

        # Verify note is soft-deleted (should not be found in normal queries)
        get_response = client.get(
            f"/api/v1/notes/{note_id}", params={"user_id": test_user.id}
        )
        assert get_response.status_code == 404

    def test_delete_note_not_found(self, client: TestClient, test_user: User):
        """Test deleting non-existent note."""
        response = client.delete(
            "/api/v1/notes/99999", params={"user_id": test_user.id}
        )

        assert response.status_code == 404

    def test_delete_note_wrong_owner(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test that users can't delete notes they don't own."""
        # Create note with test_user
        create_response = client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": test_user.id}
        )
        note_id = create_response.json()["id"]

        # Try to delete with different user_id
        response = client.delete(f"/api/v1/notes/{note_id}", params={"user_id": 99999})

        assert response.status_code == 404

    def test_notes_listing_include_deleted(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test notes listing with include_deleted parameter."""
        # Create and delete a note
        create_response = client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": test_user.id}
        )
        note_id = create_response.json()["id"]

        client.delete(f"/api/v1/notes/{note_id}", params={"user_id": test_user.id})

        # Get notes without deleted
        response = client.get(
            "/api/v1/notes/", params={"user_id": test_user.id, "include_deleted": False}
        )
        assert response.status_code == 200
        assert len(response.json()["notes"]) == 0

        # Get notes with deleted
        response = client.get(
            "/api/v1/notes/", params={"user_id": test_user.id, "include_deleted": True}
        )
        assert response.status_code == 200
        assert len(response.json()["notes"]) == 1
        assert response.json()["notes"][0]["is_deleted"] is True

    def test_search_notes_endpoint(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test notes search functionality."""
        # Create notes with different content
        note1_data = sample_note_data.copy()
        note1_data["title"] = "Python Tutorial"
        note1_data["content"] = "Learn Python programming"

        note2_data = sample_note_data.copy()
        note2_data["title"] = "JavaScript Guide"
        note2_data["content"] = "Learn JavaScript development"

        client.post("/api/v1/notes/", json=note1_data, params={"user_id": test_user.id})
        client.post("/api/v1/notes/", json=note2_data, params={"user_id": test_user.id})

        # Search by query
        search_data = {"query": "Python"}
        response = client.post(
            "/api/v1/notes/search", json=search_data, params={"user_id": test_user.id}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["notes"]) == 1
        assert "Python" in data["notes"][0]["title"]

    def test_get_week_notes_endpoint(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test getting notes for a specific week."""
        # Create a note for a specific week
        week_number = 1800
        sample_note_data["week_number"] = week_number

        client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": test_user.id}
        )

        # Get notes for that week
        response = client.get(
            f"/api/v1/notes/week/{week_number}", params={"user_id": test_user.id}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["week_number"] == week_number
        assert len(data["notes"]) == 1
        assert "week_start_date" in data
        assert "week_end_date" in data

    def test_get_note_statistics_endpoint(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test getting note statistics."""
        # Create a few notes
        for i in range(3):
            note_data = sample_note_data.copy()
            note_data["title"] = f"Test Note {i+1}"
            note_data["is_favorite"] = i == 0  # Make first note favorite
            client.post(
                "/api/v1/notes/", json=note_data, params={"user_id": test_user.id}
            )

        # Get statistics
        response = client.get(
            "/api/v1/notes/stats/summary", params={"user_id": test_user.id}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_notes"] == 3
        assert data["favorite_notes"] == 1
        assert "notes_by_week" in data

    def test_get_tags_endpoint(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test getting unique tags."""
        # Create notes with different tags
        note1_data = sample_note_data.copy()
        note1_data["tags"] = "tag1,tag2,common"

        note2_data = sample_note_data.copy()
        note2_data["tags"] = "tag3,tag4,common"

        client.post("/api/v1/notes/", json=note1_data, params={"user_id": test_user.id})
        client.post("/api/v1/notes/", json=note2_data, params={"user_id": test_user.id})

        # Get tags
        response = client.get(
            "/api/v1/notes/meta/tags", params={"user_id": test_user.id}
        )

        assert response.status_code == 200
        data = response.json()
        expected_tags = ["tag1", "tag2", "tag3", "tag4", "common"]
        assert len(data) == len(expected_tags)
        assert all(tag in data for tag in expected_tags)

    def test_restore_note_endpoint(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test restoring a soft-deleted note."""
        # Create and delete a note
        create_response = client.post(
            "/api/v1/notes/", json=sample_note_data, params={"user_id": test_user.id}
        )
        note_id = create_response.json()["id"]

        client.delete(f"/api/v1/notes/{note_id}", params={"user_id": test_user.id})

        # Restore the note
        response = client.post(
            f"/api/v1/notes/{note_id}/restore", params={"user_id": test_user.id}
        )

        assert response.status_code == 200
        data = response.json()
        assert not data["is_deleted"]
        assert data["deleted_at"] is None

        # Verify note is accessible again
        get_response = client.get(
            f"/api/v1/notes/{note_id}", params={"user_id": test_user.id}
        )
        assert get_response.status_code == 200

    def test_pagination_edge_cases(
        self, client: TestClient, test_user: User, sample_note_data: Dict[str, Any]
    ):
        """Test pagination edge cases."""
        # Test with no notes
        response = client.get(
            "/api/v1/notes/", params={"user_id": test_user.id, "page": 1, "size": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["pages"] == 0
        assert len(data["notes"]) == 0

        # Test invalid page parameters
        response = client.get(
            "/api/v1/notes/", params={"user_id": test_user.id, "page": 0, "size": 10}
        )
        assert response.status_code == 422  # Validation error

        response = client.get(
            "/api/v1/notes/", params={"user_id": test_user.id, "page": 1, "size": 0}
        )
        assert response.status_code == 422  # Validation error

    def test_large_content_handling(self, client: TestClient, test_user: User):
        """Test handling of large note content."""
        large_content = "Lorem ipsum " * 1000  # Create large content

        note_data = {
            "title": "Large Content Note",
            "content": large_content,
            "week_number": 1800,
        }

        response = client.post(
            "/api/v1/notes/", json=note_data, params={"user_id": test_user.id}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["word_count"] > 1000
        assert data["reading_time"] > 5  # Should calculate significant reading time
