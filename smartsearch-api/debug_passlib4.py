#!/usr/bin/env python3

# Let's check what classes are in passlib.handlers.bcrypt
import passlib.handlers.bcrypt as bcrypt_module

print("Looking for handler classes...")
for name in dir(bcrypt_module):
    attr = getattr(bcrypt_module, name)
    if isinstance(attr, type):
        print(f"  Class: {name}")

# Let's also check what's exported
print(f"\n__all__: {getattr(bcrypt_module, '__all__', 'Not defined')}")

# Let's see if we can find the bcrypt handler class by looking at the context
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print(f"\nContext schemes: {pwd_context.schemes()}")

# Let's look at the internal handlers using the correct attribute
print(f"Handler attribute: {getattr(pwd_context, 'handler', 'No handler attr')}")
if hasattr(pwd_context, 'handler'):
    print(f"Handler: {pwd_context.handler}")
    print(f"Handler type: {type(pwd_context.handler)}")

# Let's look at the schemes map
if hasattr(pwd_context, '_scheme_map'):
    print(f"Scheme map: {pwd_context._scheme_map}")
    for name, handler in pwd_context._scheme_map.items():
        print(f"  Scheme '{name}': {type(handler)} - {handler}")

# Let's try to get the bcrypt handler directly
if hasattr(pwd_context, '_scheme_map') and 'bcrypt' in pwd_context._scheme_map:
    bcrypt_handler = pwd_context._scheme_map['bcrypt']
    print(f"\nBcrypt handler: {bcrypt_handler}")
    print(f"Bcrypt handler type: {type(bcrypt_handler)}")

    # Let's see what methods it has
    print("Methods on bcrypt handler:")
    methods = [m for m in dir(bcrypt_handler) if not m.startswith('_')]
    for method in methods[:10]:  # Show first 10
        print(f"  {method}")
    if len(methods) > 10:
        print(f"  ... and {len(methods) - 10} more")

    # Let's look at the hash method specifically
    if hasattr(bcrypt_handler, 'hash'):
        print(f"\nHash method: {bcrypt_handler.hash}")