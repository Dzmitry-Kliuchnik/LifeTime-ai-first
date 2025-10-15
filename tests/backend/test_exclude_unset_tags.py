"""
Test for the specific issue with exclude_unset=True and tag deletion.
"""

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.note import NoteService


def test_exclude_unset_tag_issue(test_session, test_user):
    """Test that tags are properly handled when using exclude_unset=True."""

    # Create note service
    note_service = NoteService(test_session)

    # Create a note with tags
    note_data = NoteCreate(
        title="Test Note with Tags",
        content="This is a test note",
        tags=["work", "important"],
        week_number=1,
    )

    created_note = note_service.create_note(test_user.id, note_data)

    # Verify tags were saved
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is not None
    assert "work" in note_from_db.tags

    # Test 1: Update with empty array, but only set tags field
    update_data = NoteUpdate(tags=[])

    # Check what model_dump(exclude_unset=True) produces
    dumped_data = update_data.model_dump(exclude_unset=True)
    print(f"Dumped data for empty array: {dumped_data}")

    # This should include 'tags': None because we explicitly set tags to []
    assert "tags" in dumped_data
    assert dumped_data["tags"] is None

    # Now perform the actual update
    updated_note = note_service.update_note(test_user.id, created_note.id, update_data)

    # Check database - tags should be None
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is None

    # Test 2: Create another note and test with different update pattern
    note_data2 = NoteCreate(
        title="Test Note 2",
        content="Another test note",
        tags=["test", "example"],
        week_number=1,
    )

    created_note2 = note_service.create_note(test_user.id, note_data2)

    # Update with multiple fields including empty tags
    update_data2 = NoteUpdate(title="Updated Title", tags=[], is_favorite=True)

    dumped_data2 = update_data2.model_dump(exclude_unset=True)
    print(f"Dumped data for multiple fields update: {dumped_data2}")

    # This should include all three fields
    assert "title" in dumped_data2
    assert "tags" in dumped_data2
    assert "is_favorite" in dumped_data2
    assert dumped_data2["tags"] is None

    updated_note2 = note_service.update_note(
        test_user.id, created_note2.id, update_data2
    )

    # Check database
    note_from_db2 = test_session.query(Note).filter(Note.id == created_note2.id).first()
    assert note_from_db2.tags is None
    assert note_from_db2.title == "Updated Title"
    assert note_from_db2.is_favorite is True


def test_partial_update_scenarios(test_session, test_user):
    """Test different partial update scenarios that might cause issues."""

    note_service = NoteService(test_session)

    # Create note with tags
    note_data = NoteCreate(
        title="Partial Update Test",
        content="Test content",
        tags=["original", "tags"],
        week_number=1,
    )

    created_note = note_service.create_note(test_user.id, note_data)
    original_note_id = created_note.id

    # Scenario 1: Update only title, don't touch tags
    update_data1 = NoteUpdate(title="New Title Only")
    dumped1 = update_data1.model_dump(exclude_unset=True)
    print(f"Title-only update: {dumped1}")

    # Tags should not be in the update dict
    assert "tags" not in dumped1

    note_service.update_note(test_user.id, original_note_id, update_data1)
    note_from_db = test_session.query(Note).filter(Note.id == original_note_id).first()

    # Tags should still be there
    assert note_from_db.tags is not None
    assert "original" in note_from_db.tags

    # Scenario 2: Update title AND explicitly clear tags
    update_data2 = NoteUpdate(title="New Title With Cleared Tags", tags=[])
    dumped2 = update_data2.model_dump(exclude_unset=True)
    print(f"Title + cleared tags update: {dumped2}")

    # Both fields should be in the update dict
    assert "title" in dumped2
    assert "tags" in dumped2
    assert dumped2["tags"] is None

    note_service.update_note(test_user.id, original_note_id, update_data2)
    note_from_db = test_session.query(Note).filter(Note.id == original_note_id).first()

    # Tags should now be None
    assert note_from_db.tags is None
    assert note_from_db.title == "New Title With Cleared Tags"
