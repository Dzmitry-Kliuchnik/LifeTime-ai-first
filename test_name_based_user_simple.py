#!/usr/bin/env python3
"""
Test script for name-based user creation and retrieval functionality with better error handling.
"""

import requests

# API base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"


def test_find_or_create_user_by_name():
    """Test the find or create user by name functionality."""

    print("🧪 Testing name-based user creation and retrieval...")

    # Use a unique name with timestamp to avoid conflicts
    import time

    timestamp = int(time.time())

    # Test data
    test_user_data = {
        "full_name": f"Test User {timestamp}",
        "date_of_birth": "1990-05-15",
        "lifespan": 85,
        "theme": "dark",
        "font_size": 16,
    }

    print(f"\n1. Creating/finding user with name: {test_user_data['full_name']}")

    # First call - should create a new user
    response = requests.post(f"{BASE_URL}/users/by-name", json=test_user_data)

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    if response.status_code == 201:
        user1 = response.json()
        print("✅ User created successfully!")
        print(f"   - ID: {user1['id']}")
        print(f"   - Username: {user1['username']}")
        print(f"   - Full Name: {user1['full_name']}")
        print(f"   - Date of Birth: {user1['date_of_birth']}")
        print(f"   - Lifespan: {user1['lifespan']}")
        print(f"   - Theme: {user1['theme']}")
        print(f"   - Font Size: {user1['font_size']}")

        # Test that calling the same endpoint again returns the same user
        print("\n2. Calling the same endpoint again with the same name...")
        response2 = requests.post(f"{BASE_URL}/users/by-name", json=test_user_data)

        if response2.status_code == 201:
            user2 = response2.json()
            print("✅ User retrieved successfully!")
            print(f"   - ID: {user2['id']}")
            print(f"   - Username: {user2['username']}")

            # Verify it's the same user
            if user1["id"] == user2["id"]:
                print("✅ Same user returned - persistence working correctly!")
            else:
                print("❌ Different user returned - persistence not working!")
        else:
            print(
                f"❌ Failed to retrieve user: {response2.status_code} - {response2.text}"
            )

    else:
        print(f"❌ Failed to create user: {response.status_code} - {response.text}")

    print("\n🎉 Name-based user management test completed!")


if __name__ == "__main__":
    try:
        test_find_or_create_user_by_name()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print(
            "   Please make sure the backend server is running on http://127.0.0.1:8000"
        )
    except Exception as e:
        print(f"❌ An error occurred: {e}")
