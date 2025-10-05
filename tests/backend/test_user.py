"""
Tests for User model, service, and API endpoints.
"""

from datetime import date, datetime

import pytest
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.base import Base
from app.models.user import User
from app.schemas.user import PasswordChange, UserCreate, UserUpdate
from app.services.user import UserService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestUserModel:
    """Test User SQLAlchemy model."""

    @pytest.fixture
    def test_engine(self):
        """Create a test database engine."""
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
        """Test basic User model creation."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
            full_name="Test User",
            date_of_birth=date(1990, 1, 1),
            lifespan=80,
            theme="light",
            font_size=14,
            is_active=True,
            is_verified=False,
            is_superuser=False,
            is_deleted=False,
        )

        test_session.add(user)
        test_session.commit()

        # Verify user was created
        retrieved_user = test_session.query(User).filter_by(username="testuser").first()
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.full_name == "Test User"
        assert retrieved_user.date_of_birth == date(1990, 1, 1)
        assert retrieved_user.lifespan == 80
        assert retrieved_user.theme == "light"
        assert retrieved_user.font_size == 14
        assert retrieved_user.is_active is True
        assert retrieved_user.is_verified is False
        assert retrieved_user.is_superuser is False
        assert retrieved_user.is_deleted is False
        assert retrieved_user.created_at is not None
        assert retrieved_user.updated_at is not None

    def test_user_model_defaults(self, test_session):
        """Test User model default values."""
        user = User(
            username="testuser2",
            email="test2@example.com",
            hashed_password="hashedpassword123",
        )

        test_session.add(user)
        test_session.commit()

        retrieved_user = (
            test_session.query(User).filter_by(username="testuser2").first()
        )
        assert retrieved_user.is_active is True
        assert retrieved_user.is_verified is False
        assert retrieved_user.is_superuser is False
        assert retrieved_user.is_deleted is False

    def test_user_unique_constraints(self, test_session):
        """Test unique constraints on username and email."""
        user1 = User(
            username="uniqueuser",
            email="unique@example.com",
            hashed_password="hashedpassword123",
        )
        test_session.add(user1)
        test_session.commit()

        # Try to create another user with same username
        user2 = User(
            username="uniqueuser",  # Same username
            email="different@example.com",
            hashed_password="hashedpassword123",
        )
        test_session.add(user2)

        with pytest.raises(Exception):  # Should raise integrity error
            test_session.commit()

    def test_user_soft_delete_fields(self, test_session):
        """Test soft delete functionality fields."""
        user = User(
            username="deleteuser",
            email="delete@example.com",
            hashed_password="hashedpassword123",
            is_deleted=True,
            deleted_at=datetime.utcnow(),
        )

        test_session.add(user)
        test_session.commit()

        retrieved_user = (
            test_session.query(User).filter_by(username="deleteuser").first()
        )
        assert retrieved_user.is_deleted is True
        assert retrieved_user.deleted_at is not None


class TestUserSchemas:
    """Test User Pydantic schemas and validation."""

    def test_user_create_schema_valid(self):
        """Test valid UserCreate schema."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="SecurePass123",
            full_name="Test User",
            date_of_birth=date(1990, 1, 1),
            lifespan=80,
            theme="light",
            font_size=14,
        )

        assert user_data.username == "testuser"
        assert user_data.email == "test@example.com"
        assert user_data.password == "SecurePass123"
        assert user_data.date_of_birth == date(1990, 1, 1)
        assert user_data.lifespan == 80
        assert user_data.theme == "light"
        assert user_data.font_size == 14

    def test_user_create_password_validation(self):
        """Test password validation in UserCreate schema."""
        # Test weak password
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="weak",  # Too short
                full_name="Test User",
            )

        # Test password without uppercase
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="lowercase123",  # No uppercase
                full_name="Test User",
            )

        # Test password without digit
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="NoDigitPass",  # No digit
                full_name="Test User",
            )

    def test_user_profile_date_validation(self):
        """Test date of birth validation."""
        # Test future date
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="ValidPass123",
                date_of_birth=date(2030, 1, 1),  # Future date
            )

        # Test very old date
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="ValidPass123",
                date_of_birth=date(1800, 1, 1),  # Too old
            )

    def test_user_profile_theme_validation(self):
        """Test theme validation."""
        # Valid themes
        valid_user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="ValidPass123",
            theme="dark",
        )
        assert valid_user.theme == "dark"

        # Invalid theme
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="ValidPass123",
                theme="invalid_theme",
            )

    def test_user_profile_lifespan_validation(self):
        """Test lifespan validation."""
        # Valid lifespan
        valid_user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="ValidPass123",
            lifespan=85,
        )
        assert valid_user.lifespan == 85

        # Invalid lifespan (too low)
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="ValidPass123",
                lifespan=0,
            )

        # Invalid lifespan (too high)
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="ValidPass123",
                lifespan=200,
            )

    def test_user_profile_font_size_validation(self):
        """Test font size validation."""
        # Valid font size
        valid_user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="ValidPass123",
            font_size=16,
        )
        assert valid_user.font_size == 16

        # Invalid font size (too small)
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="ValidPass123",
                font_size=5,
            )

        # Invalid font size (too large)
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="ValidPass123",
                font_size=100,
            )


class TestUserService:
    """Test UserService business logic."""

    @pytest.fixture
    def test_engine(self):
        """Create a test database engine."""
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

    def test_create_user_success(self, test_session):
        """Test successful user creation."""
        user_data = UserCreate(
            username="newuser",
            email="newuser@example.com",
            password="SecurePass123",
            full_name="New User",
            date_of_birth=date(1985, 5, 15),
            lifespan=80,
            theme="dark",
            font_size=16,
        )

        user = UserService.create_user(test_session, user_data)

        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"
        assert user.date_of_birth == date(1985, 5, 15)
        assert user.lifespan == 80
        assert user.theme == "dark"
        assert user.font_size == 16
        assert user.is_active is True
        assert user.is_verified is False
        assert user.is_deleted is False
        assert UserService.verify_password("SecurePass123", user.hashed_password)

    def test_create_user_duplicate_username(self, test_session):
        """Test creating user with duplicate username."""
        user_data1 = UserCreate(
            username="duplicate",
            email="user1@example.com",
            password="SecurePass123",
        )
        UserService.create_user(test_session, user_data1)

        user_data2 = UserCreate(
            username="duplicate",  # Same username
            email="user2@example.com",
            password="SecurePass123",
        )

        with pytest.raises(ConflictError):
            UserService.create_user(test_session, user_data2)

    def test_create_user_duplicate_email(self, test_session):
        """Test creating user with duplicate email."""
        user_data1 = UserCreate(
            username="user1",
            email="duplicate@example.com",
            password="SecurePass123",
        )
        UserService.create_user(test_session, user_data1)

        user_data2 = UserCreate(
            username="user2",
            email="duplicate@example.com",  # Same email
            password="SecurePass123",
        )

        with pytest.raises(ConflictError):
            UserService.create_user(test_session, user_data2)

    def test_get_user_by_id(self, test_session):
        """Test getting user by ID."""
        user_data = UserCreate(
            username="getuser",
            email="getuser@example.com",
            password="SecurePass123",
        )
        created_user = UserService.create_user(test_session, user_data)

        retrieved_user = UserService.get_user(test_session, created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == "getuser"

    def test_get_user_not_found(self, test_session):
        """Test getting non-existent user."""
        user = UserService.get_user(test_session, 999)
        assert user is None

    def test_update_user_success(self, test_session):
        """Test successful user update."""
        user_data = UserCreate(
            username="updateuser",
            email="updateuser@example.com",
            password="SecurePass123",
        )
        created_user = UserService.create_user(test_session, user_data)

        update_data = UserUpdate(
            full_name="Updated Name",
            theme="dark",
            font_size=18,
        )

        updated_user = UserService.update_user(
            test_session, created_user.id, update_data
        )

        assert updated_user.full_name == "Updated Name"
        assert updated_user.theme == "dark"
        assert updated_user.font_size == 18
        assert updated_user.username == "updateuser"  # Unchanged

    def test_update_user_not_found(self, test_session):
        """Test updating non-existent user."""
        update_data = UserUpdate(full_name="New Name")

        with pytest.raises(NotFoundError):
            UserService.update_user(test_session, 999, update_data)

    def test_soft_delete_user(self, test_session):
        """Test soft deleting a user."""
        user_data = UserCreate(
            username="deleteuser",
            email="deleteuser@example.com",
            password="SecurePass123",
        )
        created_user = UserService.create_user(test_session, user_data)

        deleted_user = UserService.soft_delete_user(test_session, created_user.id)

        assert deleted_user.is_deleted is True
        assert deleted_user.deleted_at is not None
        assert deleted_user.is_active is False

        # User should not be found in regular queries
        user = UserService.get_user(test_session, created_user.id)
        assert user is None

        # But should be found when including deleted
        user = UserService.get_user(test_session, created_user.id, include_deleted=True)
        assert user is not None

    def test_restore_user(self, test_session):
        """Test restoring a soft-deleted user."""
        user_data = UserCreate(
            username="restoreuser",
            email="restoreuser@example.com",
            password="SecurePass123",
        )
        created_user = UserService.create_user(test_session, user_data)

        # Soft delete the user
        UserService.soft_delete_user(test_session, created_user.id)

        # Restore the user
        restored_user = UserService.restore_user(test_session, created_user.id)

        assert restored_user.is_deleted is False
        assert restored_user.deleted_at is None
        assert restored_user.is_active is True

        # User should be found in regular queries
        user = UserService.get_user(test_session, created_user.id)
        assert user is not None

    def test_change_password_success(self, test_session):
        """Test successful password change."""
        user_data = UserCreate(
            username="changepass",
            email="changepass@example.com",
            password="OldPass123",
        )
        created_user = UserService.create_user(test_session, user_data)

        password_data = PasswordChange(
            current_password="OldPass123",
            new_password="NewPass456",
            confirm_password="NewPass456",
        )

        updated_user = UserService.change_password(
            test_session, created_user.id, password_data
        )

        # Old password should not work
        assert not UserService.verify_password(
            "OldPass123", updated_user.hashed_password
        )
        # New password should work
        assert UserService.verify_password("NewPass456", updated_user.hashed_password)

    def test_change_password_wrong_current(self, test_session):
        """Test password change with wrong current password."""
        user_data = UserCreate(
            username="changepass2",
            email="changepass2@example.com",
            password="CurrentPass123",
        )
        created_user = UserService.create_user(test_session, user_data)

        password_data = PasswordChange(
            current_password="WrongPass123",  # Wrong current password
            new_password="NewPass456",
            confirm_password="NewPass456",
        )

        with pytest.raises(ValidationError):
            UserService.change_password(test_session, created_user.id, password_data)

    def test_get_users_with_filtering(self, test_session):
        """Test getting users with various filters."""
        # Create test users
        users_data = [
            UserCreate(
                username="active1", email="active1@example.com", password="Pass123456"
            ),
            UserCreate(
                username="active2", email="active2@example.com", password="Pass123456"
            ),
            UserCreate(
                username="inactive", email="inactive@example.com", password="Pass123456"
            ),
        ]

        created_users = []
        for user_data in users_data:
            user = UserService.create_user(test_session, user_data)
            created_users.append(user)

        # Deactivate one user
        UserService.deactivate_user(test_session, created_users[2].id)

        # Test filtering by active status
        active_users = UserService.get_users(test_session, is_active=True)
        assert len(active_users) == 2

        inactive_users = UserService.get_users(test_session, is_active=False)
        assert len(inactive_users) == 1

        # Test search functionality
        search_results = UserService.get_users(test_session, search="active")
        assert len(search_results) == 2

    def test_user_count(self, test_session):
        """Test user count functionality."""
        initial_count = UserService.get_user_count(test_session)

        # Create users
        for i in range(3):
            user_data = UserCreate(
                username=f"countuser{i}",
                email=f"countuser{i}@example.com",
                password="Pass123456",
            )
            UserService.create_user(test_session, user_data)

        total_count = UserService.get_user_count(test_session)
        assert total_count == initial_count + 3

        active_count = UserService.get_user_count(test_session, is_active=True)
        assert active_count == initial_count + 3


class TestUserAPI:
    """Test User API endpoints."""

    @pytest.fixture
    def test_engine(self):
        """Create a test database engine."""
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

    def test_create_user_endpoint(self, client):
        """Test user creation endpoint."""
        user_data = {
            "username": "apiuser",
            "email": "apiuser@example.com",
            "password": "SecurePass123",
            "full_name": "API User",
            "date_of_birth": "1990-01-01",
            "lifespan": 80,
            "theme": "light",
            "font_size": 14,
        }

        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201

        response_data = response.json()
        assert response_data["username"] == "apiuser"
        assert response_data["email"] == "apiuser@example.com"
        assert response_data["full_name"] == "API User"
        assert "id" in response_data
        assert "hashed_password" not in response_data  # Should not be exposed

    def test_create_user_duplicate_username(self, client):
        """Test creating user with duplicate username via API."""
        user_data = {
            "username": "duplicate",
            "email": "user1@example.com",
            "password": "SecurePass123",
        }

        # Create first user
        response1 = client.post("/api/v1/users/", json=user_data)
        assert response1.status_code == 201

        # Try to create second user with same username
        user_data["email"] = "user2@example.com"
        response2 = client.post("/api/v1/users/", json=user_data)
        assert response2.status_code == 409

    def test_get_users_endpoint(self, client):
        """Test get users endpoint."""
        # Create test users
        for i in range(3):
            user_data = {
                "username": f"listuser{i}",
                "email": f"listuser{i}@example.com",
                "password": "SecurePass123",
            }
            client.post("/api/v1/users/", json=user_data)

        response = client.get("/api/v1/users/")
        assert response.status_code == 200

        users = response.json()
        assert len(users) >= 3  # At least the 3 we created

    def test_get_user_by_id_endpoint(self, client):
        """Test get user by ID endpoint."""
        # Create a user
        user_data = {
            "username": "getbyid",
            "email": "getbyid@example.com",
            "password": "SecurePass123",
        }

        create_response = client.post("/api/v1/users/", json=user_data)
        created_user = create_response.json()
        user_id = created_user["id"]

        # Get user by ID
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200

        user_data = response.json()
        assert user_data["id"] == user_id
        assert user_data["username"] == "getbyid"

    def test_get_user_not_found(self, client):
        """Test get non-existent user."""
        response = client.get("/api/v1/users/999")
        assert response.status_code == 404

    def test_update_user_endpoint(self, client):
        """Test user update endpoint."""
        # Create a user
        user_data = {
            "username": "updateapi",
            "email": "updateapi@example.com",
            "password": "SecurePass123",
        }

        create_response = client.post("/api/v1/users/", json=user_data)
        created_user = create_response.json()
        user_id = created_user["id"]

        # Update user
        update_data = {
            "full_name": "Updated Name",
            "theme": "dark",
        }

        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert response.status_code == 200

        updated_user = response.json()
        assert updated_user["full_name"] == "Updated Name"
        assert updated_user["theme"] == "dark"

    def test_soft_delete_user_endpoint(self, client):
        """Test soft delete user endpoint."""
        # Create a user
        user_data = {
            "username": "deleteapi",
            "email": "deleteapi@example.com",
            "password": "SecurePass123",
        }

        create_response = client.post("/api/v1/users/", json=user_data)
        created_user = create_response.json()
        user_id = created_user["id"]

        # Soft delete user
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 200

        deleted_user = response.json()
        assert deleted_user["is_deleted"] is True

        # User should not be found in regular get
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404

    def test_user_stats_endpoint(self, client):
        """Test user stats endpoint."""
        response = client.get("/api/v1/users/stats/summary")
        assert response.status_code == 200

        stats = response.json()
        assert "total_users" in stats
        assert "active_users" in stats
        assert "inactive_users" in stats
        assert "deleted_users" in stats
        assert isinstance(stats["total_users"], int)
