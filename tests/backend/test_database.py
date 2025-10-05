"""
Tests for database connection, models, and session management.
"""

import os
import tempfile
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from app.core.config import Settings
from app.core.database import (
    configure_sqlite_encryption,
    create_tables,
    drop_tables,
    get_database_info,
    get_database_url,
    get_db,
    verify_database_connection,
)
from app.models.base import Base
from app.models.note import Note
from app.models.user import User
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class TestDatabaseConnection:
    """Test database connection and configuration."""

    def test_get_database_url_without_encryption(self):
        """Test database URL generation without encryption."""
        test_settings = Settings(
            database_url="sqlite:///./test.db", database_encrypt=False
        )

        with patch("app.core.database.settings", test_settings):
            url = get_database_url()
            assert url == "sqlite:///./test.db"

    def test_get_database_url_with_encryption_no_pysqlcipher(self):
        """Test database URL fallback when SQLCipher is not available."""
        test_settings = Settings(
            database_url="sqlite:///./test.db",
            database_encrypt=True,
            database_key="test-key",
        )

        with patch("app.core.database.settings", test_settings):
            # This should fall back to regular SQLite since pysqlcipher3 is not available
            url = get_database_url()
            assert url == "sqlite:///./test.db"

    def test_database_info(self):
        """Test database information gathering."""
        test_settings = Settings(
            database_url="sqlite:///./test.db",
            database_encrypt=True,
            database_key="test-key",
            database_echo=True,
            database_pool_size=5,
            database_max_overflow=10,
        )

        with patch("app.core.database.settings", test_settings):
            info = get_database_info()
            assert info["encryption_enabled"] is True
            assert info["echo_queries"] is True
            assert info["pool_size"] == 5
            assert info["max_overflow"] == 10
            # Key should be masked or encryption should be indicated
            assert (
                "***" in info["database_url"]
                or "encryption requested" in info["database_url"]
            )

    def test_verify_database_connection(self):
        """Test database connection verification."""
        # Create a temporary database for testing
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            test_db_path = tmp.name

        try:
            test_settings = Settings(
                database_url=f"sqlite:///{test_db_path}", database_encrypt=False
            )

            with patch("app.core.database.settings", test_settings):
                # Create engine for this test
                engine = create_engine(test_settings.database_url)

                with patch("app.core.database.engine", engine):
                    assert verify_database_connection() is True

                # Properly dispose of the engine
                engine.dispose()
        finally:
            # Clean up
            if os.path.exists(test_db_path):
                try:
                    os.unlink(test_db_path)
                except PermissionError:
                    # On Windows, sometimes we need to wait a bit
                    import time

                    time.sleep(0.1)
                    try:
                        os.unlink(test_db_path)
                    except PermissionError:
                        pass  # File will be cleaned up by OS eventually

    def test_sqlite_encryption_configuration(self):
        """Test SQLite encryption configuration (should handle gracefully)."""

        # Create a mock connection
        class MockConnection:
            def cursor(self):
                return MockCursor()

        class MockCursor:
            def execute(self, query):
                if "PRAGMA key" in query:
                    # Simulate SQLCipher not being available
                    raise Exception("no such function: key")
                return None

            def fetchone(self):
                return (0,)

            def close(self):
                pass

        test_settings = Settings(database_encrypt=True, database_key="test-key")

        with patch("app.core.database.settings", test_settings):
            # This should not raise an exception, just log a warning
            configure_sqlite_encryption(MockConnection(), None)


class TestDatabaseModels:
    """Test database models and relationships."""

    @pytest.fixture
    def test_engine(self):
        """Create a test database engine."""
        # Create in-memory SQLite database for testing
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def test_session(self, test_engine):
        """Create a test database session."""
        session_class = sessionmaker(bind=test_engine)
        session = session_class()
        yield session
        session.close()

    def test_user_model_creation(self, test_session):
        """Test User model creation and basic operations."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
            full_name="Test User",
            is_active=True,
            is_verified=False,
            is_superuser=False,
        )

        test_session.add(user)
        test_session.commit()

        # Verify user was created
        retrieved_user = test_session.query(User).filter_by(username="testuser").first()
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.is_active is True
        assert retrieved_user.created_at is not None
        assert retrieved_user.updated_at is not None

    def test_note_model_creation(self, test_session):
        """Test Note model creation and basic operations."""
        # First create a user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
        )
        test_session.add(user)
        test_session.commit()

        # Create a note
        note = Note(
            title="Test Note",
            content="This is test content for the note.",
            owner_id=user.id,
            category="test",
            is_favorite=False,
            is_archived=False,
            is_deleted=False,
        )

        test_session.add(note)
        test_session.commit()

        # Verify note was created
        retrieved_note = test_session.query(Note).filter_by(title="Test Note").first()
        assert retrieved_note is not None
        assert retrieved_note.content == "This is test content for the note."
        assert retrieved_note.owner_id == user.id
        assert retrieved_note.created_at is not None

    def test_user_note_relationship(self, test_session):
        """Test the relationship between User and Note models."""
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
        )
        test_session.add(user)
        test_session.commit()

        # Create multiple notes for the user
        note1 = Note(title="Note 1", content="Content 1", owner_id=user.id)
        note2 = Note(title="Note 2", content="Content 2", owner_id=user.id)

        test_session.add_all([note1, note2])
        test_session.commit()

        # Test forward relationship (user -> notes)
        retrieved_user = test_session.query(User).filter_by(username="testuser").first()
        assert len(retrieved_user.notes) == 2
        note_titles = [note.title for note in retrieved_user.notes]
        assert "Note 1" in note_titles
        assert "Note 2" in note_titles

        # Test backward relationship (note -> user)
        retrieved_note = test_session.query(Note).filter_by(title="Note 1").first()
        assert retrieved_note.owner.username == "testuser"

    def test_user_unique_constraints(self, test_session):
        """Test unique constraints on User model."""
        user1 = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
        )
        test_session.add(user1)
        test_session.commit()

        # Try to create another user with same username
        user2 = User(
            username="testuser",  # Same username
            email="different@example.com",
            hashed_password="hashed_password_here",
        )
        test_session.add(user2)

        with pytest.raises(Exception):  # Should raise integrity error
            test_session.commit()

    def test_note_cascade_delete(self, test_session):
        """Test cascade delete when user is deleted."""
        # Create user and note
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
        )
        test_session.add(user)
        test_session.commit()

        note = Note(title="Test Note", content="Test content", owner_id=user.id)
        test_session.add(note)
        test_session.commit()

        # Verify note exists
        assert test_session.query(Note).count() == 1

        # Delete user
        test_session.delete(user)
        test_session.commit()

        # Note should be deleted due to cascade
        assert test_session.query(Note).count() == 0

    def test_note_soft_delete(self, test_session):
        """Test soft delete functionality for notes."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
        )
        test_session.add(user)
        test_session.commit()

        note = Note(
            title="Test Note",
            content="Test content",
            owner_id=user.id,
            is_deleted=False,
        )
        test_session.add(note)
        test_session.commit()

        # Soft delete the note
        note.is_deleted = True
        note.deleted_at = datetime.now(timezone.utc)
        test_session.commit()

        # Note should still exist in database but marked as deleted
        retrieved_note = test_session.query(Note).filter_by(title="Test Note").first()
        assert retrieved_note is not None
        assert retrieved_note.is_deleted is True
        assert retrieved_note.deleted_at is not None


class TestDatabaseOperations:
    """Test database operations and table management."""

    def test_create_and_drop_tables(self):
        """Test table creation and dropping."""
        # Create a temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            test_db_path = tmp.name

        try:
            test_settings = Settings(
                database_url=f"sqlite:///{test_db_path}", database_encrypt=False
            )

            with patch("app.core.database.settings", test_settings):
                # Create engine for this test
                engine = create_engine(test_settings.database_url)

                with patch("app.core.database.engine", engine):
                    # Test table creation
                    create_tables()

                    # Verify tables exist
                    from sqlalchemy import inspect

                    inspector = inspect(engine)
                    tables = inspector.get_table_names()
                    assert "users" in tables
                    assert "notes" in tables

                    # Test table dropping
                    drop_tables()

                    # Verify tables are gone
                    inspector = inspect(engine)
                    tables = inspector.get_table_names()
                    assert len(tables) == 0

                # Properly dispose of the engine
                engine.dispose()
        finally:
            # Clean up
            if os.path.exists(test_db_path):
                try:
                    os.unlink(test_db_path)
                except PermissionError:
                    # On Windows, sometimes we need to wait a bit
                    import time

                    time.sleep(0.1)
                    try:
                        os.unlink(test_db_path)
                    except PermissionError:
                        pass  # File will be cleaned up by OS eventually

    def test_session_management(self):
        """Test database session management."""
        # Create a temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            test_db_path = tmp.name

        try:
            test_settings = Settings(
                database_url=f"sqlite:///{test_db_path}", database_encrypt=False
            )

            with patch("app.core.database.settings", test_settings):
                # Create engine and session for this test
                engine = create_engine(test_settings.database_url)
                session_local = sessionmaker(bind=engine)

                with patch("app.core.database.engine", engine), patch(
                    "app.core.database.SessionLocal", session_local
                ):
                    # Create tables
                    Base.metadata.create_all(engine)

                    # Test get_db generator
                    session_gen = get_db()
                    session = next(session_gen)

                    # Use the session
                    result = session.execute(text("SELECT 1")).scalar()
                    assert result == 1

                    # Close the session
                    try:
                        next(session_gen)
                    except StopIteration:
                        pass  # Expected behavior for generator cleanup

                # Properly dispose of the engine
                engine.dispose()
        finally:
            # Clean up
            if os.path.exists(test_db_path):
                try:
                    os.unlink(test_db_path)
                except PermissionError:
                    # On Windows, sometimes we need to wait a bit
                    import time

                    time.sleep(0.1)
                    try:
                        os.unlink(test_db_path)
                    except PermissionError:
                        pass  # File will be cleaned up by OS eventually
