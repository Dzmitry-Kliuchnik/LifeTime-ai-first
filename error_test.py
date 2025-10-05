import json

import requests

base_url = "http://127.0.0.1:8000"

print("=== Testing Week Calculation API Error Handling ===\n")

# Test 1: Future date of birth
print("1. Testing Future DOB Error:")
try:
    data = {"date_of_birth": "2030-01-01", "timezone": "UTC"}
    response = requests.post(f"{base_url}/api/v1/weeks/current-week", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50 + "\n")

# Test 2: Invalid timezone
print("2. Testing Invalid Timezone:")
try:
    data = {"date_of_birth": "1990-01-15", "timezone": "Invalid/Timezone"}
    response = requests.post(f"{base_url}/api/v1/weeks/current-week", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50 + "\n")

# Test 3: Invalid lifespan
print("3. Testing Invalid Lifespan:")
try:
    data = {
        "date_of_birth": "1990-01-15",
        "lifespan_years": 200,  # Too high
        "timezone": "UTC",
    }
    response = requests.post(f"{base_url}/api/v1/weeks/total-weeks", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50 + "\n")

# Test 4: Edge case - leap year DOB
print("4. Testing Leap Year DOB:")
try:
    data = {
        "date_of_birth": "2000-02-29",  # Leap day
        "lifespan_years": 80,
        "timezone": "UTC",
    }
    response = requests.post(f"{base_url}/api/v1/weeks/total-weeks", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50 + "\n")

# Test 5: Week summary with special week detection
print("5. Testing Week Summary:")
try:
    data = {
        "date_of_birth": "1990-06-15",
        "week_index": 1800,  # Around 34 years old
        "timezone": "America/New_York",
    }
    response = requests.post(f"{base_url}/api/v1/weeks/week-summary", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("Error Handling Testing Complete!")
