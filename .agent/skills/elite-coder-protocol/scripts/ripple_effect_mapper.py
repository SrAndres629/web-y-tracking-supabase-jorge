import sys
import subprocess
import os

def run_ripple_effect_check(search_term):
    """
    Mathematical analyzer for Neuron 3: Global Integrity (The Ripple Effect).
    Uses ripgrep (or subprocess grep) to ensure no entity is modified
    without updating its dependent references across the entire ecosystem.
    """
    print(f"🌍 [Neuron 3] Initiating Global Ripple Effect Mapper for: '{search_term}'")
    
    # Define the jurisdiction of the ripple effect (The entire MAS)
    search_dirs = ["app", "api", "tests", "static"]
    
    anomalies_found = 0
    
    for directory in search_dirs:
        if not os.path.exists(directory):
            continue
            
        # Recursive grep search for the exact term
        cmd = ["grep", "-rnw", directory, "-e", search_term]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                print(f"   -> 🚨 Found {len(lines)} dependent references in `{directory}/`")
                for line in lines[:5]:  # Print first 5 for triage
                    print(f"      {line[:100]}...")
                if len(lines) > 5:
                    print(f"      ... and {len(lines) - 5} more.")
                anomalies_found += len(lines)
        except Exception as e:
            print(f"⚠️ Error scanning {directory}: {e}")

    if anomalies_found == 0:
        print(f"✅ [Neuron 3] Safe to modify. No trailing dependencies found for '{search_term}'.")
    else:
        print(f"\n🛑 [Neuron 3] CAUTION! Found {anomalies_found} global references.")
        print("   -> VERDICT: You MUST update all these references iteratively before claiming task completion.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ripple_effect_mapper.py <ClassName_or_FunctionName>")
        sys.exit(1)
        
    term = sys.argv[1]
    run_ripple_effect_check(term)
