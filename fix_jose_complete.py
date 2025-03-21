#!/usr/bin/env python3
"""
This script fixes multiple syntax issues in jose.py for Python 3.12 compatibility:
1. Adds parentheses to print statements (Python 2 to 3 conversion)
2. Fixes trailing commas in function calls that cause syntax errors
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
    
    # Fix specific problematic line with trailing comma
    fixed_content = fixed_content.replace(
        "print(decrypt(deserialize_compact(jwt), {'k':key},)", 
        "print(decrypt(deserialize_compact(jwt), {'k':key}))"
    )
    
    # Fix any other similar patterns with trailing commas in function calls
    fixed_content = re.sub(r'\(([^()]*),\)', r'(\1)', fixed_content)
    
    if fixed_content != content:
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        print(f"Fixed syntax issues in {file_path}")
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
    print("1. Run this script on your EC2 instance:")
    print("   python fix_jose_complete.py [optional_path_to_jose.py]")
    print("2. If no path is provided, the script will try to find jose.py in the virtual environment.")
    print("3. After fixing, try running your FastAPI application again.")

if __name__ == "__main__":
    main() 