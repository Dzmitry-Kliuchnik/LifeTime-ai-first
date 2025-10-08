"""make_email_and_password_optional_for_users

Revision ID: 23281904674e
Revises: 60006b2ab364
Create Date: 2025-10-08 11:34:26.440901

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "23281904674e"
down_revision: Union[str, None] = "60006b2ab364"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite doesn't support ALTER COLUMN DROP NOT NULL directly
    # We need to recreate the table with new schema

    # Create new table with nullable columns
    op.create_table(
        "users_new",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("lifespan", sa.Integer(), nullable=True),
        sa.Column("theme", sa.String(length=50), nullable=True),
        sa.Column("font_size", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for new table
    op.create_index("ix_users_new_id", "users_new", ["id"], unique=False)
    op.create_index("ix_users_new_username", "users_new", ["username"], unique=True)
    # Create partial unique index for email (only when not null)
    op.execute(
        "CREATE UNIQUE INDEX ix_users_new_email ON users_new(email) WHERE email IS NOT NULL"
    )

    # Copy data from old table to new table
    op.execute("""
        INSERT INTO users_new (
            id, username, email, hashed_password, is_active, is_verified, is_superuser,
            full_name, bio, date_of_birth, lifespan, theme, font_size, is_deleted,
            deleted_at, last_login, email_verified_at, created_at, updated_at
        )
        SELECT 
            id, username, email, hashed_password, is_active, is_verified, is_superuser,
            full_name, bio, date_of_birth, lifespan, theme, font_size, is_deleted,
            deleted_at, last_login, email_verified_at, created_at, updated_at
        FROM users
    """)

    # Drop old table
    op.drop_table("users")

    # Rename new table to original name
    op.rename_table("users_new", "users")

    # Rename indexes to match original naming convention
    # SQLite doesn't support ALTER INDEX RENAME, so we need to recreate them
    op.drop_index("ix_users_new_id", "users")
    op.drop_index("ix_users_new_username", "users")
    op.drop_index("ix_users_new_email", "users")

    # Recreate with proper names
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.execute(
        "CREATE UNIQUE INDEX ix_users_email ON users(email) WHERE email IS NOT NULL"
    )


def downgrade() -> None:
    # Recreate table with NOT NULL constraints for email and hashed_password

    # Create old table structure
    op.create_table(
        "users_old",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("lifespan", sa.Integer(), nullable=True),
        sa.Column("theme", sa.String(length=50), nullable=True),
        sa.Column("font_size", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for old table
    op.create_index("ix_users_old_id", "users_old", ["id"], unique=False)
    op.create_index("ix_users_old_username", "users_old", ["username"], unique=True)
    op.create_index("ix_users_old_email", "users_old", ["email"], unique=True)

    # Copy data (only records that have email and password)
    op.execute("""
        INSERT INTO users_old (
            id, username, email, hashed_password, is_active, is_verified, is_superuser,
            full_name, bio, date_of_birth, lifespan, theme, font_size, is_deleted,
            deleted_at, last_login, email_verified_at, created_at, updated_at
        )
        SELECT 
            id, username, email, hashed_password, is_active, is_verified, is_superuser,
            full_name, bio, date_of_birth, lifespan, theme, font_size, is_deleted,
            deleted_at, last_login, email_verified_at, created_at, updated_at
        FROM users 
        WHERE email IS NOT NULL AND hashed_password IS NOT NULL
    """)

    # Drop current table (and its indexes)
    op.drop_table("users")

    # Rename old table to original name
    op.rename_table("users_old", "users")

    # Rename indexes to match original naming convention
    # SQLite doesn't support ALTER INDEX RENAME, so we need to recreate them
    op.drop_index("ix_users_old_id", "users")
    op.drop_index("ix_users_old_username", "users")
    op.drop_index("ix_users_old_email", "users")

    # Recreate with proper names (matching previous migration patterns)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
