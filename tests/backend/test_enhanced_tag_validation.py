"""
Test for the enhanced tag validation improvements.
"""

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.note import NoteService


def test_enhanced_tag_validation(test_session, test_user):
    """Test the enhanced tag validation with edge cases."""

    note_service = NoteService(test_session)

    # Create base note
    note = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Enhanced Validation Test",
            content="Test content",
            tags=["original", "tags"],
            week_number=1,
        ),
    )

    # Test 1: Update with whitespace-only string should clear tags
    note_service.update_note(test_user.id, note.id, NoteUpdate(tags="   \t\n  "))
    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    assert db_note.tags is None

    # Add tags back
    note_service.update_note(test_user.id, note.id, NoteUpdate(tags=["restored"]))
    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    assert "restored" in db_note.tags

    # Test 2: Update with only commas and spaces should clear tags
    note_service.update_note(test_user.id, note.id, NoteUpdate(tags=" , , , "))
    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    assert db_note.tags is None

    # Add tags back again
    note_service.update_note(
        test_user.id, note.id, NoteUpdate(tags=["another", "test"])
    )
    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    assert "another" in db_note.tags and "test" in db_note.tags

    # Test 3: Update with array of empty/whitespace strings should clear tags
    note_service.update_note(
        test_user.id, note.id, NoteUpdate(tags=["", "  ", "\t", "\n"])
    )
    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    assert db_note.tags is None


def test_unusual_tag_inputs(test_session, test_user):
    """Test unusual inputs that might be sent by frontend."""

    note_service = NoteService(test_session)

    # Test 1: Create note with numeric tags (convert to string)
    note1 = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Numeric Tags",
            content="Test",
            tags=["123", "456", "789"],
            week_number=1,
        ),
    )
    db_note1 = test_session.query(Note).filter(Note.id == note1.id).first()
    assert "123" in db_note1.tags and "456" in db_note1.tags

    # Clear with empty array
    note_service.update_note(test_user.id, note1.id, NoteUpdate(tags=[]))
    db_note1 = test_session.query(Note).filter(Note.id == note1.id).first()
    assert db_note1.tags is None

    # Test 2: Mixed content tags
    note2 = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Mixed Tags",
            content="Test",
            tags=["tag1", "", "tag2", "   ", "tag3"],
            week_number=1,
        ),
    )
    db_note2 = test_session.query(Note).filter(Note.id == note2.id).first()
    # Should only keep non-empty tags
    assert "tag1" in db_note2.tags
    assert "tag2" in db_note2.tags
    assert "tag3" in db_note2.tags
    # Should not contain empty strings
    assert db_note2.tags.count(",") == 2  # Only 3 real tags, so 2 commas

    # Clear with empty string
    note_service.update_note(test_user.id, note2.id, NoteUpdate(tags=""))
    db_note2 = test_session.query(Note).filter(Note.id == note2.id).first()
    assert db_note2.tags is None
