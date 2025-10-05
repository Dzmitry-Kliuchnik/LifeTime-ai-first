"""
User service layer for business logic and CRUD operations.
"""

import logging
from datetime import datetime
from typing import List, Optional

from passlib.context import CryptContext
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.models.user import User
from app.schemas.user import (
    PasswordChange,
    UserCreate,
    UserProfileUpdate,
    UserUpdate,
)

logger = logging.getLogger(__name__)

# Password hashing configuration
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__rounds=4,
)


class UserService:
    """Service class for user-related business logic and database operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password."""
        # Truncate password to 72 bytes to avoid bcrypt limitation
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            password = password_bytes.decode("utf-8", errors="ignore")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user with validation.

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            Created user instance

        Raises:
            ConflictError: If username or email already exists
            ValidationError: If data validation fails
        """
        try:
            # Check if username already exists
            existing_user = (
                db.query(User)
                .filter(
                    and_(User.username == user_data.username, User.is_deleted == False)
                )
                .first()
            )

            if existing_user:
                raise ConflictError(f"Username '{user_data.username}' already exists")

            # Check if email already exists
            existing_email = (
                db.query(User)
                .filter(and_(User.email == user_data.email, User.is_deleted == False))
                .first()
            )

            if existing_email:
                raise ConflictError(f"Email '{user_data.email}' already exists")

            # Hash the password
            hashed_password = UserService.hash_password(user_data.password)

            # Create user instance
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                bio=user_data.bio,
                date_of_birth=user_data.date_of_birth,
                lifespan=user_data.lifespan or 80,  # Default lifespan
                theme=user_data.theme or "light",  # Default theme
                font_size=user_data.font_size or 14,  # Default font size
                is_active=True,
                is_verified=False,
                is_superuser=False,
                is_deleted=False,
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            logger.info(f"Created new user: {db_user.username} ({db_user.id})")
            return db_user

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error creating user: {e}")
            if "username" in str(e):
                raise ConflictError("Username already exists")
            elif "email" in str(e):
                raise ConflictError("Email already exists")
            else:
                raise ValidationError("Data integrity constraint violated")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise

    @staticmethod
    def get_user(
        db: Session, user_id: int, include_deleted: bool = False
    ) -> Optional[User]:
        """
        Get user by ID.

        Args:
            db: Database session
            user_id: User ID
            include_deleted: Whether to include soft-deleted users

        Returns:
            User instance or None if not found
        """
        query = db.query(User).filter(User.id == user_id)

        if not include_deleted:
            query = query.filter(User.is_deleted == False)

        return query.first()

    @staticmethod
    def get_user_by_username(
        db: Session, username: str, include_deleted: bool = False
    ) -> Optional[User]:
        """
        Get user by username.

        Args:
            db: Database session
            username: Username to search for
            include_deleted: Whether to include soft-deleted users

        Returns:
            User instance or None if not found
        """
        query = db.query(User).filter(User.username == username)

        if not include_deleted:
            query = query.filter(User.is_deleted == False)

        return query.first()

    @staticmethod
    def get_user_by_email(
        db: Session, email: str, include_deleted: bool = False
    ) -> Optional[User]:
        """
        Get user by email.

        Args:
            db: Database session
            email: Email to search for
            include_deleted: Whether to include soft-deleted users

        Returns:
            User instance or None if not found
        """
        query = db.query(User).filter(User.email == email)

        if not include_deleted:
            query = query.filter(User.is_deleted == False)

        return query.first()

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[User]:
        """
        Get users with optional filtering and pagination.

        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted users
            search: Search term for username, email, or full_name
            is_active: Filter by active status

        Returns:
            List of user instances
        """
        query = db.query(User)

        if not include_deleted:
            query = query.filter(User.is_deleted == False)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

            # If searching without explicit is_active filter, default to active users only
            # This ensures search results don't include inactive users unless explicitly requested
            if is_active is None:
                query = query.filter(User.is_active)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """
        Update user information.

        Args:
            db: Database session
            user_id: User ID to update
            user_data: Updated user data

        Returns:
            Updated user instance

        Raises:
            NotFoundError: If user not found
            ConflictError: If username or email conflicts
        """
        user = UserService.get_user(db, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        try:
            # Check for username conflicts (if username is being updated)
            if user_data.username and user_data.username != user.username:
                existing_user = (
                    db.query(User)
                    .filter(
                        and_(
                            User.username == user_data.username,
                            User.id != user_id,
                            User.is_deleted == False,
                        )
                    )
                    .first()
                )

                if existing_user:
                    raise ConflictError(
                        f"Username '{user_data.username}' already exists"
                    )

            # Check for email conflicts (if email is being updated)
            if user_data.email and user_data.email != user.email:
                existing_email = (
                    db.query(User)
                    .filter(
                        and_(
                            User.email == user_data.email,
                            User.id != user_id,
                            User.is_deleted == False,
                        )
                    )
                    .first()
                )

                if existing_email:
                    raise ConflictError(f"Email '{user_data.email}' already exists")

            # Update user fields
            update_data = user_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)

            db.commit()
            db.refresh(user)

            logger.info(f"Updated user: {user.username} ({user.id})")
            return user

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error updating user: {e}")
            if "username" in str(e):
                raise ConflictError("Username already exists")
            elif "email" in str(e):
                raise ConflictError("Email already exists")
            else:
                raise ValidationError("Data integrity constraint violated")
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user: {e}")
            raise

    @staticmethod
    def update_user_profile(
        db: Session, user_id: int, profile_data: UserProfileUpdate
    ) -> User:
        """
        Update user profile settings only.

        Args:
            db: Database session
            user_id: User ID to update
            profile_data: Updated profile data

        Returns:
            Updated user instance

        Raises:
            NotFoundError: If user not found
        """
        user = UserService.get_user(db, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        try:
            # Update profile fields
            update_data = profile_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)

            db.commit()
            db.refresh(user)

            logger.info(f"Updated user profile: {user.username} ({user.id})")
            return user

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user profile: {e}")
            raise

    @staticmethod
    def change_password(
        db: Session, user_id: int, password_data: PasswordChange
    ) -> User:
        """
        Change user password.

        Args:
            db: Database session
            user_id: User ID
            password_data: Password change data

        Returns:
            Updated user instance

        Raises:
            NotFoundError: If user not found
            ValidationError: If current password is incorrect
        """
        user = UserService.get_user(db, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        # Verify current password
        if not UserService.verify_password(
            password_data.current_password, user.hashed_password
        ):
            raise ValidationError("Current password is incorrect")

        # Verify password confirmation
        if password_data.new_password != password_data.confirm_password:
            raise ValidationError("New passwords do not match")

        try:
            # Hash and update password
            user.hashed_password = UserService.hash_password(password_data.new_password)

            db.commit()
            db.refresh(user)

            logger.info(f"Changed password for user: {user.username} ({user.id})")
            return user

        except Exception as e:
            db.rollback()
            logger.error(f"Error changing password: {e}")
            raise

    @staticmethod
    def soft_delete_user(db: Session, user_id: int) -> User:
        """
        Soft delete a user (mark as deleted without removing from database).

        Args:
            db: Database session
            user_id: User ID to delete

        Returns:
            Soft-deleted user instance

        Raises:
            NotFoundError: If user not found
        """
        user = UserService.get_user(db, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        try:
            user.is_deleted = True
            user.deleted_at = datetime.utcnow()
            user.is_active = False  # Also deactivate the user

            db.commit()
            db.refresh(user)

            logger.info(f"Soft deleted user: {user.username} ({user.id})")
            return user

        except Exception as e:
            db.rollback()
            logger.error(f"Error soft deleting user: {e}")
            raise

    @staticmethod
    def restore_user(db: Session, user_id: int) -> User:
        """
        Restore a soft-deleted user.

        Args:
            db: Database session
            user_id: User ID to restore

        Returns:
            Restored user instance

        Raises:
            NotFoundError: If user not found
        """
        user = UserService.get_user(db, user_id, include_deleted=True)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        if not user.is_deleted:
            raise ValidationError("User is not deleted")

        try:
            user.is_deleted = False
            user.deleted_at = None
            user.is_active = True  # Reactivate the user

            db.commit()
            db.refresh(user)

            logger.info(f"Restored user: {user.username} ({user.id})")
            return user

        except Exception as e:
            db.rollback()
            logger.error(f"Error restoring user: {e}")
            raise

    @staticmethod
    def hard_delete_user(db: Session, user_id: int) -> bool:
        """
        Permanently delete a user from the database.
        WARNING: This operation cannot be undone!

        Args:
            db: Database session
            user_id: User ID to delete

        Returns:
            True if deletion was successful

        Raises:
            NotFoundError: If user not found
        """
        user = UserService.get_user(db, user_id, include_deleted=True)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        try:
            username = user.username
            db.delete(user)
            db.commit()

            logger.warning(f"Hard deleted user: {username} ({user_id})")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error hard deleting user: {e}")
            raise

    @staticmethod
    def activate_user(db: Session, user_id: int) -> User:
        """
        Activate a user account.

        Args:
            db: Database session
            user_id: User ID to activate

        Returns:
            Activated user instance

        Raises:
            NotFoundError: If user not found
        """
        user = UserService.get_user(db, user_id, include_deleted=True)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        try:
            user.is_active = True

            db.commit()
            db.refresh(user)

            logger.info(f"Activated user: {user.username} ({user.id})")
            return user

        except Exception as e:
            db.rollback()
            logger.error(f"Error activating user: {e}")
            raise

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> User:
        """
        Deactivate a user account.

        Args:
            db: Database session
            user_id: User ID to deactivate

        Returns:
            Deactivated user instance

        Raises:
            NotFoundError: If user not found
        """
        user = UserService.get_user(db, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        try:
            user.is_active = False

            db.commit()
            db.refresh(user)

            logger.info(f"Deactivated user: {user.username} ({user.id})")
            return user

        except Exception as e:
            db.rollback()
            logger.error(f"Error deactivating user: {e}")
            raise

    @staticmethod
    def update_last_login(db: Session, user_id: int) -> User:
        """
        Update user's last login timestamp.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Updated user instance

        Raises:
            NotFoundError: If user not found
        """
        user = UserService.get_user(db, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        try:
            user.last_login = datetime.utcnow()

            db.commit()
            db.refresh(user)

            logger.debug(f"Updated last login for user: {user.username} ({user.id})")
            return user

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating last login: {e}")
            raise

    @staticmethod
    def get_user_count(
        db: Session, include_deleted: bool = False, is_active: Optional[bool] = None
    ) -> int:
        """
        Get total count of users.

        Args:
            db: Database session
            include_deleted: Whether to include soft-deleted users
            is_active: Filter by active status

        Returns:
            Total user count
        """
        query = db.query(User)

        if not include_deleted:
            query = query.filter(User.is_deleted == False)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.count()
