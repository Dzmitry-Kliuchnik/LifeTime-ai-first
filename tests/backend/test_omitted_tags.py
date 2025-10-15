"""
Test the specific issue where frontend omits tags field entirely.
"""

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.note import NoteService


def test_frontend_omits_tags_field(test_session, test_user):
    """Test when frontend completely omits the tags field from payload."""

    note_service = NoteService(test_session)

    print("=== Testing Frontend Omitting Tags Field ===")

    # Create note with tags
    note = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Test Note",
            content="Test content",
            tags=["should", "be", "removed"],
            week_number=1,
        ),
    )

    # Verify initial state
    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    print(f"Initial tags: {repr(db_note.tags)}")
    assert "should" in db_note.tags

    # Simulate frontend payload that omits tags field entirely
    # This is what happens when frontend sends: {"title": "Updated Title"}
    # without any tags field
    frontend_payload = {"title": "Updated Title"}

    # Create update schema from frontend payload
    update_schema = NoteUpdate(**frontend_payload)

    # Check what gets included in model_dump
    dumped = update_schema.model_dump(exclude_unset=True)
    print(f"Model dump from omitted tags: {dumped}")

    # This should NOT include tags field
    assert "tags" not in dumped
    print("✓ Tags field correctly excluded from update")

    # Perform update
    updated_note = note_service.update_note(test_user.id, note.id, update_schema)

    # Check database - tags should still be there (NOT cleared)
    db_note_after = test_session.query(Note).filter(Note.id == note.id).first()
    print(f"Tags after update: {repr(db_note_after.tags)}")

    # This is the current behavior - tags remain unchanged
    assert db_note_after.tags is not None
    assert "should" in db_note_after.tags
    print("✓ Current behavior: tags remain when field omitted")

    print("\n=== This demonstrates the issue! ===")
    print("When frontend omits tags field, they don't get cleared.")


def test_explicit_empty_tags_vs_omitted(test_session, test_user):
    """Compare explicit empty tags vs omitted tags field."""

    note_service = NoteService(test_session)

    print("\n=== Comparing Explicit vs Omitted ===")

    # Test 1: Explicit empty tags
    note1 = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Explicit Test", content="Test", tags=["remove"], week_number=1
        ),
    )

    explicit_payload = {
        "title": "Updated",
        "tags": [],
    }  # Frontend explicitly sends empty array
    explicit_update = NoteUpdate(**explicit_payload)
    explicit_dump = explicit_update.model_dump(exclude_unset=True)
    print(f"Explicit empty tags dump: {explicit_dump}")

    note_service.update_note(test_user.id, note1.id, explicit_update)
    db_note1 = test_session.query(Note).filter(Note.id == note1.id).first()
    print(f"Result with explicit empty: {repr(db_note1.tags)}")
    assert db_note1.tags is None  # Tags cleared

    # Test 2: Omitted tags field
    note2 = note_service.create_note(
        test_user.id,
        NoteCreate(title="Omitted Test", content="Test", tags=["keep"], week_number=1),
    )

    omitted_payload = {"title": "Updated"}  # Frontend omits tags field
    omitted_update = NoteUpdate(**omitted_payload)
    omitted_dump = omitted_update.model_dump(exclude_unset=True)
    print(f"Omitted tags dump: {omitted_dump}")

    note_service.update_note(test_user.id, note2.id, omitted_update)
    db_note2 = test_session.query(Note).filter(Note.id == note2.id).first()
    print(f"Result with omitted: {repr(db_note2.tags)}")
    assert db_note2.tags is not None  # Tags remain
    assert "keep" in db_note2.tags
