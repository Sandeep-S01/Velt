#!/usr/bin/env python3

# Let's look at the actual bcrypt.py file from passlib to see what's happening
import inspect
import passlib.handlers.bcrypt as bcrypt_module

print("Examining bcrypt.py source...")
print(f"Module file: {bcrypt_module.__file__}")

# Let's read the source file directly
try:
    with open(bcrypt_module.__file__, 'r') as f:
        content = f.read()
        print(f"\nFile length: {len(content)} characters")

        # Let's look for the _calc_hash method
        import re
        # Find class definitions
        class_pattern = r'class\s+(\w+)\s*\([^)]*\):'
        classes = re.findall(class_pattern, content)
        print(f"Classes found: {classes}")

        # Look for _calc_hash method
        calc_hash_pattern = r'def\s+_calc_hash\s*\([^)]*\):'
        calc_hash_matches = re.findall(calc_hash_pattern, content)
        print(f"_calc_hash method matches: {len(calc_hash_matches)}")

        if calc_hash_matches:
            # Let's get a larger chunk around the method
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '_calc_hash' in line and 'def ' in line:
                    print(f"\nFound _calc_hash at line {i+1}:")
                    # Print 20 lines around it
                    start = max(0, i - 5)
                    end = min(len(lines), i + 15)
                    for j in range(start, end):
                        marker = ">>> " if j == i else "    "
                        print(f"{marker}{j+1:4d}: {lines[j]}")
                    break
except Exception as e:
    print(f"Error reading file: {e}")
    import traceback
    traceback.print_exc()

# Let's also check what the bcrypt class actually is
print(f"\n=== Examining the bcrypt class ===")
bcrypt_class = getattr(bcrypt_module, 'bcrypt', None)
print(f"bcrypt class: {bcrypt_class}")
print(f"bcrypt class type: {type(bcrypt_class)}")

if bcrypt_class and hasattr(bcrypt_class, '__mro__'):
    print(f"MRO: {bcrypt_class.__mro__}")

# Let's see if it's a subclass of something
if bcrypt_class:
    for cls in bcrypt_class.__mro__:
        print(f"  {cls}")

# Let's look for the actual implementation
print(f"\n=== Looking for backend implementation ===")
# From earlier, we saw _PyBcryptBackend class
if hasattr(bcrypt_module, '_PyBcryptBackend'):
    backend_class = getattr(bcrypt_module, '_PyBcryptBackend')
    print(f"Found _PyBcryptBackend: {backend_class}")
    if hasattr(backend_class, '_calc_hash'):
        try:
            source = inspect.getsource(backend_class._calc_hash)
            print(f"\n_PyBcryptBackend._calc_hash source:")
            print(source)
        except Exception as e:
            print(f"Could not get source: {e}")
            import traceback
            traceback.print_exc()

# Let's test the actual call that's failing
print(f"\n=== Testing the actual failing scenario ===")
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Let's manually call what happens in the context
print("Getting bcrypt handler from context...")
if hasattr(pwd_context, '_scheme_map') and 'bcrypt' in pwd_context._scheme_map:
    handler = pwd_context._scheme_map['bcrypt']
    print(f"Handler: {handler}")
    print(f"Handler type: {type(handler)}")

    # Let's see what class it is
    print(f"Handler class: {handler.__class__}")
    print(f"Handler class module: {handler.__class__.__module__}")

    # Now let's call hash and see what happens
    password = "password123"
    print(f"\nCalling handler.hash('{password}')...")
    try:
        result = handler.hash(password)
        print(f"Success: {result}")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()

        # Let's also try to call _calc_hash directly if we can access it
        if hasattr(handler, '_calc_hash'):
            print("\nTrying to call _calc_hash directly...")
            try:
                # We need to know what parameters it takes
                import inspect
                sig = inspect.signature(handler._calc_hash)
                print(f"_calc_hash signature: {sig}")
                # This is tricky because we need to know what to pass
            except Exception as e2:
                print(f"Could not get signature: {e2}")
else:
    print("Could not find bcrypt handler in context scheme map")