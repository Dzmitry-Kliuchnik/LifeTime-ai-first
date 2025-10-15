"""
Debug test to trace tag deletion issue step by step.
"""

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.note import NoteService


def test_debug_tag_propagation(test_session, test_user):
    """Debug the exact flow of tag deletion."""

    print("=== DEBUG: Tag Propagation Test ===")

    # Create note service
    note_service = NoteService(test_session)

    # Step 1: Create note with tags
    print("\n1. Creating note with tags...")
    note_data = NoteCreate(
        title="Debug Test Note",
        content="Test content",
        tags=["debug", "test"],
        week_number=1,
    )

    created_note = note_service.create_note(test_user.id, note_data)
    print(f"Created note ID: {created_note.id}")
    print(f"Response tags: {created_note.tags}")

    # Check database directly
    db_note = test_session.query(Note).filter(Note.id == created_note.id).first()
    print(f"Database tags: {repr(db_note.tags)}")

    # Step 2: Test the update schema
    print("\n2. Testing update schema...")
    update_data = NoteUpdate(tags=[])
    dumped = update_data.model_dump(exclude_unset=True)
    print(f"Update schema dump: {dumped}")

    # Step 3: Perform the update
    print("\n3. Performing update...")
    updated_note = note_service.update_note(test_user.id, created_note.id, update_data)
    print(f"Update response tags: {updated_note.tags}")

    # Step 4: Check database after update
    print("\n4. Checking database after update...")
    test_session.refresh(db_note)  # Refresh from database
    print(f"Database tags after refresh: {repr(db_note.tags)}")

    # Step 5: Query fresh from database
    db_note_fresh = test_session.query(Note).filter(Note.id == created_note.id).first()
    print(f"Fresh query tags: {repr(db_note_fresh.tags)}")

    # Step 6: Test with explicit None
    print("\n5. Testing with explicit None...")
    update_data2 = NoteUpdate(tags=None)
    updated_note2 = note_service.update_note(
        test_user.id, created_note.id, update_data2
    )
    print(f"None update response tags: {updated_note2.tags}")

    # Check database again
    db_note_fresh2 = test_session.query(Note).filter(Note.id == created_note.id).first()
    print(f"Database after None update: {repr(db_note_fresh2.tags)}")

    print("\n=== End Debug Test ===")

    # Assert for test to pass/fail
    assert (
        db_note_fresh2.tags is None
    ), f"Expected None, got {repr(db_note_fresh2.tags)}"
