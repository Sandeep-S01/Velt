#!/usr/bin/env python3

import bcrypt
from passlib.context import CryptContext

print("Testing bcrypt directly:")
try:
    # Test bcrypt directly
    password = b"password123"
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    print(f"Direct bcrypt success: {hashed}")
except Exception as e:
    print(f"Direct bcrypt failed: {e}")

print("\nTesting passlib:")
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password = "password123"
    hashed = pwd_context.hash(password)
    print(f"Passlib success: {hashed}")
except Exception as e:
    print(f"Passlib failed: {e}")
    import traceback
    traceback.print_exc()