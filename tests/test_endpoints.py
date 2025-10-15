#!/usr/bin/env python3
"""
Quick test script for the new GET endpoints.
"""

import json
from datetime import date

import requests


# Test the GET endpoints
def test_endpoints():
    base_url = "http://127.0.0.1:8000/api/v1"

    print("Testing Week Calculation GET Endpoints")
    print("=" * 50)

    # Test GET /weeks/total
    print("\n1. Testing GET /weeks/total endpoint:")
    try:
        response = requests.get(
            f"{base_url}/weeks/total",
            params={"date_of_birth": "1990-01-15", "lifespan_years": 80},
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
        return

    # Test GET /weeks/current
    print("\n2. Testing GET /weeks/current endpoint:")
    try:
        response = requests.get(
            f"{base_url}/weeks/current",
            params={"date_of_birth": "1990-01-15", "timezone": "UTC"},
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
        return

    # Test with different timezone
    print("\n3. Testing with different timezone (America/New_York):")
    try:
        response = requests.get(
            f"{base_url}/weeks/current",
            params={"date_of_birth": "1990-01-15", "timezone": "America/New_York"},
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
        return

    # Test error handling - future date
    print("\n4. Testing error handling (future date):")
    try:
        future_date = date.today().replace(year=date.today().year + 1).isoformat()
        response = requests.get(
            f"{base_url}/weeks/total",
            params={"date_of_birth": future_date, "lifespan_years": 80},
        )

        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Error Response: {json.dumps(data, indent=2)}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
        return

    # Test OpenAPI docs
    print("\n5. Testing OpenAPI documentation:")
    try:
        response = requests.get("http://127.0.0.1:8000/openapi.json")
        print(f"OpenAPI Status Code: {response.status_code}")

        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})

            if "/api/v1/weeks/total" in paths:
                print("✅ GET /weeks/total endpoint documented")
            else:
                print("❌ GET /weeks/total endpoint not found in docs")

            if "/api/v1/weeks/current" in paths:
                print("✅ GET /weeks/current endpoint documented")
            else:
                print("❌ GET /weeks/current endpoint not found in docs")

    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
        return

    print("\n" + "=" * 50)
    print("✅ All endpoint tests completed!")


if __name__ == "__main__":
    test_endpoints()
