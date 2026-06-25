#!/usr/bin/env python3

from passlib.context import CryptContext
from pydantic import BaseModel, Field, EmailStr

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simple UserCreate model for testing
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(..., min_length=8)
    is_active: bool = True
    is_verified: bool = False

def test_password_hashing():
    # Create a user object
    user_data = UserCreate(
        email="test@example.com",
        full_name="Test User",
        password="password123",
        is_active=True,
        is_verified=False
    )

    print(f"User object: {user_data}")
    print(f"User.password type: {type(user_data.password)}")
    print(f"User.password value: '{user_data.password}'")
    print(f"User.password length: {len(user_data.password)}")

    # Extract password
    password = user_data.password
    print(f"\nExtracted password:")
    print(f"  Password type: {type(password)}")
    print(f"  Password value: '{password}'")
    print(f"  Password length: {len(password)}")

    # Test bcrypt with hardcoded string
    print(f"\nTesting bcrypt with hardcoded string:")
    try:
        hashed_hardcoded = pwd_context.hash("password123")
        print(f"  Success: {hashed_hardcoded}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test bcrypt with extracted password
    print(f"\nTesting bcrypt with extracted password:")
    try:
        print(f"  About to hash password: '{password}'")
        hashed_password = pwd_context.hash(password)
        print(f"  Success: {hashed_password}")
    except Exception as e:
        print(f"  Error: {e}")
        print(f"  Password value at error time: '{password}'")
        print(f"  Password type at error time: {type(password)}")
        print(f"  Password length at error time: {len(password) if isinstance(password, str) else 'N/A'}")

    # Test with user.dict()
    print(f"\nTesting user.dict():")
    user_dict = user_data.dict()
    print(f"  User dict keys: {list(user_dict.keys())}")
    print(f"  User dict password: '{user_dict.get('password', 'NOT FOUND')}'")

    # Remove password from dict
    if 'password' in user_dict:
        del user_dict['password']
        print(f"  After deleting password, dict keys: {list(user_dict.keys())}")

    # Check if password attribute changed after dict()
    print(f"\nAfter user.dict():")
    print(f"  User.password value: '{user_data.password}'")
    print(f"  User.password length: {len(user_data.password)}")

if __name__ == "__main__":
    test_password_hashing()