import subprocess
import sys
import os

def run_mutation_audit():
    """
    ALGO: Runs Mutmut on the domain layer to identify 'surviving mutants'.
    If a mutant survives (i.e. we delete a line of code and tests still pass),
    it means our test coverage is weak in that specific logic path.
    """
    print("🚀 STARTING MUTATION AUDIT (Domain Layer)...")
    
    # Target path: app/domain/models/
    # Tests path: tests/01_unit (or 08/09)
    target = "app/domain/models"
    test_path = "tests"
    
    try:
        # 1. Run initialization
        # 2. Run mutations
        cmd = [
            "mutmut", "run",
            "--paths-to-mutate", target,
            "--tests-dir", test_path
        ]
        
        # We run it synchronously for the audit report
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 3. Generate HTML report if possible
        subprocess.run(["mutmut", "html"])
        
        print(result.stdout)
        if result.returncode != 0:
            print(f"⚠️ Mutation audit completed with findings or errors. Check mutmut_projects/html")
            
    except FileNotFoundError:
        print("❌ mutmut not found. Please install it with 'pip install mutmut'")
    except Exception as e:
        print(f"❌ Error during mutation audit: {e}")

if __name__ == "__main__":
    run_mutation_audit()
