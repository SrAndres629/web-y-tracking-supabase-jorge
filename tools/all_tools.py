
import re
import sys
import difflib

def smart_patch(file_path, search_pattern, replacement, dry_run=True):
    with open(file_path, 'r') as f:
        content = f.read()

    # Normalize whitespace for matching (simple version)
    search_norm = ' '.join(search_pattern.split())
    
    # Simple direct search first
    if search_pattern in content:
        print(f'Exact match found in {file_path}.')
        new_content = content.replace(search_pattern, replacement)
    else:
        # Fuzzy line-based search? Or just normalized?
        # Let's try to find the block by stripping lines
        lines = content.splitlines()
        search_lines = search_pattern.splitlines()
        
        # This is complex to implement robustly in one go without libraries.
        # Fallback to simple replace for now, but report failure clearly.
        print(f'Pattern not found exactly in {file_path}.')
        return False

    if not dry_run:
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f'Patched {file_path}.')
    else:
        print('Dry run successful.')
    return True

if __name__ == '__main__':
    # Usage: python3 tools/smart_patch.py file search_file replace_file [apply]
    if len(sys.argv) < 4:
        print('Usage: python3 tools/smart_patch.py <target_file> <search_pattern_file> <replacement_file> [apply]')
        sys.exit(1)
        
    target = sys.argv[1]
    with open(sys.argv[2], 'r') as f: search = f.read()
    with open(sys.argv[3], 'r') as f: replace = f.read()
    apply = len(sys.argv) > 4 and sys.argv[4] == 'apply'
    
    smart_patch(target, search, replace, not apply)

import sys

def main():
    if len(sys.argv) < 3:
        print('Usage: python3 tools/log_strip.py <logfile> <lines> [grep_pattern]')
        sys.exit(1)
    file_path = sys.argv[1]
    n = int(sys.argv[2])
    pattern = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        # Take last N lines
        subset = lines[-n:]
        
        # Filter
        if pattern:
            subset = [l for l in subset if pattern in l]
            
        print(''.join(subset))
    except FileNotFoundError:
        print(f'File {file_path} not found.')

if __name__ == '__main__':
    main()
