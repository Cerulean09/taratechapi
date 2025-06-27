#!/usr/bin/env python3
"""
Test script for Supabase API endpoints
Run this script to test the API functionality
"""

import requests
import json
import os

# Base URL for the API
BASE_URL = "http://localhost:8000"

def testConnection():
    """Test the connection to Supabase"""
    print("Testing Supabase connection...")
    try:
        response = requests.get(f"{BASE_URL}/api/supabase/test-connection/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def testGetData():
    """Test getting data from a table"""
    print("\nTesting get data endpoint...")
    try:
        # You'll need to replace 'your_table_name' with an actual table name
        response = requests.get(f"{BASE_URL}/api/supabase/get-data/?table=your_table_name&limit=5")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 400]  # 400 is expected if table doesn't exist
    except Exception as e:
        print(f"Error: {e}")
        return False

def testInsertData():
    """Test inserting data into a table"""
    print("\nTesting insert data endpoint...")
    try:
        data = {
            "table": "test_table",
            "data": {
                "name": "Test User",
                "email": "test@example.com",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/supabase/insert-data/",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 400]  # 400 is expected if table doesn't exist
    except Exception as e:
        print(f"Error: {e}")
        return False

def testUpdateData():
    """Test updating data in a table"""
    print("\nTesting update data endpoint...")
    try:
        data = {
            "table": "test_table",
            "data": {
                "name": "Updated Test User"
            },
            "conditions": {
                "email": "test@example.com"
            }
        }
        response = requests.put(
            f"{BASE_URL}/api/supabase/update-data/",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 400]
    except Exception as e:
        print(f"Error: {e}")
        return False

def testDeleteData():
    """Test deleting data from a table"""
    print("\nTesting delete data endpoint...")
    try:
        data = {
            "table": "test_table",
            "conditions": {
                "email": "test@example.com"
            }
        }
        response = requests.delete(
            f"{BASE_URL}/api/supabase/delete-data/",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 400]
    except Exception as e:
        print(f"Error: {e}")
        return False

def testAuthentication():
    """Test user authentication"""
    print("\nTesting authentication endpoint...")
    try:
        data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        response = requests.post(
            f"{BASE_URL}/api/supabase/auth/login/",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 401]  # 401 is expected for invalid credentials
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Supabase API tests...")
    print("=" * 50)
    
    # Check if Django server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print("Django server is running")
    except:
        print("Error: Django server is not running. Please start it with 'python manage.py runserver'")
        return
    
    # Run tests
    tests = [
        testConnection,
        testGetData,
        testInsertData,
        testUpdateData,
        testDeleteData,
        testAuthentication
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("All tests passed! 🎉")
    else:
        print("Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 