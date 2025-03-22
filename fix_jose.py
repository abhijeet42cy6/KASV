#!/usr/bin/env python
"""
Script to fix python-jose compatibility with Python 3.12
This script finds and updates old-style print statements in jose.py
"""
import os
import sys
import re
import site
from pathlib import Path

def fix_jose_print_statements():
    """
    Find and fix print statements in jose.py that are incompatible with Python 3.12
    """
    print("Searching for python-jose installation...")
    
    # Find site-packages directory
    site_packages = site.getsitepackages()
    
    jose_file_paths = []
    for sp in site_packages:
        possible_paths = [
            Path(sp) / "jose.py",
            Path(sp) / "jose" / "jose.py",
            Path(sp) / "jose" / "__init__.py",
        ]
        
        for path in possible_paths:
            if path.exists():
                jose_file_paths.append(path)
    
    if not jose_file_paths:
        print("Could not find python-jose installation. Make sure it's installed.")
        return False
    
    fixed_files = 0
    for jose_path in jose_file_paths:
        print(f"Checking {jose_path}...")
        
        # Read the file
        with open(jose_path, 'r') as f:
            content = f.read()
        
        # Check for Python 2 style print statements
        # Regular expression for Python 2 style print (not inside comments)
        pattern = r'(?<!\#.*)(?<!\")print\s+([^(].*?)(?=$|\n)'
        
        # Find matches
        matches = re.findall(pattern, content)
        if not matches:
            print(f"No old-style print statements found in {jose_path}")
            continue
        
        print(f"Found {len(matches)} old-style print statements in {jose_path}")
        
        # Replace old print statements with new style
        new_content = re.sub(pattern, r'print(\1)', content)
        
        # Write the updated content back to the file
        try:
            with open(jose_path, 'w') as f:
                f.write(new_content)
            print(f"Successfully updated {jose_path}")
            fixed_files += 1
        except Exception as e:
            print(f"Error updating {jose_path}: {e}")
            print("You might need to run this script with administrator privileges")
    
    if fixed_files:
        print(f"Successfully fixed {fixed_files} files.")
        return True
    else:
        print("No files were modified.")
        return False

if __name__ == "__main__":
    success = fix_jose_print_statements()
    if success:
        print("python-jose has been fixed for Python 3.12 compatibility.")
    else:
        print("Failed to fix python-jose. You may need to edit jose.py manually.") 