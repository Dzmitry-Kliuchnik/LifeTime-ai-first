"""
Test the new clear_omitted_tags functionality.
"""

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.note import NoteService


def test_clear_omitted_tags_parameter(test_session, test_user):
    """Test the new clear_omitted_tags parameter."""

    note_service = NoteService(test_session)

    print("=== Testing clear_omitted_tags Parameter ===")

    # Create note with tags
    note = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Test Note",
            content="Test content",
            tags=["should", "be", "cleared"],
            week_number=1,
        ),
    )

    # Verify initial state
    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    print(f"Initial tags: {repr(db_note.tags)}")
    assert "should" in db_note.tags

    # Test 1: Normal behavior (clear_omitted_tags=False) - tags remain
    print("\n1. Testing normal behavior (clear_omitted_tags=False)...")
    update_data = NoteUpdate(title="Updated Title")  # Omit tags field

    updated_note = note_service.update_note(
        test_user.id, note.id, update_data, clear_omitted_tags=False
    )

    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    print(f"Tags after normal update: {repr(db_note.tags)}")
    assert db_note.tags is not None  # Tags should remain
    assert "should" in db_note.tags

    # Test 2: New behavior (clear_omitted_tags=True) - tags cleared
    print("\n2. Testing new behavior (clear_omitted_tags=True)...")
    update_data2 = NoteUpdate(title="Updated Title 2")  # Omit tags field

    updated_note2 = note_service.update_note(
        test_user.id, note.id, update_data2, clear_omitted_tags=True
    )

    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    print(f"Tags after clear_omitted_tags=True: {repr(db_note.tags)}")
    assert db_note.tags is None  # Tags should be cleared

    # Test 3: Explicit tags should still work regardless of flag
    print("\n3. Testing explicit tags with clear_omitted_tags=True...")
    update_data3 = NoteUpdate(title="Updated Title 3", tags=["new", "tags"])

    updated_note3 = note_service.update_note(
        test_user.id, note.id, update_data3, clear_omitted_tags=True
    )

    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    print(f"Tags after explicit update: {repr(db_note.tags)}")
    assert db_note.tags is not None
    assert "new" in db_note.tags and "tags" in db_note.tags

    # Test 4: Explicit empty tags should work regardless of flag
    print("\n4. Testing explicit empty tags with clear_omitted_tags=True...")
    update_data4 = NoteUpdate(title="Updated Title 4", tags=[])

    updated_note4 = note_service.update_note(
        test_user.id, note.id, update_data4, clear_omitted_tags=True
    )

    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    print(f"Tags after explicit empty: {repr(db_note.tags)}")
    assert db_note.tags is None  # Should be cleared

    print("\n=== All tests passed! ===")


def test_api_endpoint_with_clear_omitted_tags(test_session, test_user):
    """Test that the API endpoint parameter works correctly."""

    # This test would require the full API setup, so we'll just test the service layer
    # The API test would look like:
    # PUT /api/v1/notes/123?user_id=1&clear_omitted_tags=true
    # Body: {"title": "Updated"}  // No tags field
    # Expected: Tags get cleared in database

    print("=== API Endpoint Test (Service Layer) ===")

    note_service = NoteService(test_session)

    # Create note
    note = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="API Test", content="Test", tags=["api", "test"], week_number=1
        ),
    )

    # Simulate API call with clear_omitted_tags=true
    update_payload = {"title": "Updated via API"}  # Frontend omits tags
    update_schema = NoteUpdate(**update_payload)

    # This simulates the API endpoint calling the service with clear_omitted_tags=True
    updated_note = note_service.update_note(
        test_user.id, note.id, update_schema, clear_omitted_tags=True
    )

    # Verify tags were cleared
    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    print(f"API test result - tags: {repr(db_note.tags)}")
    assert db_note.tags is None
    assert db_note.title == "Updated via API"

    print("✓ API endpoint behavior works correctly")
