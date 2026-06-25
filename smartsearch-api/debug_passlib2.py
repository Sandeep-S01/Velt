#!/usr/bin/env python3

# Let's see what's in the passlib.handlers.bcrypt module
import passlib.handlers.bcrypt as bcrypt_module

print("Attributes in passlib.handlers.bcrypt:")
attrs = [attr for attr in dir(bcrypt_module) if not attr.startswith('_')]
for attr in attrs:
    print(f"  {attr}")

# Let's see what the main class is
print(f"\nModule: {bcrypt_module}")