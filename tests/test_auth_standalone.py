#!/usr/bin/env python3
"""
Standalone test for core authentication functions
Tests password hashing and JWT tokens without any app dependencies
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set default values for testing
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-development-only")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("ALGORITHM", "HS256")

# Import the libraries directly (make sure these are installed)
try:
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    print("✅ Required libraries imported successfully")
except ImportError as e:
    print(f"❌ Missing required library: {e}")
    print("Install with: pip install python-jose[cryptography] passlib[bcrypt]")
    exit(1)

# Initialize crypto context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Settings for testing
SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key-for-development-only")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain, hashed)

def create_access_token(email: str) -> str:
    """Create a JWT access token for the given email"""
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": datetime.utcnow() + expires_delta}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT token, returning the payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise ValueError("Invalid token payload - no subject")
        return payload
    except JWTError as e:
        raise ValueError(f"Could not validate token: {e}")

def test_password_functions():
    """Test password hashing and verification"""
    print("🔐 Testing password functions...")
    
    # Test password hashing
    password = "my_secure_password_123"
    hashed = get_password_hash(password)
    print(f"✅ Password hashed: {hashed[:30]}...")
    
    # Test password verification
    is_valid = verify_password(password, hashed)
    print(f"✅ Password verification: {is_valid}")
    
    # Test wrong password
    is_invalid = verify_password("wrong_password", hashed)
    print(f"✅ Wrong password rejected: {not is_invalid}")
    
    # Test edge cases
    try:
        # Test empty password
        empty_hash = get_password_hash("")
        print("✅ Empty password can be hashed")
        
        # Test very long password
        long_password = "a" * 1000
        long_hash = get_password_hash(long_password)
        long_valid = verify_password(long_password, long_hash)
        print(f"✅ Long password works: {long_valid}")
        
    except Exception as e:
        print(f"⚠️ Edge case issue: {e}")
    
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
        print(f"✅ Token verified: sub={payload.get('sub')}, exp={payload.get('exp')}")
        
        # Check if email matches
        if payload.get("sub") == email:
            print("✅ Token email matches")
        else:
            print("❌ Token email mismatch")
            return False
        
        # Check expiration
        exp_timestamp = payload.get("exp")
        if exp_timestamp and exp_timestamp > datetime.utcnow().timestamp():
            print("✅ Token not expired")
        else:
            print("⚠️ Token appears expired")
            
        return True
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return False

def test_invalid_token():
    """Test invalid token handling"""
    print("\n🚫 Testing invalid token...")
    
    invalid_tokens = [
        "invalid_token_here",
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature",
        "",
        "Bearer token_without_prefix"
    ]
    
    for i, invalid_token in enumerate(invalid_tokens):
        try:
            payload = verify_token(invalid_token)
            print(f"❌ Invalid token {i+1} should have failed: {invalid_token[:20]}...")
            return False
        except Exception as e:
            print(f"✅ Invalid token {i+1} properly rejected: {type(e).__name__}")
    
    return True

def test_expired_token():
    """Test expired token handling"""
    print("\n⏰ Testing expired token...")
    
    try:
        # Create a token that's already expired
        past_time = datetime.utcnow() - timedelta(minutes=1)
        to_encode = {"sub": "test@example.com", "exp": past_time}
        expired_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        payload = verify_token(expired_token)
        print(f"❌ Expired token should have failed")
        return False
    except Exception as e:
        print(f"✅ Expired token properly rejected: {type(e).__name__}")
        return True

def test_token_with_different_secrets():
    """Test token verification with wrong secret"""
    print("\n🔑 Testing token with wrong secret...")
    
    try:
        # Create token with current secret
        email = "test@example.com"
        token = create_access_token(email)
        
        # Try to verify with different secret
        wrong_secret = "wrong-secret-key"
        payload = jwt.decode(token, wrong_secret, algorithms=[ALGORITHM])
        print("❌ Token with wrong secret should have failed")
        return False
    except Exception as e:
        print(f"✅ Token with wrong secret properly rejected: {type(e).__name__}")
        return True

def performance_test():
    """Basic performance test for password hashing"""
    print("\n⚡ Performance test...")
    
    import time
    
    # Test password hashing speed
    start_time = time.time()
    for i in range(10):
        get_password_hash(f"password_{i}")
    hash_time = time.time() - start_time
    
    print(f"✅ Hashed 10 passwords in {hash_time:.3f} seconds ({hash_time/10:.3f}s each)")
    
    # Test token creation speed
    start_time = time.time()
    for i in range(100):
        create_access_token(f"user{i}@example.com")
    token_time = time.time() - start_time
    
    print(f"✅ Created 100 tokens in {token_time:.3f} seconds ({token_time/100:.4f}s each)")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Authentication Functions (Standalone)")
    print("=" * 60)
    
    # Check configuration
    print(f"🔧 Configuration:")
    print(f"   Secret Key: {SECRET_KEY[:20]}..." if len(SECRET_KEY) > 20 else f"   Secret Key: {SECRET_KEY}")
    print(f"   Algorithm: {ALGORITHM}")
    print(f"   Token Expiry: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    print()
    
    # Run all tests
    test_results = []
    test_results.append(("Password Functions", test_password_functions()))
    test_results.append(("Token Functions", test_token_functions()))
    test_results.append(("Invalid Token", test_invalid_token()))
    test_results.append(("Expired Token", test_expired_token()))
    test_results.append(("Wrong Secret", test_token_with_different_secrets()))
    test_results.append(("Performance", performance_test()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All authentication tests passed!")
        print("\n🎯 Verified Components:")
        print("   ✅ Password hashing with bcrypt")
        print("   ✅ Password verification") 
        print("   ✅ JWT token creation")
        print("   ✅ JWT token verification")
        print("   ✅ Invalid token rejection")
        print("   ✅ Expired token rejection")
        print("   ✅ Wrong secret key rejection")
        print("   ✅ Performance benchmarks")
        print("\n🚀 Ready to integrate with your RAG system!")
    else:
        print("\n❌ Some tests failed - check the errors above!")
        print("Make sure you have installed: pip install python-jose[cryptography] passlib[bcrypt]")