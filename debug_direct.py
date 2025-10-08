#!/usr/bin/env python3
"""
Debug script to directly test the find_or_create_user_by_name function and see what's happening.
"""

import os
import sys

# Add the backend directory to the Python path and set working directory
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)  # Change to backend directory so it finds the right database

from app.core.database import SessionLocal
from app.services.user import UserService


def debug_find_or_create():
    """Debug the find_or_create_user_by_name function directly."""

    db = SessionLocal()

    try:
        print("🔍 Direct database test of find_or_create_user_by_name")

        # Initial data
        full_name = "Debug Direct User"
        initial_data = {
            "date_of_birth": "1990-01-01",
            "lifespan": 80,
            "theme": "light",
            "font_size": 14,
        }

        print(f"\n1. Creating initial user: {full_name}")
        print(f"   Initial data: {initial_data}")

        # Create initial user
        user1 = UserService.find_or_create_user_by_name(
            db=db, full_name=full_name, **initial_data
        )

        print("✅ User created/found:")
        print(f"   - ID: {user1.id}")
        print(f"   - DOB: {user1.date_of_birth}")
        print(f"   - Lifespan: {user1.lifespan}")
        print(f"   - Theme: {user1.theme}")
        print(f"   - Font Size: {user1.font_size}")

        # Updated data
        updated_data = {
            "date_of_birth": "1995-06-15",
            "lifespan": 85,
            "theme": "dark",
            "font_size": 16,
        }

        print("\n2. Calling again with updated data:")
        print(f"   Updated data: {updated_data}")

        # Try to update
        user2 = UserService.find_or_create_user_by_name(
            db=db, full_name=full_name, **updated_data
        )

        print("✅ User after update attempt:")
        print(f"   - ID: {user2.id}")
        print(f"   - DOB: {user2.date_of_birth}")
        print(f"   - Lifespan: {user2.lifespan}")
        print(f"   - Theme: {user2.theme}")
        print(f"   - Font Size: {user2.font_size}")

        # Check if values changed
        print("\n3. Comparison:")
        if user1.id == user2.id:
            print("✅ Same user ID - update attempted")

            if str(user2.date_of_birth) == updated_data["date_of_birth"]:
                print("✅ DOB updated successfully!")
            else:
                print(
                    f"❌ DOB NOT updated! Expected: {updated_data['date_of_birth']}, Got: {user2.date_of_birth}"
                )

            if user2.lifespan == updated_data["lifespan"]:
                print("✅ Lifespan updated successfully!")
            else:
                print(
                    f"❌ Lifespan NOT updated! Expected: {updated_data['lifespan']}, Got: {user2.lifespan}"
                )

            if user2.theme == updated_data["theme"]:
                print("✅ Theme updated successfully!")
            else:
                print(
                    f"❌ Theme NOT updated! Expected: {updated_data['theme']}, Got: {user2.theme}"
                )

            if user2.font_size == updated_data["font_size"]:
                print("✅ Font size updated successfully!")
            else:
                print(
                    f"❌ Font size NOT updated! Expected: {updated_data['font_size']}, Got: {user2.font_size}"
                )
        else:
            print("❌ Different users returned!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    debug_find_or_create()
