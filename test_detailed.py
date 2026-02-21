import requests
import json
import time

def test_detailed_endpoints():
    """Test endpoints in detail to verify security improvements"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔬 Detailed Security Testing")
    print("=" * 40)
    
    # Test 1: Check balance endpoint error handling
    print("\n1️⃣ Testing check_balance error handling...")
    try:
        response = requests.post(f"{base_url}/check_balance", 
                               json={"public_key": "invalid_key"})
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            if 'error' in response_data:
                print(f"✅ Proper error returned: {response_data['error']}")
            else:
                print("ℹ️ Response:", response_data)
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Send money input validation
    print("\n2️⃣ Testing send_money input validation...")
    try:
        # Test with missing fields
        response = requests.post(f"{base_url}/send_money", 
                               json={})
        print(f"Missing fields status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            if 'error' in response_data:
                print(f"✅ Validation error: {response_data['error']}")
            else:
                print("ℹ️ Response:", response_data)

        # Test with invalid amount
        response = requests.post(f"{base_url}/send_money", 
                               json={
                                   "recipient": "GBXXXX", 
                                   "amount": "invalid", 
                                   "transaction_password": "test"
                               })
        print(f"Invalid amount status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            if 'error' in response_data:
                print(f"✅ Amount validation error: {response_data['error']}")
            else:
                print("ℹ️ Response:", response_data)
                
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: Rate limiting effectiveness
    print("\n3️⃣ Testing rate limiting...")
    success_count = 0
    rate_limited_count = 0
    
    for i in range(7):  # Test more than the 5/minute limit for send_money
        try:
            response = requests.post(f"{base_url}/send_money", 
                                   json={"test": "rate_limit"})
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:  # Rate limited
                rate_limited_count += 1
            elif response.status_code == 403:  # Forbidden (might be rate limit)
                rate_limited_count += 1
            print(f"Request {i+1}: {response.status_code}")
        except Exception as e:
            print(f"Request {i+1} failed: {e}")
        time.sleep(0.2)
    
    print(f"Success responses: {success_count}")
    print(f"Rate limited responses: {rate_limited_count}")
    
    if rate_limited_count > 0:
        print("✅ Rate limiting appears to be working")
    else:
        print("ℹ️ Rate limiting may require authenticated requests")

    print("\n✨ Detailed testing completed!")

if __name__ == "__main__":
    test_detailed_endpoints()