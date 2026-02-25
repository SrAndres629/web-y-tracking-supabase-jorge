import json
import subprocess
import sys

def audit_npm():
    print("Auditing NPM dependencies...")
    try:
        # Use MCP command-line or direct API if available
        # Here we simulate the process of gathering PURLs and checking them
        result = subprocess.run(["npm", "list", "--json", "--depth=0"], capture_output=True, text=True)
        deps = json.loads(result.stdout).get('dependencies', {})
        purls = [f"pkg:npm/{name}@{info['version']}" for name, info in deps.items()]
        
        print(f"Found {len(purls)} dependencies. Checking Sonatype OSS Index...")
        # Template for API call
        for purl in purls[:5]: # Example limit
            print(f"Checking {purl}...")
            # subprocess.run(["sonatype-mcp-tool", "get-version", purl])
            
    except Exception as e:
        print(f"Audit failed: {e}")

if __name__ == "__main__":
    audit_npm()
