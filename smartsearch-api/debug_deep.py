#!/usr/bin/env python3

# Let's look at the _PyBcryptBackend._calc_hash method
import inspect
import passlib.handlers.bcrypt as bcrypt_module

print("Examining _PyBcryptBackend._calc_hash...")

if hasattr(bcrypt_module, '_PyBcryptBackend'):
    backend_class = getattr(bcrypt_module, '_PyBcryptBackend')
    print(f"_PyBcryptBackend class: {backend_class}")

    if hasattr(backend_class, '_calc_hash'):
        method = getattr(backend_class, '_calc_hash')
        print(f"_calc_hash method: {method}")

        try:
            source = inspect.getsource(method)
            print(f"\n_PyBcryptBackend._calc_hash source:")
            print("=" * 50)
            print(source)
            print("=" * 50)
        except Exception as e:
            print(f"Could not get source: {e}")
            # Try to get the source another way
            try:
                import inspect
                lines = inspect.getsourcelines(method)[0]
                print(f"\n_PyBcryptBackend._calc_hash source (via getsourcelines):")
                print("=" * 50)
                for i, line in enumerate(lines):
                    print(f"{i+1:4d}: {line.rstrip()}")
                print("=" * 50)
            except Exception as e2:
                print(f"Also failed with getsourcelines: {e2}")
    else:
        print("_PyBcryptBackend does not have _calc_hash method")
else:
    print("_PyBcryptBackend not found")

# Now let's see how the context gets the handler
print("\n=== Investigating context mechanism ===")
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(f"Context: {pwd_context}")
print(f"Context type: {type(pwd_context)}")

# Let's look at the context's internal structure
attrs = [attr for attr in dir(pwd_context) if not attr.startswith('_') or attr in ['_scheme', '_scheme_map', '_handlers']]
print(f"\nInteresting attributes:")
for attr in attrs:
    if hasattr(pwd_context, attr):
        val = getattr(pwd_context, attr)
        print(f"  {attr}: {val} (type: {type(val)})")

# Let's try to find where the handlers are stored
if hasattr(pwd_context, '_scheme_map'):
    print(f"\n_scheme_map: {pwd_context._scheme_map}")
    if 'bcrypt' in pwd_context._scheme_map:
        handler = pwd_context._scheme_map['bcrypt']
        print(f"Bcrypt handler: {handler}")
        print(f"Handler type: {type(handler)}")
        print(f"Handler class: {handler.__class__}")
        print(f"Handler class MRO: {handler.__class__.__mro__}")

        # Now let's look at the hash method
        if hasattr(handler, 'hash'):
            print(f"\nHandler.hash method: {handler.hash}")
            try:
                source = inspect.getsource(handler.hash)
                print(f"Handler.hash source:")
                print(source)
            except Exception as e:
                print(f"Could not get hash source: {e}")

        # Let's look at _calc_hash if it exists
        if hasattr(handler, '_calc_hash'):
            print(f"\nHandler._calc_hash method: {handler._calc_hash}")
            try:
                source = inspect.getsource(handler._calc_hash)
                print(f"Handler._calc_hash source:")
                print(source)
            except Exception as e:
                print(f"Could not get _calc_hash source: {e}")

# Now let's actually call the hash method and see where it fails
print(f"\n=== Testing the actual call ===")
password = "password123"
print(f"Password: {password!r}")

try:
    print("Calling pwd_context.hash(password)...")
    result = pwd_context.hash(password)
    print(f"SUCCESS: {result}")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    print("Full traceback:")
    traceback.print_exc()

    # Let's also try to manually trace what happens
    print("\n=== Manual tracing ===")
    if hasattr(pwd_context, '_scheme_map') and 'bcrypt' in pwd_context._scheme_map:
        handler = pwd_context._scheme_map['bcrypt']
        print(f"Using handler: {handler}")
        try:
            print("Calling handler.hash(password)...")
            result = handler.hash(password)
            print(f"SUCCESS: {result}")
        except Exception as e2:
            print(f"Handler.hash also failed: {e2}")
            traceback.print_exc()

            # Let's see if we can call the underlying methods
            if hasattr(handler, '_calc_hash'):
                print("\nTrying to understand what _calc_hash expects...")
                try:
                    sig = inspect.signature(handler._calc_hash)
                    print(f"_calc_hash signature: {sig}")

                    # Let's see what the method actually is
                    print(f"_calc_hash method: {handler._calc_hash}")
                    print(f"_calc_hash type: {type(handler._calc_hash)}")

                except Exception as e3:
                    print(f"Could not get _calc_hash signature: {e3}")
else:
    print("Could not find bcrypt handler in scheme map")