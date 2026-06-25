#!/usr/bin/env python3

# Let's test what happens when we try to hash a long password with bcrypt directly
import bcrypt

print("=== Testing bcrypt with long passwords ===")

# Test with a short password (should work)
short_password = b"password123"
print(f"Short password length: {len(short_password)}")
try:
    hash_result = bcrypt.hashpw(short_password, bcrypt.gensalt())
    print(f"Short password hash SUCCESS: {hash_result}")
except Exception as e:
    print(f"Short password hash FAILED: {e}")

# Test with a password that's exactly 72 bytes
password_72 = b"A" * 72
print(f"\n72-byte password length: {len(password_72)}")
try:
    hash_result = bcrypt.hashpw(password_72, bcrypt.gensalt())
    print(f"72-byte password hash SUCCESS: {hash_result}")
except Exception as e:
    print(f"72-byte password hash FAILED: {e}")

# Test with a password that's 73 bytes (should fail with current bcrypt Python library)
password_73 = b"A" * 73
print(f"\n73-byte password length: {len(password_73)}")
try:
    hash_result = bcrypt.hashpw(password_73, bcrypt.gensalt())
    print(f"73-byte password hash SUCCESS: {hash_result}")
except Exception as e:
    print(f"73-byte password hash FAILED: {e}")

# Test with a 255 byte password (like passlib's detect_wrap_bug uses)
# 25*10 + 5 = 255 bytes
password_255 = b"0123456789" * 25 + b"01234"
print(f"\n255-byte password length: {len(password_255)}")
try:
    hash_result = bcrypt.hashpw(password_255, bcrypt.gensalt())
    print(f"255-byte password hash SUCCESS: {hash_result}")
except Exception as e:
    print(f"255-byte password hash FAILED: {e}")

# Let's also test what the actual secret is in detect_wrap_bug
print("\n=== Testing detect_wrap_bug secret ===")
detect_secret = (b"0123456789"*26)[:255]
print(f"detect_wrap_bug secret length: {len(detect_secret)}")
print(f"First 20 bytes: {detect_secret[:20]}")
print(f"Last 20 bytes: {detect_secret[-20:]}")

try:
    hash_result = bcrypt.hashpw(detect_secret, bcrypt.gensalt())
    print(f"detect_wrap_bug secret hash SUCCESS: {hash_result}")
except Exception as e:
    print(f"detect_wrap_bug secret hash FAILED: {e}")

# Let's see what happens if we truncate to 72 bytes
print("\n=== Testing truncated secret ===")
truncated_secret = detect_secret[:72]
print(f"Truncated secret length: {len(truncated_secret)}")
try:
    hash_result = bcrypt.hashpw(truncated_secret, bcrypt.gensalt())
    print(f"Truncated hash SUCCESS: {hash_result}")
except Exception as e:
    print(f"Truncated hash FAILED: {e}")