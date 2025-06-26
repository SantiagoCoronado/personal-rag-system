#!/usr/bin/env python3
"""
Test script for authentication API endpoints
This script demonstrates the usage of the auth API endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_register():
    """Test user registration"""
    print("🔐 Testing user registration...")
    
    register_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User registered successfully!")
            print(f"   User ID: {user_data['id']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Username: {user_data['username']}")
            return user_data
        else:
            print(f"❌ Registration failed: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running.")
        return None

def test_login(username, password):
    """Test user login"""
    print(f"\n🔑 Testing user login for {username}...")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            login_response = response.json()
            print(f"✅ Login successful!")
            print(f"   Token: {login_response['access_token'][:50]}...")
            print(f"   Token Type: {login_response['token_type']}")
            print(f"   User: {login_response['user']['username']}")
            return login_response['access_token']
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running.")
        return None

def test_get_me(token):
    """Test getting current user info"""
    print(f"\n👤 Testing get current user info...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User info retrieved successfully!")
            print(f"   User ID: {user_data['id']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Username: {user_data['username']}")
            print(f"   Active: {user_data['is_active']}")
            return True
        else:
            print(f"❌ Failed to get user info: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running.")
        return False

def test_invalid_token():
    """Test with invalid token"""
    print(f"\n🚫 Testing with invalid token...")
    
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Invalid token properly rejected!")
            return True
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running.")
        return False

if __name__ == "__main__":
    print("🧪 Testing Authentication API Endpoints")
    print("=" * 50)
    
    # Test registration
    user_data = test_register()
    
    if user_data:
        # Test login
        token = test_login("testuser", "testpassword123")
        
        if token:
            # Test get current user
            test_get_me(token)
            
            # Test invalid token
            test_invalid_token()
    
    print("\n" + "=" * 50)
    print("🎉 Auth API testing completed!")
    print("\nTo run the server:")
    print("uvicorn app.main:app --reload") 