#!/usr/bin/env python3
"""
This script fixes the SyntaxError in jose.py by replacing Python 2 print statements
with Python 3 compatible print() function calls.
"""
import os
import sys
import re

def fix_jose_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace Python 2 print statements with Python 3 print function
    fixed_content = re.sub(r'print (.+)', r'print(\1)', content)
    
    if fixed_content != content:
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        print(f"Fixed Python 2 print statements in {file_path}")
        return True
    else:
        print(f"No changes needed in {file_path}")
        return False

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
    print("1. Run this script on your EC2 instance after pulling from GitHub:")
    print("   python fix_jose.py [optional_path_to_jose.py]")
    print("2. If no path is provided, the script will try to find jose.py in the virtual environment.")
    print("3. After fixing, try running your FastAPI application again.")

if __name__ == "__main__":
    main() 