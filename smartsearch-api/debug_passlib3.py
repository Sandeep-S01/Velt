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

# Let's look at the internal handlers
print(f"Internal handlers type: {type(pwd_context._handlers)}")
if hasattr(pwd_context._handlers, '__len__'):
    print(f"Number of handlers: {len(pwd_context._handlers)}")
    for i, handler in enumerate(pwd_context._handlers):
        print(f"  Handler {i}: {type(handler)} - {handler}")
        if hasattr(handler, '__class__'):
            print(f"    Class: {handler.__class__}")
            print(f"    Module: {handler.__class__.__module__}")