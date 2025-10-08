#!/usr/bin/env python3
"""
Test script specifically for testing date of birth updates in name-based user functionality.
"""

import requests

# API base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"


def test_date_of_birth_update():
    """Test that date of birth gets updated when creating user with existing name."""

    print("🧪 Testing date of birth update functionality...")

    # Initial user data
    initial_data = {
        "full_name": "Test Update User",
        "date_of_birth": "1990-01-01",
        "lifespan": 80,
        "theme": "light",
        "font_size": 14,
    }

    print(f"\n1. Creating initial user: {initial_data['full_name']}")
    print(f"   Initial DOB: {initial_data['date_of_birth']}")

    # Create initial user
    response1 = requests.post(f"{BASE_URL}/users/by-name", json=initial_data)

    if response1.status_code == 201:
        user1 = response1.json()
        print("✅ Initial user created successfully!")
        print(f"   - ID: {user1['id']}")
        print(f"   - Date of Birth: {user1['date_of_birth']}")
    else:
        print(
            f"❌ Failed to create initial user: {response1.status_code} - {response1.text}"
        )
        return

    # Updated user data with different date of birth
    updated_data = {
        "full_name": "Test Update User",  # Same name
        "date_of_birth": "1995-06-15",  # Different DOB
        "lifespan": 85,  # Different lifespan
        "theme": "dark",  # Different theme
        "font_size": 16,  # Different font size
    }

    print("\n2. Updating user with new data:")
    print(f"   New DOB: {updated_data['date_of_birth']}")
    print(f"   New Lifespan: {updated_data['lifespan']}")
    print(f"   New Theme: {updated_data['theme']}")
    print(f"   New Font Size: {updated_data['font_size']}")

    # Update user by calling the same endpoint with new data
    response2 = requests.post(f"{BASE_URL}/users/by-name", json=updated_data)

    if response2.status_code == 201:
        user2 = response2.json()
        print("✅ User update call completed!")
        print(f"   - ID: {user2['id']}")
        print(f"   - Date of Birth: {user2['date_of_birth']}")
        print(f"   - Lifespan: {user2['lifespan']}")
        print(f"   - Theme: {user2['theme']}")
        print(f"   - Font Size: {user2['font_size']}")

        # Verify it's the same user ID
        if user1["id"] == user2["id"]:
            print("✅ Same user ID - update attempted!")

            # Check if date of birth was updated
            if user2["date_of_birth"] == updated_data["date_of_birth"]:
                print("✅ Date of birth was successfully updated!")
            else:
                print("❌ Date of birth was NOT updated!")
                print(f"   Expected: {updated_data['date_of_birth']}")
                print(f"   Got: {user2['date_of_birth']}")

            # Check other fields
            if user2["lifespan"] == updated_data["lifespan"]:
                print("✅ Lifespan was successfully updated!")
            else:
                print(
                    f"❌ Lifespan was NOT updated! Expected: {updated_data['lifespan']}, Got: {user2['lifespan']}"
                )

            if user2["theme"] == updated_data["theme"]:
                print("✅ Theme was successfully updated!")
            else:
                print(
                    f"❌ Theme was NOT updated! Expected: {updated_data['theme']}, Got: {user2['theme']}"
                )

            if user2["font_size"] == updated_data["font_size"]:
                print("✅ Font size was successfully updated!")
            else:
                print(
                    f"❌ Font size was NOT updated! Expected: {updated_data['font_size']}, Got: {user2['font_size']}"
                )

        else:
            print("❌ Different user ID returned - should be the same user!")

    else:
        print(f"❌ Failed to update user: {response2.status_code} - {response2.text}")

    print("\n🎉 Date of birth update test completed!")


if __name__ == "__main__":
    try:
        test_date_of_birth_update()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print(
            "   Please make sure the backend server is running on http://127.0.0.1:8000"
        )
    except Exception as e:
        print(f"❌ An error occurred: {e}")
