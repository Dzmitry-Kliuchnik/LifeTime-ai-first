"""
User repository for database abstraction and complex queries.
"""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repository class for User model database operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create(self, user_data: Dict) -> User:
        """
        Create a new user record.

        Args:
            user_data: Dictionary containing user data

        Returns:
            Created user instance
        """
        user = User(**user_data)
        self.db.add(user)
        self.db.flush()  # Get the ID without committing
        return user

    def get_by_id(self, user_id: int, include_deleted: bool = False) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID
            include_deleted: Whether to include soft-deleted users

        Returns:
            User instance or None
        """
        query = self.db.query(User).filter(User.id == user_id)

        if not include_deleted:
            query = query.filter(~User.is_deleted)

        return query.first()

    def get_by_username(
        self, username: str, include_deleted: bool = False
    ) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username to search for
            include_deleted: Whether to include soft-deleted users

        Returns:
            User instance or None
        """
        query = self.db.query(User).filter(User.username == username)

        if not include_deleted:
            query = query.filter(~User.is_deleted)

        return query.first()

    def get_by_email(self, email: str, include_deleted: bool = False) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: Email to search for
            include_deleted: Whether to include soft-deleted users

        Returns:
            User instance or None
        """
        query = self.db.query(User).filter(User.email == email)

        if not include_deleted:
            query = query.filter(~User.is_deleted)

        return query.first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        order_by: str = "created_at",
        order_desc: bool = False,
    ) -> List[User]:
        """
        Get users with filtering, searching, and pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted users
            search: Search term for username, email, or full_name
            is_active: Filter by active status
            is_verified: Filter by verification status
            is_superuser: Filter by superuser status
            order_by: Field to order by
            order_desc: Whether to order in descending order

        Returns:
            List of user instances
        """
        query = self.db.query(User)

        # Apply filters
        if not include_deleted:
            query = query.filter(~User.is_deleted)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if is_verified is not None:
            query = query.filter(User.is_verified == is_verified)

        if is_superuser is not None:
            query = query.filter(User.is_superuser == is_superuser)

        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        # Apply ordering
        if hasattr(User, order_by):
            order_column = getattr(User, order_by)
            if order_desc:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column)

        return query.offset(skip).limit(limit).all()

    def count(
        self,
        include_deleted: bool = False,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
    ) -> int:
        """
        Count users with optional filtering.

        Args:
            include_deleted: Whether to include soft-deleted users
            search: Search term for username, email, or full_name
            is_active: Filter by active status
            is_verified: Filter by verification status
            is_superuser: Filter by superuser status

        Returns:
            Total count of matching users
        """
        query = self.db.query(User)

        # Apply filters
        if not include_deleted:
            query = query.filter(~User.is_deleted)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if is_verified is not None:
            query = query.filter(User.is_verified == is_verified)

        if is_superuser is not None:
            query = query.filter(User.is_superuser == is_superuser)

        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return query.count()

    def update(self, user: User, update_data: Dict) -> User:
        """
        Update user with provided data.

        Args:
            user: User instance to update
            update_data: Dictionary containing update data

        Returns:
            Updated user instance
        """
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        self.db.flush()
        return user

    def delete(self, user: User) -> None:
        """
        Hard delete user from database.

        Args:
            user: User instance to delete
        """
        self.db.delete(user)
        self.db.flush()

    def soft_delete(self, user: User) -> User:
        """
        Soft delete user (mark as deleted).

        Args:
            user: User instance to soft delete

        Returns:
            Soft-deleted user instance
        """
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()
        user.is_active = False
        self.db.flush()
        return user

    def restore(self, user: User) -> User:
        """
        Restore soft-deleted user.

        Args:
            user: User instance to restore

        Returns:
            Restored user instance
        """
        user.is_deleted = False
        user.deleted_at = None
        user.is_active = True
        self.db.flush()
        return user

    def exists_by_username(
        self, username: str, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Check if username exists.

        Args:
            username: Username to check
            exclude_id: User ID to exclude from check (for updates)

        Returns:
            True if username exists, False otherwise
        """
        query = self.db.query(User).filter(
            and_(User.username == username, ~User.is_deleted)
        )

        if exclude_id:
            query = query.filter(User.id != exclude_id)

        return query.first() is not None

    def exists_by_email(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if email exists.

        Args:
            email: Email to check
            exclude_id: User ID to exclude from check (for updates)

        Returns:
            True if email exists, False otherwise
        """
        query = self.db.query(User).filter(and_(User.email == email, ~User.is_deleted))

        if exclude_id:
            query = query.filter(User.id != exclude_id)

        return query.first() is not None

    def get_user_stats(self) -> Dict[str, int]:
        """
        Get user statistics.

        Returns:
            Dictionary with user statistics
        """
        total_users = self.db.query(User).filter(~User.is_deleted).count()
        active_users = (
            self.db.query(User)
            .filter(and_(~User.is_deleted, User.is_active == True))
            .count()
        )
        verified_users = (
            self.db.query(User)
            .filter(and_(~User.is_deleted, User.is_verified == True))
            .count()
        )
        superusers = (
            self.db.query(User)
            .filter(and_(~User.is_deleted, User.is_superuser == True))
            .count()
        )
        deleted_users = self.db.query(User).filter(User.is_deleted == True).count()

        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "superusers": superusers,
            "deleted_users": deleted_users,
        }

    def get_users_by_theme(self, theme: str) -> List[User]:
        """
        Get users by theme preference.

        Args:
            theme: Theme to filter by

        Returns:
            List of users with specified theme
        """
        return (
            self.db.query(User)
            .filter(and_(~User.is_deleted, User.theme == theme))
            .all()
        )

    def get_users_with_recent_activity(self, days: int = 30) -> List[User]:
        """
        Get users with recent login activity.

        Args:
            days: Number of days to look back

        Returns:
            List of users with recent activity
        """
        cutoff_date = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)

        return (
            self.db.query(User)
            .filter(and_(~User.is_deleted, User.last_login >= cutoff_date))
            .all()
        )

    def get_users_by_age_range(
        self, min_age: Optional[int] = None, max_age: Optional[int] = None
    ) -> List[User]:
        """
        Get users by age range (requires date_of_birth).

        Args:
            min_age: Minimum age
            max_age: Maximum age

        Returns:
            List of users in age range
        """
        query = self.db.query(User).filter(
            and_(~User.is_deleted, User.date_of_birth.isnot(None))
        )

        current_date = datetime.now().date()

        if max_age is not None:
            # Users older than max_age have birth dates before this date
            max_birth_date = current_date.replace(year=current_date.year - max_age)
            query = query.filter(User.date_of_birth >= max_birth_date)

        if min_age is not None:
            # Users younger than min_age have birth dates after this date
            min_birth_date = current_date.replace(year=current_date.year - min_age - 1)
            query = query.filter(User.date_of_birth <= min_birth_date)

        return query.all()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.db.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.db.rollback()

    def refresh(self, user: User) -> User:
        """
        Refresh user instance from database.

        Args:
            user: User instance to refresh

        Returns:
            Refreshed user instance
        """
        self.db.refresh(user)
        return user
