#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRIPT: audit_css_classes.py
AUTHOR: Antigravity
DESCRIPTION:
    Audits the CSS classes used in HTML templates against the ones defined in the CSS source files.
    This version is improved to use the full Tailwind output for a more accurate audit.

USAGE:
    npm run audit:css
    python scripts/audit_css_classes.py
"""

import os
import re
from pathlib import Path

# --- CONFIGURATION ---
TEMPLATE_DIRS = ['api/templates']
CSS_AUDIT_FILE = 'static/dist/css/app.audit.css'
IGNORED_PREFIXES = ['fa-', 'fas-', 'far-', 'fab-']

# --- MAIN LOGIC ---

def find_html_files(directories):
    """Finds all HTML files in a list of directories."""
    files_found = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.html'):
                    files_found.append(os.path.join(root, file))
    return files_found

def extract_classes_from_html(files):
    """Extracts all unique class names from a list of HTML files, ignoring template syntax."""
    used_classes = set()
    # Improved regex to capture classes within class attributes, handles more characters
    class_regex = re.compile(r'class="([^"]+)"')
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove Jinja2 comments and tags before parsing
                content = re.sub(r'\{#.*?#\}', '', content, flags=re.DOTALL)
                content = re.sub(r'\{\%.*?\%\}', '', content)
                content = re.sub(r'\{\{.*?\}\}', '', content)

                matches = class_regex.findall(content)
                for match in matches:
                    # Split space-separated classes
                    classes = match.split()
                    for cls in classes:
                        # Clean up and add to set
                        cleaned_cls = cls.strip()
                        if cleaned_cls:
                            used_classes.add(cleaned_cls)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    return used_classes

def extract_classes_from_css(css_file):
    """Extracts all unique class names from a single CSS file using a more robust regex."""
    defined_classes = set()
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # This regex is much more robust. It looks for a class selector that starts with a dot,
            # and it handles pseudo-classes and pseudo-elements.
            # It also handles special characters used by Tailwind.
            class_regex = re.compile(r'\.([a-zA-Z0-9\\/:-_\[\]\.\%]+)(?=[^\{]*?\{)')
            
            matches = class_regex.findall(content)
            for match in matches:
                # The class might have pseudo-elements attached, e.g., 'hover:bg-blue-500::before'
                # We strip pseudo-elements off
                cleaned_match = match.split('::')[0].replace('\\', '')
                defined_classes.add(cleaned_match)
    except FileNotFoundError:
        print(f"Audit file not found: {css_file}")
        print("Please run 'npm run audit:css' first.")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return defined_classes

def main():
    """Main function to run the audit."""
    print("--- 🔍 Starting CSS Class Audit (Final Version) ---")
    
    # 1. Find HTML files
    html_files = find_html_files(TEMPLATE_DIRS)
    print(f"Found {len(html_files)} HTML files to audit.")
    
    # 2. Extract classes
    used_classes = extract_classes_from_html(html_files)
    print(f"Found {len(used_classes)} unique classes used in templates.")
    
    defined_classes = extract_classes_from_css(CSS_AUDIT_FILE)
    print(f"Found {len(defined_classes)} unique classes defined in the audit CSS file.")
    
    # 3. Compare and find missing classes
    missing_classes = set()
    for cls in used_classes:
        if cls not in defined_classes:
            # Ignore FontAwesome classes
            if any(cls.startswith(prefix) for prefix in IGNORED_PREFIXES):
                continue
            # This is a simple heuristic: if a class contains '[', it's likely a JIT class from tailwind
            if '[' not in cls and ']' not in cls:
                missing_classes.add(cls)

    # 4. Report results
    if not missing_classes:
        print("\n--- ✅ Audit Passed: All classes appear to be defined! ---")
    else:
        print(f"\n--- 🚨 Audit Failed: Found {len(missing_classes)} potentially undefined classes ---")
        for i, cls in enumerate(sorted(list(missing_classes))):
            print(f"  {i+1}. {cls}")
            
    print("\n--- Audit Complete ---")

if __name__ == '__main__':
    main()
