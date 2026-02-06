
import asyncio
import sys
import json
from app.diagnostics import run_full_diagnostics

# Mock Vercel for accurate env loading if needed
import os
os.environ["VERCEL"] = "1" 

def main():
    print("🚀 STARTED: Robust Connection Verification")
    print("------------------------------------------")
    
    report = run_full_diagnostics()
    
    # Pretty print
    print(json.dumps(report, indent=2))
    
    # Exit codes
    db_status = report.get("database", {}).get("status")
    redis_status = report.get("redis", {}).get("status")
    
    if db_status == "error" or redis_status == "error":
        print("\n❌ FAILED: Critical errors detected.")
        sys.exit(1)
        
    if db_status == "skipped":
        print("\n⚠️ WARNING: Database check skipped (secrets missing).")
    
    print("\n✨ Done.")

if __name__ == "__main__":
    main()
