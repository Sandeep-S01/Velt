#!/usr/bin/env python3

# Let's test the actual user_service.create_user function
from passlib.context import CryptContext
from app.models.schemas import UserCreate

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print("=== Testing user_service.create_user scenario ===")

# Create user data exactly like in the test
user_data = UserCreate(
    email="test@example.com",
    full_name="Test User",
    password="password123",  # Shorter password to avoid bcrypt issues
    is_active=True,
    is_verified=False
)

print(f"user_data: {user_data}")
print(f"user_data.password: '{user_data.password}' (type: {type(user_data.password)}, length: {len(user_data.password)})")

# Extract password first (line 28 in user_service.py)
password = user_data.password
print(f"password variable: '{password}' (type: {type(password)}, length: {len(password)})")

# Debug line from user_service.py (line 29)
print(f"DEBUG: password type: {type(password)}, value: {password}")

# Hash the password (line 32 in user_service.py)
try:
    print("About to call pwd_context.hash(password)...")
    hashed_password = pwd_context.hash(password)
    print(f"SUCCESS: hashed_password = {hashed_password}")
except Exception as e:
    print(f"ERROR in pwd_context.hash: {e}")
    print(f"Password at time of error: '{password}' (type: {type(password)}, length: {len(password) if isinstance(password, str) else 'N/A'})")

    # Let's also check the state of the bcrypt handler
    print(f"\nChecking bcrypt handler state...")
    if hasattr(pwd_context, '_scheme_map') and 'bcrypt' in pwd_context._scheme_map:
        handler = pwd_context._scheme_map['bcrypt']
        print(f"Handler: {handler}")
        print(f"Handler type: {type(handler)}")

        # Check if the backend has the wraparound bug flag set
        if hasattr(handler, '_has_2a_wraparound_bug'):
            print(f"_has_2a_wraparound_bug: {handler._has_2a_wraparound_bug}")
        if hasattr(handler, '_workrounds_initialized'):
            print(f"_workrounds_initialized: {handler._workrounds_initialized}")

    # Let's try to manually trigger the backend initialization to see if that's where the error occurs
    print("\nTrying to manually initialize the backend...")
    try:
        # Access the handler to trigger initialization
        handler = pwd_context._scheme_map['bcrypt']
        print(f"Got handler: {handler}")

        # Try to call a method that might trigger initialization
        # Let's see if we can access the ident attribute
        if hasattr(handler, 'ident'):
            print(f"Handler ident: {handler.ident}")

    except Exception as e2:
        print(f"Error during manual initialization check: {e2}")
        import traceback
        traceback.print_exc()