"""
User API endpoints for CRUD operations.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.rate_limiting import (
    user_auth_rate_limit,
    user_read_rate_limit,
    user_write_rate_limit,
)
from app.schemas.user import (
    PasswordChange,
    UserByNameCreate,
    UserCreate,
    UserProfileUpdate,
    UserResponse,
    UserSummary,
    UserUpdate,
)
from app.services.user import UserService

# Create router for user endpoints
user_router = APIRouter(prefix="/users", tags=["users"])

# Constants for error messages
INVALID_USER_ID_MSG = "User ID must be a positive integer"


@user_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate, db: Session = Depends(get_db)
) -> UserResponse:
    """
    Create a new user account.

    Args:
        user_data: User creation data
        db: Database session

    Returns:
        Created user information

    Raises:
        409: Username or email already exists
        422: Validation error
    """
    try:
        user = UserService.create_user(db, user_data)
        return UserResponse.model_validate(user)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@user_router.post(
    "/by-name", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def find_or_create_user_by_name(
    user_data: UserByNameCreate, db: Session = Depends(get_db)
) -> UserResponse:
    """
    Find existing user by name or create a new one with default settings.
    This is useful for simple user management where users are identified by name only.

    Args:
        user_data: User data including full name and optional settings
        db: Database session

    Returns:
        User information (existing or newly created)

    Raises:
        409: Unable to create user
        422: Validation error
    """
    try:
        user = UserService.find_or_create_user_by_name(
            db=db,
            full_name=user_data.full_name,
            date_of_birth=user_data.date_of_birth,
            lifespan=user_data.lifespan,
            theme=user_data.theme,
            font_size=user_data.font_size,
        )
        return UserResponse.model_validate(user)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@user_router.get("/", response_model=List[UserSummary])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of users to return"
    ),
    search: Optional[str] = Query(
        None, description="Search term for username, email, or full name"
    ),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    include_deleted: bool = Query(False, description="Include soft-deleted users"),
    db: Session = Depends(get_db),
) -> List[UserSummary]:
    """
    Get list of users with optional filtering and pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for filtering
        is_active: Filter by active status
        include_deleted: Whether to include soft-deleted users
        db: Database session

    Returns:
        List of user summaries
    """
    users = UserService.get_users(
        db=db,
        skip=skip,
        limit=limit,
        include_deleted=include_deleted,
        search=search,
        is_active=is_active,
    )
    return [UserSummary.model_validate(user) for user in users]


@user_router.get("/by-name/{full_name}", response_model=UserResponse)
async def get_user_by_name(
    full_name: str, db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get user by full name.

    Args:
        full_name: User's full name
        db: Database session

    Returns:
        User information

    Raises:
        404: User not found
    """
    try:
        from app.repositories.user import UserRepository

        repo = UserRepository(db)
        user = repo.get_by_full_name(full_name, include_deleted=False)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with name '{full_name}' not found",
            )

        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@user_router.get("/{user_id}", response_model=UserResponse)
@user_read_rate_limit()
async def get_user(
    user_id: int,
    include_deleted: bool = Query(False, description="Include soft-deleted user"),
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Get user by ID.

    Args:
        user_id: User ID to retrieve
        include_deleted: Whether to include soft-deleted user
        db: Database session

    Returns:
        User information

    Raises:
        400: Invalid user ID (non-positive integer)
        404: User not found
    """
    # Validate user_id
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_USER_ID_MSG,
        )

    user = UserService.get_user(db, user_id, include_deleted=include_deleted)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return UserResponse.model_validate(user)


@user_router.get("/username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    include_deleted: bool = Query(False, description="Include soft-deleted user"),
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Get user by username.

    Args:
        username: Username to search for
        include_deleted: Whether to include soft-deleted user
        db: Database session

    Returns:
        User information

    Raises:
        404: User not found
    """
    user = UserService.get_user_by_username(
        db, username, include_deleted=include_deleted
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username '{username}' not found",
        )
    return UserResponse.model_validate(user)


@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update user information.

    Args:
        user_id: User ID to update
        user_data: Updated user data
        db: Database session

    Returns:
        Updated user information

    Raises:
        404: User not found
        409: Username or email already exists
        422: Validation error
    """
    try:
        user = UserService.update_user(db, user_id, user_data)
        return UserResponse.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@user_router.patch("/{user_id}", response_model=UserResponse)
@user_write_rate_limit()
async def patch_user(
    user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)
) -> UserResponse:
    """
    Partially update user information using PATCH method.
    Only provided fields will be updated, null/undefined fields are ignored.

    Args:
        user_id: User ID to update
        user_data: Partial user data to update
        db: Database session

    Returns:
        Updated user information

    Raises:
        400: Invalid user ID (non-positive integer)
        404: User not found
        409: Username or email already exists
        422: Validation error
    """
    # Validate user_id
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_USER_ID_MSG,
        )

    try:
        user = UserService.update_user(db, user_id, user_data)
        return UserResponse.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@user_router.patch("/{user_id}/profile", response_model=UserResponse)
@user_write_rate_limit()
async def update_user_profile(
    user_id: int, profile_data: UserProfileUpdate, db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update user profile settings only.

    Args:
        user_id: User ID to update
        profile_data: Updated profile data
        db: Database session

    Returns:
        Updated user information

    Raises:
        400: Invalid user ID (non-positive integer)
        404: User not found
        422: Validation error
    """
    # Validate user_id
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_USER_ID_MSG,
        )

    try:
        user = UserService.update_user_profile(db, user_id, profile_data)
        return UserResponse.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@user_router.post("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
@user_auth_rate_limit()
async def change_password(
    user_id: int, password_data: PasswordChange, db: Session = Depends(get_db)
) -> None:
    """
    Change user password.

    Args:
        user_id: User ID
        password_data: Password change data
        db: Database session

    Raises:
        404: User not found
        422: Current password incorrect or validation error
    """
    try:
        UserService.change_password(db, user_id, password_data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@user_router.delete("/{user_id}", response_model=UserResponse)
async def soft_delete_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    """
    Soft delete a user (mark as deleted).

    Args:
        user_id: User ID to delete
        db: Database session

    Returns:
        Soft-deleted user information

    Raises:
        404: User not found
    """
    try:
        user = UserService.soft_delete_user(db, user_id)
        return UserResponse.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@user_router.post("/{user_id}/restore", response_model=UserResponse)
async def restore_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    """
    Restore a soft-deleted user.

    Args:
        user_id: User ID to restore
        db: Database session

    Returns:
        Restored user information

    Raises:
        404: User not found
        422: User is not deleted
    """
    try:
        user = UserService.restore_user(db, user_id)
        return UserResponse.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@user_router.delete("/{user_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
async def hard_delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    """
    Permanently delete a user from the database.
    WARNING: This operation cannot be undone!

    Args:
        user_id: User ID to delete
        db: Database session

    Raises:
        404: User not found
    """
    try:
        UserService.hard_delete_user(db, user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@user_router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    """
    Activate a user account.

    Args:
        user_id: User ID to activate
        db: Database session

    Returns:
        Activated user information

    Raises:
        404: User not found
    """
    try:
        user = UserService.activate_user(db, user_id)
        return UserResponse.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@user_router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    """
    Deactivate a user account.

    Args:
        user_id: User ID to deactivate
        db: Database session

    Returns:
        Deactivated user information

    Raises:
        404: User not found
    """
    try:
        user = UserService.deactivate_user(db, user_id)
        return UserResponse.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@user_router.get("/stats/summary")
async def get_user_stats(db: Session = Depends(get_db)) -> dict:
    """
    Get user statistics summary.

    Args:
        db: Database session

    Returns:
        Dictionary with user statistics
    """
    total_users = UserService.get_user_count(db, include_deleted=False)
    active_users = UserService.get_user_count(db, include_deleted=False, is_active=True)
    deleted_users = UserService.get_user_count(db, include_deleted=True) - total_users

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "deleted_users": deleted_users,
    }
