#!/usr/bin/env python3
"""
Quick test script for authentication endpoints
Run this after starting your FastAPI server to verify auth is working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Test user registration"""
    print("🔐 Testing user registration...")
    
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    
    if response.status_code == 200:
        print("✅ Registration successful!")
        print(f"   User ID: {response.json()['id']}")
        return True
    elif response.status_code == 400 and "already" in response.json().get("detail", ""):
        print("⚠️  User already exists (that's fine for testing)")
        return True
    else:
        print(f"❌ Registration failed: {response.status_code} - {response.text}")
        return False

def test_login():
    """Test user login and get token"""
    print("\n🎫 Testing user login...")
    
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login", 
        json=login_data,  # JSON data, not form data
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Login successful!")
        print(f"   Token type: {token_data['token_type']}")
        print(f"   Token: {token_data['access_token'][:20]}...")
        return token_data['access_token']
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_me_endpoint(token):
    """Test the /me endpoint with token"""
    print("\n👤 Testing /me endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        print("✅ /me endpoint successful!")
        print(f"   Email: {user_data['email']}")
        print(f"   Username: {user_data['username']}")
        print(f"   Active: {user_data['is_active']}")
        return True
    else:
        print(f"❌ /me endpoint failed: {response.status_code} - {response.text}")
        return False

def test_health_endpoints():
    """Test health endpoints"""
    print("\n🏥 Testing health endpoints...")
    
    # Test main health endpoint
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Main health endpoint working")
    else:
        print(f"❌ Main health endpoint failed: {response.status_code}")
    
    # Test query health endpoint
    response = requests.get(f"{BASE_URL}/query/health")
    if response.status_code == 200:
        print("✅ Query health endpoint working")
    else:
        print(f"❌ Query health endpoint failed: {response.status_code}")

def main():
    """Run all authentication tests"""
    print("🧪 Testing RAG System Authentication")
    print("=" * 50)
    print("Make sure your server is running: uvicorn app.main:app --reload")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Server not responding. Make sure it's running on localhost:8000")
            return
        print("✅ Server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
        print("   Run: uvicorn app.main:app --reload")
        return
    
    # Run tests
    test_health_endpoints()
    register_ok = test_register()
    
    if not register_ok:
        print("\n❌ Registration failed, stopping tests")
        return
    
    token = test_login()
    if not token:
        print("\n❌ Login failed, stopping tests")
        return
    
    me_ok = test_me_endpoint(token)
    
    # Summary
    print("\n" + "=" * 50)
    if register_ok and token and me_ok:
        print("🎉 All authentication tests passed!")
        print("✅ Ready to proceed to task 6 (File Upload System)")
        print(f"\n🔑 Your test token: {token}")
        print("You can use this token to test other endpoints manually")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
