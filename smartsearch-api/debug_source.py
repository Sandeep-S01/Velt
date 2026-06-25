#!/usr/bin/env python3

# Let's look at the actual bcrypt.py file from passlib to see what's happening
import inspect
import passlib.handlers.bcrypt as bcrypt_module

print("Examining bcrypt.py source...")

# Let's look at the _calc_hash method
if hasattr(bcrypt_module, '_bcrypt'):
    bcrypt_class = getattr(bcrypt_module, '_bcrypt', None)
    if bcrypt_class:
        print(f"Found _bcrypt class: {bcrypt_class}")
        if hasattr(bcrypt_class, '_calc_hash'):
            print("_calc_hash method found")
            try:
                source = inspect.getsource(bcrypt_class._calc_hash)
                print("\n_calc_hash source:")
                print(source[:500])  # First 500 chars
            except Exception as e:
                print(f"Could not get source: {e}")

# Let's also check what the bcrypt attribute is
bcrypt_attr = getattr(bcrypt_module, 'bcrypt', None)
print(f"\nbcrypt module attribute: {bcrypt_attr}")
print(f"Type: {type(bcrypt_attr)}")

if hasattr(bcrypt_attr, '__file__'):
    print(f"bcrypt module file: {bcrypt_attr.__file__}")

# Let's check if there's a hashpw function and what it expects
if hasattr(bcrypt_attr, 'hashpw'):
    print(f"bcrypt.hashpw: {bcrypt_attr.hashpw}")
    try:
        sig = inspect.signature(bcrypt_attr.hashpw)
        print(f"bcrypt.hashpw signature: {sig}")
    except Exception as e:
        print(f"Could not get signature: {e}")

# Let's test what happens when we call bcrypt.hashpw directly with the bcrypt from passlib
print("\n=== Testing bcrypt from passlib module ===")
if bcrypt_attr and hasattr(bcrypt_attr, 'hashpw'):
    try:
        # Test with string
        result = bcrypt_attr.hashpw("password123", b'$2b$12$XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        print(f"String password worked: {result}")
    except Exception as e:
        print(f"String password failed: {e}")

    try:
        # Test with bytes
        result = bcrypt_attr.hashpw(b"password123", b'$2b$12$XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        print(f"Bytes password worked: {result}")
    except Exception as e:
        print(f"Bytes password failed: {e}")

# Now let's see what's happening in the _calc_hash method by looking at the source
print("\n=== Looking at _calc_hash source ===")
try:
    # Find the actual bcrypt implementation class
    for name in dir(bcrypt_module):
        obj = getattr(bcrypt_module, name)
        if hasattr(obj, '__name__') and 'bcrypt' in name.lower() and isinstance(obj, type):
            if hasattr(obj, '_calc_hash'):
                print(f"Found _calc_hash in class {name}")
                try:
                    source = inspect.getsource(obj._calc_hash)
                    print(f"Source of {name}._calc_hash:")
                    print(source)
                    break
                except Exception as e:
                    print(f"Could not get source for {nname}._calc_hash: {e}")
except Exception as e:
    print(f"Error searching for _calc_hash: {e}")