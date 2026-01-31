import pkg_resources
import sys
import os

def audit_deps():
    print("🔍 INITIATING DEPENDENCY AUDIT...")
    
    req_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'requirements.txt')
    
    if not os.path.exists(req_path):
        print("❌ Error: requirements.txt not found.")
        sys.exit(1)
        
    print(f"📄 Reading {req_path}")
    
    with open(req_path, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"📦 Found {len(requirements)} requirements.")
    
    # Simple conflict check (duplicate packages)
    packages = {}
    conflicts = False
    
    for req in requirements:
        # Very basic parsing, handles 'package>=version'
        pkg_name = req.split('>=')[0].split('==')[0].split('<')[0].strip().lower()
        # Remove extras like [fastapi]
        if '[' in pkg_name:
            pkg_name = pkg_name.split('[')[0]
            
        if pkg_name in packages:
            print(f"⚠️  WARNING: Duplicate requirement found for '{pkg_name}'")
            conflicts = True
        packages[pkg_name] = req
        print(f"   - {req}")
        
    if conflicts:
        print("🟡 Audit finished with warnings (Duplicates detected).")
    else:
        print("✅ Audit finished. No obvious conflicts in definition.")

if __name__ == "__main__":
    audit_deps()
