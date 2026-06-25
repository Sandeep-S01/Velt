#!/usr/bin/env python3

# Let's look at the context where detect_wrap_bug is called
import passlib.handlers.bcrypt as bcrypt_module

source_file = bcrypt_module.__file__
print(f"Reading from: {source_file}")

with open(source_file, 'r') as f:
    lines = f.readlines()

# Look for the context around line 421
print("Context around line 421 (where detect_wrap_bug is called):")
for i in range(max(0, 421-10), min(len(lines), 421+10)):
    marker = ">>> " if i == 420 else "    "  # Line 421 is index 420 (0-based)
    print(f"{marker}{i+1:4d}: {lines[i].rstrip()}")

# Let's get a bit more context to see the function
print("\nLooking for the function that contains this call...")
in_function = False
function_lines = []
function_name = ""

for i, line in enumerate(lines):
    if line.strip().startswith('def '):
        # End previous function
        if in_function and function_lines:
            print(f"\nFunction {function_name} ended at line {i}")
            in_function = False
            function_lines = []

        # Start new function
        if 'detect_wrap_bug' not in line:  # We're not looking for detect_wrap_bug itself
            in_function = True
            function_name = line.split('def ')[1].split('(')[0].strip()
            function_lines = [line]
        else:
            # We found detect_wrap_bug, let's see what calls it
            in_function = False

    elif in_function:
        function_lines.append(line)
        # Check if this line calls detect_wrap_bug
        if 'detect_wrap_bug' in line:
            print(f"\nFound call to detect_wrap_bug in function {function_name} at line {i+1}:")
            print(f"    {line.rstrip()}")
            # Show some context
            print(f"  Context:")
            for j in range(max(0, i-5), min(len(lines), i+6)):
                marker = ">>> " if j == i else "    "
                print(f"    {marker}{j+1:4d}: {lines[j].rstrip()}")
            break

# Let's also look at the _finalize_backend_mixin function where the error is happening
print("\n" + "="*60)
print("Looking for _finalize_backend_mixin function...")

for i, line in enumerate(lines):
    if line.strip().startswith('def _finalize_backend_mixin'):
        print(f"Found _finalize_backend_mixin at line {i+1}:")
        print(f"    {line.rstrip()}")
        # Show the function
        j = i + 1
        indent = len(line) - len(line.lstrip())
        while j < len(lines):
            line_j = lines[j]
            if line_j.strip() and not line_j.startswith(' ') and not line_j.startswith('\t'):
                # End of function
                break
            print(f"    {j+1:4d}: {line_j.rstrip()}")
            j += 1
        break