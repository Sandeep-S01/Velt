#!/usr/bin/env python3

import bcrypt
from passlib.utils.handlers import constant_time, to_unicode
from passlib.utils.binary import aba64_to_bytes

# Recreate the test from passlib's detect_wrap_bug_wrap_bf = b'$2b$'
IDENT_2A = b'$2a$'

# This is the test hash from passlib
bug_hash = b'$2a$05$ccccccccccccccccccccccccccccccccccccccccCc'

def test_wrap_bug():
    # This is what passlib is doing in detect_wrap_bug
    ID = b'$2a$'
    # Check if we need to reset state

    # The test password that passlib uses
    password = b"k"

    print(f"Testing wrap bug detection...")
    print(f"Password: {password}")
    print(f"Password length: {len(password)}")
    print(f"Hash: {bug_hash}")

    try:
        # This is where it fails
        result = bcrypt.checkpw(password, bug_hash)
        print(f"bcrypt.checkpw result: {result}")
        return result
    except Exception as e:
        print(f"bcrypt.checkpw error: {e}")
        return False

def test_direct_bcrypt():
    # Test with a normal password and hash
    password = b"password123"
    salt = bcrypt.gensalt()
    print(f"Salt: {salt}")

    # Hash the password
    hashed = bcrypt.hashpw(password, salt)
    print(f"Hashed: {hashed}")

    # Check the password
    check_result = bcrypt.checkpw(password, hashed)
    print(f"Check result: {check_result}")

    return hashed

if __name__ == "__main__":
    print("=== Testing wrap bug detection ===")
    wrap_result = test_wrap_bug()

    print("\n=== Testing direct bcrypt ===")
    hash_result = test_direct_bcrypt()