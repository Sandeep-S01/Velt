#!/usr/bin/env python3

# Let's replicate exactly what passlib's _calc_checksum does
import bcrypt
from passlib.utils.handlers import to_unicode

# This is from passlib.handlers.bcrypt.BCryptHandler._calc_checksum
def _calc_checksum_passlib(secret):
    """Replicate passlib's _calc_checksum method"""
    print(f"  [_calc_checksum] Input secret: {secret!r} (type: {type(secret)}, length: {len(secret) if isinstance(secret, (str, bytes)) else 'N/A'})")

    # to_unicode conversion
    secret = to_unicode(secret)
    print(f"  [_calc_checksum] After to_unicode: {secret!r} (type: {type(secret)}, length: {len(secret)})")

    # Now call the backend's hashpw method
    # We need to get the config - let's use a standard bcrypt config
    config = b'$2b$12$XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    print(f"  [_calc_checksum] About to call bcrypt.hashpw(secret, config)")
    print(f"  [_calc_checksum] secret: {secret!r}")
    print(f"  [_calc_checksum] config: {config!r}")

    try:
        # This is the call that's failing
        hash = bcrypt.hashpw(secret, config)
        print(f"  [_calc_checksum] Success: {hash!r}")
        return hash
    except Exception as e:
        print(f"  [_calc_checksum] ERROR: {e}")
        raise

# Now let's test detect_wrap_bug which is where the error occurs
def detect_wrap_bug_passlib(secret):
    """Replicate passlib's detect_wrap_bug function"""
    IDENT_2A = b'$2a$'
    # This is the test hash from passlib
    bug_hash = b'$2a$05$ccccccccccccccccccccccccccccccccccccccccCc'

    print(f"[detect_wrap_bug] Testing with IDENT_2A: {IDENT_2A!r}")
    print(f"[detect_wrap_bug] bug_hash: {bug_hash!r}")
    print(f"[detect_wrap_bug] secret: {secret!r} (type: {type(secret)}, length: {len(secret) if isinstance(secret, (str, bytes)) else 'N/A'})")

    try:
        # This is what detect_wrap_bug does:
        # if verify(secret, bug_hash):
        result = _calc_checksum_passlib(secret) == bug_hash[-22:]  # Compare checksum part
        print(f"[detect_wrap_bug] verify result: {result}")
        return result
    except Exception as e:
        print(f"[detect_wrap_bug] ERROR in verify: {e}")
        raise

# Test with our password
print("=== Testing passlib's detect_wrap_bug replication ===")
password = "password123"
print(f"Testing password: {password!r}")

try:
    result = detect_wrap_bug_passlib(password)
    print(f"Result: {result}")
except Exception as e:
    print(f"Failed: {e}")

# Let's also test what happens if we call hashpw directly with the same parameters
print("\n=== Testing direct bcrypt.hashpw call ===")
try:
    # Let's see what config passlib would use
    # From the error, it looks like it's using a config like $2b$12$...
    config = b'$2b$12$XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    print(f"Calling bcrypt.hashpw({password!r}, {config!r})")
    hash_result = bcrypt.hashpw(password, config)
    print(f"Success: {hash_result!r}")
except Exception as e:
    print(f"Direct call failed: {e}")
    import traceback
    traceback.print_exc()

# Let's see what happens if we pass bytes vs string
print("\n=== Testing with bytes vs string ===")
config = b'$2b$12$XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

for pwd_val in ["password123", b"password123"]:
    try:
        print(f"Testing with {type(pwd_val)}: {pwd_val!r}")
        result = bcrypt.hashpw(pwd_val, config)
        print(f"  Success: {result!r}")
    except Exception as e:
        print(f"  Failed: {e}")