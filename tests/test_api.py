"""
Simple test script for week calculation API endpoints.
"""

import json

import requests


def test_api_endpoints():
    """Test the week calculation API endpoints."""
    base_url = "http://127.0.0.1:8000"

    print("Testing Week Calculation API")
    print("=" * 50)

    # Test 1: API Health
    print("\n1. Testing API Health:")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Week calculation service health
    print("\n2. Testing Week Calculation Service Health:")
    try:
        response = requests.get(f"{base_url}/api/v1/weeks/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: Calculate total weeks
    print("\n3. Testing Total Weeks Calculation:")
    try:
        data = {"date_of_birth": "1990-01-15", "lifespan_years": 80, "timezone": "UTC"}
        response = requests.post(f"{base_url}/api/v1/weeks/total-weeks", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 4: Calculate current week
    print("\n4. Testing Current Week Calculation:")
    try:
        data = {"date_of_birth": "1990-01-15", "timezone": "America/New_York"}
        response = requests.post(f"{base_url}/api/v1/weeks/current-week", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 5: Get week summary
    print("\n5. Testing Week Summary:")
    try:
        data = {
            "date_of_birth": "1990-01-15",
            "week_index": 1800,  # ~34 years old
            "timezone": "UTC",
        }
        response = requests.post(f"{base_url}/api/v1/weeks/week-summary", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 6: Calculate life progress
    print("\n6. Testing Life Progress Calculation:")
    try:
        data = {
            "date_of_birth": "1990-06-15",
            "lifespan_years": 85,
            "timezone": "Europe/London",
        }
        response = requests.post(f"{base_url}/api/v1/weeks/life-progress", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 7: Quick current week (GET endpoint)
    print("\n7. Testing Quick Current Week (GET):")
    try:
        response = requests.get(f"{base_url}/api/v1/weeks/current-week/1985-03-20")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 8: Quick total weeks (GET endpoint)
    print("\n8. Testing Quick Total Weeks (GET):")
    try:
        response = requests.get(f"{base_url}/api/v1/weeks/total-weeks/1985-03-20/75")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 9: Error handling - future DOB
    print("\n9. Testing Error Handling (Future DOB):")
    try:
        data = {"date_of_birth": "2030-01-01", "timezone": "UTC"}
        response = requests.post(f"{base_url}/api/v1/weeks/current-week", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50)
    print("API Testing Complete!")


if __name__ == "__main__":
    test_api_endpoints()
