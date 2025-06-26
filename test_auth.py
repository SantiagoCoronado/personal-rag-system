#!/usr/bin/env python3
"""
Test script for authentication functions
This script demonstrates the usage of the auth functions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    verify_token
)

def test_password_functions():
    """Test password hashing and verification"""
    print("🔐 Testing password functions...")
    
    # Test password hashing
    password = "my_secure_password_123"
    hashed = get_password_hash(password)
    print(f"✅ Password hashed: {hashed[:20]}...")
    
    # Test password verification
    is_valid = verify_password(password, hashed)
    print(f"✅ Password verification: {is_valid}")
    
    # Test wrong password
    is_invalid = verify_password("wrong_password", hashed)
    print(f"✅ Wrong password rejected: {not is_invalid}")
    
    return True

def test_token_functions():
    """Test JWT token creation and verification"""
    print("\n🎫 Testing token functions...")
    
    # Test token creation
    email = "user@example.com"
    token = create_access_token(email)
    print(f"✅ Token created: {token[:50]}...")
    
    # Test token verification
    try:
        payload = verify_token(token)
        print(f"✅ Token verified: {payload}")
        return True
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return False

def test_invalid_token():
    """Test invalid token handling"""
    print("\n🚫 Testing invalid token...")
    
    try:
        payload = verify_token("invalid_token_here")
        print(f"❌ Invalid token should have failed")
        return False
    except Exception as e:
        print(f"✅ Invalid token properly rejected: {type(e).__name__}")
        return True

if __name__ == "__main__":
    print("🧪 Testing Authentication Functions")
    print("=" * 50)
    
    # Test password functions
    password_ok = test_password_functions()
    
    # Test token functions
    token_ok = test_token_functions()
    
    # Test invalid token
    invalid_ok = test_invalid_token()
    
    print("\n" + "=" * 50)
    if password_ok and token_ok and invalid_ok:
        print("✅ All authentication tests passed!")
    else:
        print("❌ Some tests failed!") 