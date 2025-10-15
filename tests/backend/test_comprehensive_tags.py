"""
Comprehensive tests for tag handling in notes.
"""

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.note import NoteService


def test_tag_validation_edge_cases(test_session, test_user):
    """Test various edge cases for tag validation."""

    # Create note service
    note_service = NoteService(test_session)

    # Test 1: Empty array should result in None in database
    note_data = NoteCreate(
        title="Test Empty Array", content="Test content", tags=[], week_number=1
    )
    created_note = note_service.create_note(test_user.id, note_data)
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is None

    # Test 2: Array with empty strings should result in None
    note_data = NoteCreate(
        title="Test Empty Strings in Array",
        content="Test content",
        tags=["", "  ", ""],
        week_number=1,
    )
    created_note = note_service.create_note(test_user.id, note_data)
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is None

    # Test 3: Empty string should result in None
    note_data = NoteCreate(
        title="Test Empty String", content="Test content", tags="", week_number=1
    )
    created_note = note_service.create_note(test_user.id, note_data)
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is None

    # Test 4: String with only commas and spaces should result in None
    note_data = NoteCreate(
        title="Test Commas and Spaces",
        content="Test content",
        tags="  ,  ,  ",
        week_number=1,
    )
    created_note = note_service.create_note(test_user.id, note_data)
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is None


def test_tag_update_workflow(test_session, test_user):
    """Test the complete workflow of tag updates."""

    # Create note service
    note_service = NoteService(test_session)

    # Step 1: Create note with tags
    note_data = NoteCreate(
        title="Workflow Test",
        content="Test content",
        tags=["work", "important", "project"],
        week_number=1,
    )
    created_note = note_service.create_note(test_user.id, note_data)

    # Verify initial state
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is not None
    assert "work" in note_from_db.tags
    assert "important" in note_from_db.tags
    assert "project" in note_from_db.tags

    # Step 2: Update with new tags
    update_data = NoteUpdate(tags=["personal", "hobby"])
    updated_note = note_service.update_note(test_user.id, created_note.id, update_data)

    # Verify update
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is not None
    assert "personal" in note_from_db.tags
    assert "hobby" in note_from_db.tags
    assert "work" not in note_from_db.tags

    # Step 3: Remove all tags with empty array
    update_data = NoteUpdate(tags=[])
    updated_note = note_service.update_note(test_user.id, created_note.id, update_data)

    # Verify tags are removed
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is None

    # Step 4: Add tags back
    update_data = NoteUpdate(tags=["restored"])
    updated_note = note_service.update_note(test_user.id, created_note.id, update_data)

    # Verify tags are back
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is not None
    assert "restored" in note_from_db.tags

    # Step 5: Remove tags with empty string
    update_data = NoteUpdate(tags="")
    updated_note = note_service.update_note(test_user.id, created_note.id, update_data)

    # Verify tags are removed again
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is None


def test_tag_api_endpoint(client, test_user, test_session):
    """Test tag deletion through the actual API endpoint."""

    # Step 1: Create note with tags through API
    note_data = {
        "title": "API Test Note",
        "content": "Test content",
        "tags": ["api", "test", "important"],
        "week_number": 1,
    }

    response = client.post(f"/api/v1/notes/?user_id={test_user.id}", json=note_data)
    assert response.status_code == 201
    created_note = response.json()
    note_id = created_note["id"]

    # Verify tags in response
    assert created_note["tags"] == ["api", "important", "test"]  # Should be sorted

    # Step 2: Update note to remove all tags with empty array
    update_data = {"title": "Updated API Test Note", "tags": []}

    response = client.put(
        f"/api/v1/notes/{note_id}?user_id={test_user.id}", json=update_data
    )
    assert response.status_code == 200
    updated_note = response.json()

    # Verify tags are removed in API response
    assert updated_note["tags"] is None or updated_note["tags"] == []

    # Step 3: Verify directly in database
    note_from_db = test_session.query(Note).filter(Note.id == note_id).first()
    assert note_from_db.tags is None

    # Step 4: Update with empty string
    update_data = {"tags": ""}

    response = client.put(
        f"/api/v1/notes/{note_id}?user_id={test_user.id}", json=update_data
    )
    assert response.status_code == 200
    updated_note = response.json()

    # Verify tags are still removed
    assert updated_note["tags"] is None or updated_note["tags"] == []

    # Verify in database
    note_from_db = test_session.query(Note).filter(Note.id == note_id).first()
    assert note_from_db.tags is None
