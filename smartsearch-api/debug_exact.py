#!/usr/bin/env python3

# Let's test the exact scenario from user_service.py
from passlib.context import CryptContext
from app.models.schemas import UserCreate

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print("=== Testing exact scenario from user_service.py ===")

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

    # Let's examine the password more carefully
    print(f"Password repr: {repr(password)}")
    for i, char in enumerate(password):
        print(f"  [{i}]: '{char}' (ord={ord(char)})")

    # Let's try to hash a known good password
    try:
        print("\nTrying to hash a known good password 'test123'...")
        good_hash = pwd_context.hash("test123")
        print(f"Good hash worked: {good_hash}")
    except Exception as e2:
        print(f"Even good password failed: {e2}")

    # Let's check if there's something wrong with the bcrypt installation
    import bcrypt
    print(f"\nbcrypt version info: {getattr(bcrypt, '__version__', 'No version attr')}")
    try:
        # Test bcrypt directly
        direct_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt())
        print(f"Direct bcrypt works: {direct_hash}")
    except Exception as e3:
        print(f"Direct bcrypt also failed: {e3}")