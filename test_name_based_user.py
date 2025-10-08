#!/usr/bin/env python3
"""
Test script for name-based user creation and retrieval functionality.
"""

import requests

# API base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"


def test_find_or_create_user_by_name():
    """Test the find or create user by name functionality."""

    print("🧪 Testing name-based user creation and retrieval...")

    # Test data
    test_user_data = {
        "full_name": "John Doe",
        "date_of_birth": "1990-05-15",
        "lifespan": 85,
        "theme": "dark",
        "font_size": 16,
    }

    print(f"\n1. Creating/finding user with name: {test_user_data['full_name']}")

    # First call - should create a new user
    response = requests.post(f"{BASE_URL}/users/by-name", json=test_user_data)

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
    else:
        print(f"❌ Failed to create user: {response.status_code} - {response.text}")
        return

    print("\n2. Calling the same endpoint again with the same name...")

    # Second call - should return the existing user
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
        print(f"❌ Failed to retrieve user: {response2.status_code} - {response2.text}")
        return

    print("\n3. Testing direct retrieval by name...")

    # Test getting user by name
    encoded_name = requests.utils.quote(test_user_data["full_name"])
    response3 = requests.get(f"{BASE_URL}/users/by-name/{encoded_name}")

    if response3.status_code == 200:
        user3 = response3.json()
        print("✅ User retrieved by name successfully!")
        print(f"   - ID: {user3['id']}")
        print(f"   - Username: {user3['username']}")

        # Verify it's the same user
        if user1["id"] == user3["id"]:
            print("✅ Same user returned via GET endpoint!")
        else:
            print("❌ Different user returned via GET endpoint!")

    else:
        print(
            f"❌ Failed to retrieve user by name: {response3.status_code} - {response3.text}"
        )

    print("\n4. Testing with a different name...")

    # Test with a different user
    test_user_data2 = {
        "full_name": "Jane Smith",
        "date_of_birth": "1985-12-01",
        "lifespan": 90,
        "theme": "light",
        "font_size": 14,
    }

    response4 = requests.post(f"{BASE_URL}/users/by-name", json=test_user_data2)

    if response4.status_code == 201:
        user4 = response4.json()
        print("✅ Second user created successfully!")
        print(f"   - ID: {user4['id']}")
        print(f"   - Username: {user4['username']}")
        print(f"   - Full Name: {user4['full_name']}")

        # Verify it's a different user
        if user1["id"] != user4["id"]:
            print("✅ Different users have different IDs - correct behavior!")
        else:
            print("❌ Same user ID returned for different names!")

    else:
        print(
            f"❌ Failed to create second user: {response4.status_code} - {response4.text}"
        )

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
