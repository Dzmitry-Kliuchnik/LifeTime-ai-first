"""
Complete test suite for tag functionality.
"""

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.note import NoteService


def test_tag_creation_variations(test_session, test_user):
    """Test different ways to create notes with tags."""

    note_service = NoteService(test_session)

    # Test 1: Create with array
    note1 = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Array Tags",
            content="Test",
            tags=["work", "important"],
            week_number=1,
        ),
    )
    db_note1 = test_session.query(Note).filter(Note.id == note1.id).first()
    assert "important" in db_note1.tags and "work" in db_note1.tags

    # Test 2: Create with string
    note2 = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="String Tags",
            content="Test",
            tags="personal,hobby,fun",
            week_number=1,
        ),
    )
    db_note2 = test_session.query(Note).filter(Note.id == note2.id).first()
    assert "personal" in db_note2.tags and "hobby" in db_note2.tags

    # Test 3: Create with None
    note3 = note_service.create_note(
        test_user.id,
        NoteCreate(title="No Tags", content="Test", tags=None, week_number=1),
    )
    db_note3 = test_session.query(Note).filter(Note.id == note3.id).first()
    assert db_note3.tags is None

    # Test 4: Create with empty array
    note4 = note_service.create_note(
        test_user.id,
        NoteCreate(title="Empty Array Tags", content="Test", tags=[], week_number=1),
    )
    db_note4 = test_session.query(Note).filter(Note.id == note4.id).first()
    assert db_note4.tags is None


def test_tag_update_all_scenarios(test_session, test_user):
    """Test all possible tag update scenarios."""

    note_service = NoteService(test_session)

    # Create base note
    note = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Base Note",
            content="Test content",
            tags=["original", "tags"],
            week_number=1,
        ),
    )
    note_id = note.id

    # Scenario 1: Update tags with new array
    note_service.update_note(test_user.id, note_id, NoteUpdate(tags=["new", "tags"]))
    db_note = test_session.query(Note).filter(Note.id == note_id).first()
    assert "new" in db_note.tags and "tags" in db_note.tags
    assert "original" not in db_note.tags

    # Scenario 2: Update tags with new string
    note_service.update_note(
        test_user.id, note_id, NoteUpdate(tags="string,format,tags")
    )
    db_note = test_session.query(Note).filter(Note.id == note_id).first()
    assert "string" in db_note.tags and "format" in db_note.tags
    assert "new" not in db_note.tags

    # Scenario 3: Clear tags with empty array
    note_service.update_note(test_user.id, note_id, NoteUpdate(tags=[]))
    db_note = test_session.query(Note).filter(Note.id == note_id).first()
    assert db_note.tags is None

    # Scenario 4: Add tags back
    note_service.update_note(test_user.id, note_id, NoteUpdate(tags=["restored"]))
    db_note = test_session.query(Note).filter(Note.id == note_id).first()
    assert "restored" in db_note.tags

    # Scenario 5: Clear tags with empty string
    note_service.update_note(test_user.id, note_id, NoteUpdate(tags=""))
    db_note = test_session.query(Note).filter(Note.id == note_id).first()
    assert db_note.tags is None

    # Scenario 6: Add tags back again
    note_service.update_note(test_user.id, note_id, NoteUpdate(tags="final,test"))
    db_note = test_session.query(Note).filter(Note.id == note_id).first()
    assert "final" in db_note.tags and "test" in db_note.tags

    # Scenario 7: Clear tags with None
    note_service.update_note(test_user.id, note_id, NoteUpdate(tags=None))
    db_note = test_session.query(Note).filter(Note.id == note_id).first()
    assert db_note.tags is None


def test_tag_edge_cases(test_session, test_user):
    """Test edge cases that might cause issues."""

    note_service = NoteService(test_session)

    # Test 1: Tags with special characters
    note1 = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Special Chars",
            content="Test",
            tags=["tag-with-dash", "tag_with_underscore", "tag.with.dots"],
            week_number=1,
        ),
    )
    db_note1 = test_session.query(Note).filter(Note.id == note1.id).first()
    assert "tag-with-dash" in db_note1.tags

    # Clear these special tags
    note_service.update_note(test_user.id, note1.id, NoteUpdate(tags=[]))
    db_note1 = test_session.query(Note).filter(Note.id == note1.id).first()
    assert db_note1.tags is None

    # Test 2: Very long tag names
    long_tag = "a" * 100
    note2 = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Long Tags", content="Test", tags=[long_tag, "short"], week_number=1
        ),
    )
    db_note2 = test_session.query(Note).filter(Note.id == note2.id).first()
    assert long_tag in db_note2.tags

    # Clear long tags
    note_service.update_note(test_user.id, note2.id, NoteUpdate(tags=[]))
    db_note2 = test_session.query(Note).filter(Note.id == note2.id).first()
    assert db_note2.tags is None

    # Test 3: Duplicate tags
    note3 = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Duplicate Tags",
            content="Test",
            tags=["duplicate", "duplicate", "unique"],
            week_number=1,
        ),
    )
    db_note3 = test_session.query(Note).filter(Note.id == note3.id).first()
    # Should be deduplicated
    tag_count = db_note3.tags.count("duplicate")
    assert tag_count == 1  # Only one instance of "duplicate"

    # Clear duplicate tags
    note_service.update_note(test_user.id, note3.id, NoteUpdate(tags=[]))
    db_note3 = test_session.query(Note).filter(Note.id == note3.id).first()
    assert db_note3.tags is None


def test_tag_mixed_updates(test_session, test_user):
    """Test updating tags along with other fields."""

    note_service = NoteService(test_session)

    # Create note
    note = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Mixed Update Test",
            content="Original content",
            tags=["original"],
            week_number=1,
            is_favorite=False,
        ),
    )

    # Update multiple fields including clearing tags
    note_service.update_note(
        test_user.id,
        note.id,
        NoteUpdate(
            title="Updated Title",
            content="Updated content",
            tags=[],  # Clear tags
            is_favorite=True,
        ),
    )

    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    assert db_note.title == "Updated Title"
    assert db_note.content == "Updated content"
    assert db_note.tags is None
    assert db_note.is_favorite is True
