"""
Test for tag deletion issue in note updates.
"""

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.note import NoteService


def test_tag_deletion_in_note_update(test_session, test_user):
    """Test that tags are properly removed from database when note is updated with empty tags."""

    # Create note service
    note_service = NoteService(test_session)

    # Create a note with tags
    note_data = NoteCreate(
        title="Test Note with Tags",
        content="This is a test note",
        tags=["test", "important", "work"],  # Array format from frontend
        week_number=1,
    )

    created_note = note_service.create_note(test_user.id, note_data)

    # Verify tags were saved as comma-separated string
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is not None
    assert "test" in note_from_db.tags
    assert "important" in note_from_db.tags
    assert "work" in note_from_db.tags

    # Update note with empty tags (simulating frontend sending empty array)
    update_data = NoteUpdate(
        title="Updated Test Note",
        tags=[],  # Empty array from frontend
    )

    updated_note = note_service.update_note(test_user.id, created_note.id, update_data)

    # Check the database directly - tags should be None/null
    note_from_db_after_update = (
        test_session.query(Note).filter(Note.id == created_note.id).first()
    )
    assert (
        note_from_db_after_update.tags is None or note_from_db_after_update.tags == ""
    )

    # Also check that the response shows empty tags
    assert updated_note.tags is None or updated_note.tags == []


def test_tag_deletion_with_empty_string(test_session, test_user):
    """Test that tags are properly removed when updated with empty string."""

    # Create note service
    note_service = NoteService(test_session)

    # Create a note with tags
    note_data = NoteCreate(
        title="Test Note with Tags 2",
        content="This is a test note",
        tags="test,important,work",  # String format
        week_number=1,
    )

    created_note = note_service.create_note(test_user.id, note_data)

    # Verify tags were saved
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is not None

    # Update note with empty string tags
    update_data = NoteUpdate(
        title="Updated Test Note 2",
        tags="",  # Empty string
    )

    updated_note = note_service.update_note(test_user.id, created_note.id, update_data)

    # Check the database directly - tags should be None
    note_from_db_after_update = (
        test_session.query(Note).filter(Note.id == created_note.id).first()
    )
    assert note_from_db_after_update.tags is None

    # Also check that the response shows empty tags
    assert updated_note.tags is None or updated_note.tags == []


def test_tag_deletion_with_none(test_session, test_user):
    """Test that tags are properly removed when explicitly set to None."""

    # Create note service
    note_service = NoteService(test_session)

    # Create a note with tags
    note_data = NoteCreate(
        title="Test Note with Tags 3",
        content="This is a test note",
        tags=["test", "important"],
        week_number=1,
    )

    created_note = note_service.create_note(test_user.id, note_data)

    # Verify tags were saved
    note_from_db = test_session.query(Note).filter(Note.id == created_note.id).first()
    assert note_from_db.tags is not None

    # Update note with None tags
    update_data = NoteUpdate(
        title="Updated Test Note 3",
        tags=None,  # Explicit None
    )

    updated_note = note_service.update_note(test_user.id, created_note.id, update_data)

    # Check the database directly - tags should be None
    note_from_db_after_update = (
        test_session.query(Note).filter(Note.id == created_note.id).first()
    )
    assert note_from_db_after_update.tags is None

    # Also check that the response shows empty tags
    assert updated_note.tags is None or updated_note.tags == []
