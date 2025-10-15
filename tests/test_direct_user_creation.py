#!/usr/bin/env python3
"""
Direct database test for user creation functionality.
"""

import sys

sys.path.append("backend")

from app.core.database import get_db
from app.services.user import UserService
from sqlalchemy.orm import Session


def test_direct_user_creation():
    """Test user creation directly through the service layer."""

    print("🧪 Testing direct user creation through service layer...")

    # Get database session
    db_gen = get_db()
    db: Session = next(db_gen)

    try:
        # Test data
        import time

        timestamp = int(time.time())

        full_name = f"Direct Test User {timestamp}"
        print(f"\n1. Creating user with name: {full_name}")

        # Create user using service
        user = UserService.find_or_create_user_by_name(
            db=db,
            full_name=full_name,
            date_of_birth="1990-05-15",
            lifespan=85,
            theme="dark",
            font_size=16,
        )

        print("✅ User created successfully!")
        print(f"   - ID: {user.id}")
        print(f"   - Username: {user.username}")
        print(f"   - Full Name: {user.full_name}")
        print(f"   - Email: {user.email}")
        print(f"   - Date of Birth: {user.date_of_birth}")
        print(f"   - Lifespan: {user.lifespan}")
        print(f"   - Theme: {user.theme}")
        print(f"   - Font Size: {user.font_size}")

        # Test finding the same user
        print("\n2. Finding the same user by name...")
        user2 = UserService.find_or_create_user_by_name(
            db=db,
            full_name=full_name,
            date_of_birth="1990-05-15",
            lifespan=85,
            theme="dark",
            font_size=16,
        )

        if user.id == user2.id:
            print("✅ Same user returned - persistence working correctly!")
        else:
            print("❌ Different user returned - persistence not working!")

        db.commit()

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback

        traceback.print_exc()
    finally:
        db.close()

    print("\n🎉 Direct user creation test completed!")


if __name__ == "__main__":
    test_direct_user_creation()
