#!/usr/bin/env python3
"""
This script fixes multiple syntax issues in jose.py for Python 3.12 compatibility:
1. Adds parentheses to print statements (Python 2 to 3 conversion)
2. Fixes trailing commas in function calls that cause syntax errors
3. Specifically handles the indentation issue around line 546-547
"""
import os
import sys
import re

def fix_jose_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # First pass: fix print statements
    for i in range(len(lines)):
        # Add parentheses to print statements
        if re.match(r'^\s*print\s+[^(]', lines[i]):
            lines[i] = re.sub(r'print\s+(.+)', r'print(\1)', lines[i])
    
    # Second pass: fix the specific problematic area around line 546-547
    for i in range(len(lines)):
        # If this is a line containing the problematic decrypt statement
        if 'decrypt(deserialize_compact(jwt)' in lines[i]:
            # Remove trailing comma if present
            lines[i] = lines[i].replace("{'k':key},", "{'k':key}")
            
            # If this line ends with a parenthesis and the next line starts with 'validate_claims'
            if i+1 < len(lines) and 'validate_claims' in lines[i+1]:
                # This is the case with the indentation error - merge the lines
                combined_line = lines[i].rstrip('\n').rstrip(')') + ' ' + lines[i+1].lstrip()
                lines[i] = combined_line
                lines[i+1] = ''  # Clear the next line since we merged it
    
    # Write the fixed content back
    with open(file_path, 'w') as f:
        f.writelines([line for line in lines if line])
    
    print(f"Fixed syntax issues in {file_path}")
    return True

def main():
    if len(sys.argv) > 1:
        jose_path = sys.argv[1]
    else:
        # Try to find jose.py in the site-packages
        venv_path = os.path.join(os.getcwd(), 'venv')
        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        site_packages = os.path.join(venv_path, 'lib', python_version, 'site-packages')
        jose_path = os.path.join(site_packages, 'jose.py')
    
    if fix_jose_file(jose_path):
        print("Fix applied successfully!")
    else:
        print("Failed to apply fix or no fix needed.")
    
    print("\nInstructions:")
    print("1. Run this script on your EC2 instance:")
    print("   python fix_jose_indentation.py [optional_path_to_jose.py]")
    print("2. After fixing, try running your FastAPI application again.")

if __name__ == "__main__":
    main() 