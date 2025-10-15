import json

import requests

# Test basic API endpoints
base_url = "http://127.0.0.1:8000"

print("=== Testing Week Calculation API ===\n")

# Test 1: Total weeks calculation
print("1. Testing Total Weeks Calculation:")
try:
    data = {"date_of_birth": "1990-01-15", "lifespan_years": 80, "timezone": "UTC"}
    response = requests.post(f"{base_url}/api/v1/weeks/total-weeks", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50 + "\n")

# Test 2: Current week calculation
print("2. Testing Current Week Calculation:")
try:
    data = {"date_of_birth": "1990-01-15", "timezone": "America/New_York"}
    response = requests.post(f"{base_url}/api/v1/weeks/current-week", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50 + "\n")

# Test 3: Life progress calculation
print("3. Testing Life Progress Calculation:")
try:
    data = {
        "date_of_birth": "1985-06-15",
        "lifespan_years": 85,
        "timezone": "Europe/London",
    }
    response = requests.post(f"{base_url}/api/v1/weeks/life-progress", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50 + "\n")

# Test 4: Quick endpoints
print("4. Testing Quick Current Week (GET):")
try:
    response = requests.get(f"{base_url}/api/v1/weeks/current-week/1985-03-20")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50 + "\n")

print("5. Testing Quick Total Weeks (GET):")
try:
    response = requests.get(f"{base_url}/api/v1/weeks/total-weeks/1985-03-20/75")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("API Testing Complete!")
