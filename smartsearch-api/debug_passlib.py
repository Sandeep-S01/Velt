#!/usr/bin/env python3

# Let's debug what's happening inside passlib's bcrypt handler
import bcrypt
from passlib.handlers.bcrypt import BCryptHandler
from passlib.utils.handlers import convert_to_bytes

# Create a simple bcrypt handler
handler = BCryptHandler()

print("=== Debugging passlib bcrypt handler ===")

# Test password
password = "password123"
print(f"Original password: '{password}' (type: {type(password)}, length: {len(password)})")

# Let's see what convert_to_bytes does
try:
    password_bytes = convert_to_bytes(password)
    print(f"After convert_to_bytes: {password_bytes!r} (type: {type(password_bytes)}, length: {len(password_bytes)})")
except Exception as e:
    print(f"convert_to_bytes failed: {e}")

# Let's manually call the problematic detect_wrap_bug function
from passlib.handlers.bcrypt import IDENT_2A
bug_hash = b'$2a$05$ccccccccccccccccccccccccccccccccccccccccCc'

print(f"\nTesting detect_wrap_bug with:")
print(f"  IDENT_2A: {IDENT_2A!r}")
print(f"  bug_hash: {bug_hash!r}")
print(f"  password: {password!r}")

# This is what detect_wrap_bug does:
# if verify(secret, bug_hash):
# Let's see what verify does
try:
    print("\nCalling handler.verify(secret, bug_hash)...")
    result = handler.verify(password, bug_hash)
    print(f"handler.verify result: {result}")
except Exception as e:
    print(f"handler.verify failed: {e}")
    import traceback
    traceback.print_exc()

# Let's see what happens if we call _calc_checksum directly
try:
    print("\nCalling handler._calc_checksum(secret)...")
    checksum = handler._calc_checksum(password)
    print(f"_calc_checksum result: {checksum!r}")
except Exception as e:
    print(f"_calc_checksum failed: {e}")
    import traceback
    traceback.print_exc()

# Let's see what happens in the verify method step by step
print("\n=== Manual verification steps ===")
try:
    # This is what verify does according to the traceback:
    # consteq(self._calc_checksum(secret), chk)
    # Let's break it down

    # First, get the checksum
    print("Calculating checksum...")
    checksum = handler._calc_checksum(password)
    print(f"Checksum: {checksum!r}")

    # The bug_hash checksum part (last 22 chars after the salt)
    # Format: $2a$05$salt22charschecksum22chars
    # bug_hash = $2a$05$ccccccccccccccccccccccccccccccccccccccccCc
    #           ^^ salt ^^           ^^checksum^^
    salt = bug_hash[7:7+22]  # Characters 7-28
    stored_checksum = bug_hash[7+22:]  # Characters 29-50
    print(f"Salt from bug_hash: {salt!r}")
    print(f"Stored checksum from bug_hash: {stored_checksum!r}")

except Exception as e:
    print(f"Manual verification failed: {e}")
    import traceback
    traceback.print_exc()

# Let's test if the issue is with the password being modified somewhere
print("\n=== Testing password integrity ===")
test_passwords = [
    "password123",
    "test",
    "a",
    "12345678901234567890123456789012345678901234567890123456789012345678901234567890",  # 70 chars
    "123456789012345678901234567890123456789012345678901234567890123456789012345678901",  # 71 chars
    "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123",  # 72 chars
]

for pwd in test_passwords:
    try:
        result = handler.verify(pwd, bug_hash)
        print(f"Password '{pwd[:20]}{'...' if len(pwd) > 20 else ''}' (len={len(pwd)}): verify = {result}")
    except Exception as e:
        print(f"Password '{pwd[:20]}{'...' if len(pwd) > 20 else ''}' (len={len(pwd)}): ERROR - {e}")