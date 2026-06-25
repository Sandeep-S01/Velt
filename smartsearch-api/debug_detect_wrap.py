#!/usr/bin/env python3

# Let's look at the actual detect_wrap_bug function from passlib
import passlib.handlers.bcrypt as bcrypt_module

# Read the source and find the detect_wrap_bug function
source_file = bcrypt_module.__file__
print(f"Reading from: {source_file}")

with open(source_file, 'r') as f:
    content = f.read()

# Find the detect_wrap_bug function
import re
pattern = r'def detect_wrap_bug\([^)]*\):\s*([^}]*?(?=\n\s*def|\n\s*class|\Z))'
matches = re.findall(pattern, content, re.DOTALL)

if matches:
    print("Found detect_wrap_bug function:")
    print("=" * 50)
    for i, match in enumerate(matches):
        print(f"Match {i+1}:")
        print(match.strip())
        print("-" * 30)
else:
    # Try a simpler approach
    lines = content.split('\n')
    in_function = False
    function_lines = []

    for line in lines:
        if line.strip().startswith('def detect_wrap_bug'):
            in_function = True
            function_lines = [line]
        elif in_function:
            if line.startswith('def ') or line.startswith('class ') or (not line.startswith(' ') and line.strip()):
                # End of function
                break
            else:
                function_lines.append(line)

    if function_lines:
        print("Found detect_wrap_bug function:")
        print("=" * 50)
        for line in function_lines:
            print(line)
        print("=" * 50)
    else:
        print("Could not find detect_wrap_bug function")

# Let's also look for the exact error line
print("\nLooking for the specific error line...")
if 'if verify(secret, bug_hash):' in content:
    print("Found the vulnerable line: if verify(secret, bug_hash):")
    # Show context
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'if verify(secret, bug_hash):' in line:
            print(f"\nContext around line {i+1}:")
            for j in range(max(0, i-3), min(len(lines), i+4)):
                marker = ">>> " if j == i else "    "
                print(f"{marker}{j+1:4d}: {lines[j]}")
            break

# Let's also check what the bug_hash constant is
print("\nLooking for bug_hash or TEST_HASH...")
if 'TEST_HASH_2A' in content:
    print("Found TEST_HASH_2A")
elif 'bug_hash' in content.lower():
    print("Found something with 'bug_hash' in it")

# Let's look at the constants section
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'IDENT_2A' in line or 'TEST_HASH' in line or '_2A' in line and ('=' in line):
        print(f"Line {i+1}: {line}")