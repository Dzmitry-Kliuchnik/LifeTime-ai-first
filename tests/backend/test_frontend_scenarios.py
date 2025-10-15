"""
Test various frontend scenarios that might cause tag deletion issues.
"""

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.note import NoteService


def test_frontend_scenarios(test_session, test_user):
    """Test scenarios that frontend might send."""

    note_service = NoteService(test_session)

    print("=== Testing Frontend Scenarios ===")

    # Scenario 1: Frontend sends { tags: [] } in JSON
    print("\n1. Testing JSON with empty array...")
    note1 = note_service.create_note(
        test_user.id,
        NoteCreate(title="JSON Test", content="Test", tags=["original"], week_number=1),
    )

    # Simulate what frontend might send
    json_data = {"tags": []}  # Empty array from frontend
    update_schema = NoteUpdate(**json_data)
    print(f"Schema from JSON: tags = {update_schema.tags}")
    print(f"Model dump: {update_schema.model_dump(exclude_unset=True)}")

    note_service.update_note(test_user.id, note1.id, update_schema)
    db_note1 = test_session.query(Note).filter(Note.id == note1.id).first()
    print(f"Result in DB: {repr(db_note1.tags)}")
    assert db_note1.tags is None

    # Scenario 2: Frontend sends { tags: "" } in JSON
    print("\n2. Testing JSON with empty string...")
    note2 = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="String Test", content="Test", tags=["original"], week_number=1
        ),
    )

    json_data2 = {"tags": ""}
    update_schema2 = NoteUpdate(**json_data2)
    print(f"Schema from JSON: tags = {repr(update_schema2.tags)}")
    print(f"Model dump: {update_schema2.model_dump(exclude_unset=True)}")

    note_service.update_note(test_user.id, note2.id, update_schema2)
    db_note2 = test_session.query(Note).filter(Note.id == note2.id).first()
    print(f"Result in DB: {repr(db_note2.tags)}")
    assert db_note2.tags is None

    # Scenario 3: Partial update without tags field
    print("\n3. Testing partial update without tags...")
    note3 = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Partial Test",
            content="Test",
            tags=["should", "remain"],
            week_number=1,
        ),
    )

    json_data3 = {"title": "Updated Title"}  # No tags field
    update_schema3 = NoteUpdate(**json_data3)
    print(f"Schema from JSON: tags = {getattr(update_schema3, 'tags', 'NOT_SET')}")
    print(f"Model dump: {update_schema3.model_dump(exclude_unset=True)}")

    note_service.update_note(test_user.id, note3.id, update_schema3)
    db_note3 = test_session.query(Note).filter(Note.id == note3.id).first()
    print(f"Result in DB: {repr(db_note3.tags)}")
    # Tags should remain unchanged
    assert "should" in db_note3.tags and "remain" in db_note3.tags

    # Scenario 4: Mixed update with title and empty tags
    print("\n4. Testing mixed update with empty tags...")
    note4 = note_service.create_note(
        test_user.id,
        NoteCreate(
            title="Mixed Test", content="Test", tags=["remove", "these"], week_number=1
        ),
    )

    json_data4 = {"title": "New Title", "tags": []}
    update_schema4 = NoteUpdate(**json_data4)
    print(f"Schema from JSON: tags = {update_schema4.tags}")
    print(f"Model dump: {update_schema4.model_dump(exclude_unset=True)}")

    note_service.update_note(test_user.id, note4.id, update_schema4)
    db_note4 = test_session.query(Note).filter(Note.id == note4.id).first()
    print(f"Result in DB: tags = {repr(db_note4.tags)}, title = {db_note4.title}")
    assert db_note4.tags is None
    assert db_note4.title == "New Title"

    print("\n=== All scenarios passed! ===")


def test_potential_edge_cases(test_session, test_user):
    """Test potential edge cases that might cause issues."""

    note_service = NoteService(test_session)

    print("=== Testing Edge Cases ===")

    # Edge case 1: What if tags field is explicitly set but with None?
    print("\n1. Testing explicit None in update...")
    note = note_service.create_note(
        test_user.id,
        NoteCreate(title="Edge Test", content="Test", tags=["edge"], week_number=1),
    )

    # Create update with explicit None - this should be included in model_dump
    update_data = NoteUpdate(tags=None)
    dumped = update_data.model_dump(exclude_unset=True)
    print(f"Explicit None dump: {dumped}")

    # This should include tags field
    assert "tags" in dumped
    assert dumped["tags"] is None

    note_service.update_note(test_user.id, note.id, update_data)
    db_note = test_session.query(Note).filter(Note.id == note.id).first()
    print(f"Result: {repr(db_note.tags)}")
    assert db_note.tags is None

    print("\n=== Edge cases passed! ===")
