#!/usr/bin/env python3
"""
Test script for the payment APIs
"""

import requests
import json

# Base URL for your Django API on PythonAnywhere
BASE_URL = "https://taratechid.pythonanywhere.com"

def test_create_payment():
    """Test creating a payment"""
    print("Testing create payment...")
    
    url = f"{BASE_URL}/api/payment/create/"
    
    # Test data
    payload = {
        "amount": 100000,  # 100,000 IDR
        "paymentMethod": "virtualAccount",  # or "qris"
        "receiptId": "test-receipt-123",
        "bookingId": "test-booking-456"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                paymentId = data['data']['paymentId']
                print(f"Payment created successfully! Payment ID: {paymentId}")
                return paymentId
        
        return None
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_get_payment_status(paymentId):
    """Test getting payment status"""
    print(f"\nTesting get payment status for {paymentId}...")
    
    url = f"{BASE_URL}/api/payment/{paymentId}/status/"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def test_simulate_payment(paymentId):
    """Test simulating payment success"""
    print(f"\nTesting simulate payment for {paymentId}...")
    
    url = f"{BASE_URL}/api/payment/{paymentId}/simulate/"
    
    try:
        response = requests.post(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def test_api_endpoints():
    """Test all API endpoints"""
    print("Testing all API endpoints...")
    
    endpoints = [
        f"{BASE_URL}/api/supabase/test-connection/",
        f"{BASE_URL}/api/supabase/get-data/?table=test",
        f"{BASE_URL}/api/payment/create/",
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint}")
        try:
            if "create" in endpoint:
                response = requests.post(endpoint, json={"amount": 1000, "paymentMethod": "virtualAccount"})
            else:
                response = requests.get(endpoint)
            print(f"Status: {response.status_code}")
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    """Main test function"""
    print("=== Payment API Test Script for PythonAnywhere ===\n")
    print(f"Testing against: {BASE_URL}")
    
    # Test 1: Test all endpoints
    test_api_endpoints()
    
    # Test 2: Create payment
    paymentId = test_create_payment()
    
    if paymentId:
        # Test 3: Get payment status
        test_get_payment_status(paymentId)
        
        # Test 4: Simulate payment (uncomment to test)
        # test_simulate_payment(paymentId)
        
        # Test 5: Get payment status again after simulation
        # test_get_payment_status(paymentId)
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    main() 