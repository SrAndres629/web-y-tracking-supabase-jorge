import subprocess
import sys
import os
import datetime
import json
import urllib.request
import urllib.error
import argparse
import time
import requests
import re

# =================================================================
# 🛡️ SILICON VALLEY DEPLOYMENT PROTOCOL
# =================================================================
# Robust, Idempotent, and Observable.
# =================================================================

# --- CONFIGURATION (Secrets should ideally be ENV, but preserving existing pattern) ---
CLOUDFLARE_ZONE_ID = "19bd9bdd7abf8f74b4e95d75a41e8583"
CLOUDFLARE_API_KEY = "6094d6fa8c138d93409de2f59a3774cd8795a"
CLOUDFLARE_EMAIL = "Acordero629@gmail.com"
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
# -------------------------------------------------------

class Console:
    """Professional Logging Wrapper"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def log(msg, symbol="🔹"):
        print(f"{symbol} {msg}")

    @staticmethod
    def success(msg):
        print(f"{Console.GREEN}✅ {msg}{Console.ENDC}")

    @staticmethod
    def error(msg):
        print(f"{Console.FAIL}❌ {msg}{Console.ENDC}")

    @staticmethod
    def info(msg):
        print(f"{Console.CYAN}ℹ️  {msg}{Console.ENDC}")

    @staticmethod
    def warning(msg):
        print(f"{Console.WARNING}⚠️  {msg}{Console.ENDC}")

def purge_cloudflare_cache():
    """Purge everything from Cloudflare Edge for jorgeaguirreflores.com"""
    Console.log("Initiating Cloudflare Cache Purge (Standard SV Protocol)...", "🧹")
    url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/purge_cache"
    headers = {
        "X-Auth-Email": CLOUDFLARE_EMAIL,
        "X-Auth-Key": CLOUDFLARE_API_KEY,
        "Content-Type": "application/json"
    }
    data = json.dumps({"purge_everything": True}).encode("utf-8")
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("success"):
                Console.success("CLOUDFLARE CACHE PURGED. Site is now live at the Edge.")
            else:
                Console.error(f"Cloudflare Purge Issue: {result.get('errors')}")
    except Exception as e:
        Console.error(f"Critical Purge Exception: {e}")

def run_cmd(command, cwd=None, exit_on_fail=False):
    """Executes shell command with strict error checking"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        if exit_on_fail:
            Console.error(f"Command failed: {command}\n{result.stderr.strip()}")
            sys.exit(1)
        return False, result.stdout, result.stderr
    return True, result.stdout, result.stderr

def check_environment():
    """Phase 0: Environment Integrity Verification"""
    Console.log("Verifying Execution Environment...", "🔍")
    
    required_modules = ["pytest", "hypothesis", "httpx"]
    missing = []
    
    for mod in required_modules:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    
    if missing:
        Console.error(f"CRITICAL: Missing core engineering mandates: {', '.join(missing)}")
        Console.info("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    Console.success("Environment Integrity Verified (Dependencies Loaded).")

def main():
    parser = argparse.ArgumentParser(description="Silicon Valley Deployment Pipeline")
    parser.add_argument("--force", action="store_true", help="Bypass checks (NOT RECOMMENDED)")
    parser.add_argument("message", nargs="?", default=None, help="Commit message")
    args = parser.parse_args()

    print(f"\n{Console.BOLD}🧠 [NEURAL-SYNC] Initializing Silicon Valley Deployment Protocol...{Console.ENDC}\n")

    # PHASE 0: INTEGRITY CHECK
    check_environment()

    # PHASE 1: THE IRON GATE (Unified Audit)
    Console.log("[1/6] Executing The Iron Gate (Strict Audit)...", "🛡️")
    
    # 🛑 CRITICAL INTEGRITY TESTS (Cannot be bypassed easily)
    integrity_tests = [
        "tests/test_boot_integrity.py",
        "tests/test_template_integrity.py",
        "tests/test_architecture_audit.py"
    ]
    
    if args.force:
        Console.warning("⚠️ SKIPPING GATES: --force flag detected. You are flying blind.")
    else:
        for t_file in integrity_tests:
            Console.log(f"Running Integrity: {t_file}...", "🧪")
            # -W error: Treat ALL warnings as errors (Zero Tolerance)
            test_cmd = f'"{sys.executable}" -m pytest {t_file} -v -W error'
            success, stdout, stderr = run_cmd(test_cmd, cwd=REPO_PATH)
            
            if not success:
                Console.error(f"⛔ DEPLOYMENT BLOCKED: {t_file} failed.")
                Console.info("Reason: Tests, Audits, or Strict Warnings failed.")
                print(f"\n{Console.FAIL}=== AUDIT REPORT START ==={Console.ENDC}")
                print(stdout)
                print(stderr)
                print(f"{Console.FAIL}=== AUDIT REPORT END ==={Console.ENDC}")
                sys.exit(1)
            
        Console.success("The Iron Gate Passed. Zero Defects Detected.")

    # PHASE 1.5: SINCRO-VAL (Verify Global Versioning Logic locally)
    Console.log("[1.5/6] Verifying Sincro-Logic...", "🧬")
    sincro_cmd = f'"{sys.executable}" -m pytest tests/test_synchronicity.py -v'
    success, _, stderr = run_cmd(sincro_cmd, cwd=REPO_PATH)
    if not success:
        Console.error("⛔ SINCRO-VAL FAILED: Asset versioning logic is broken.")
        print(stderr)
        sys.exit(1)

    # PHASE 2: STAGE (Commit Local Changes First)
    Console.log("[2/6] Staging & Committing...", "📦")
    run_cmd("git add .", cwd=REPO_PATH)
    
    success, output, _ = run_cmd("git status --porcelain", cwd=REPO_PATH)
    has_changes = bool(output.strip())
    
    if has_changes or args.force:
        time_str = datetime.datetime.now().strftime('%H:%M')
        msg = args.message if args.message else f"chore: system sync {time_str}"
        
        if not has_changes and args.force:
            msg += " (FORCED)"
            run_cmd(f'git commit --allow-empty -m "{msg}"', cwd=REPO_PATH)
        elif has_changes:
            Console.log(f"Committing source: '{msg}'", "📝")
            run_cmd(f'git commit -m "{msg}"', cwd=REPO_PATH)
    else:
        Console.info("No local changes to commit.")

    # PHASE 3: SYNC & REBASE (Integrate Remote)
    Console.log("[3/6] Synchronizing with Origin...", "📡")
    run_cmd("git fetch origin", cwd=REPO_PATH)
    
    Console.log("[4/6] Rebase Integration...", "🔄")
    # Now we can rebase safely because we are clean
    success, _, stderr = run_cmd("git pull origin main --rebase", cwd=REPO_PATH)
    if not success:
        Console.error("CRITICAL: Rebase Conflict. Resolve manually with 'git status'.")
        sys.exit(1)
    
    # Check if we need to push
    # (Existing logic to check ahead/behind)
    _, local_sha, _ = run_cmd("git rev-parse HEAD", cwd=REPO_PATH)
    _, remote_sha, _ = run_cmd("git rev-parse origin/main", cwd=REPO_PATH)
    
    if local_sha.strip() == remote_sha.strip():
        Console.success("SYSTEM SYNCED. No Ops Required.")
        return
    else:
        Console.log("Local is ahead. Proceeding to Push...", "⬆️")

    # PHASE 6: DEPLOY
    Console.log("[6/6] Injecting into Production...", "🚀")
    success, _, stderr = run_cmd("git push -u origin main", cwd=REPO_PATH)
    
    if success:
        Console.success("✅ DEPLOYMENT SUCCESSFUL")
        Console.log("Validating Edge Cache Purge...", "🧹")
        purge_cloudflare_cache()
        
        # 💎 SILICON VALLEY PRE-WARM: Force global propagation
        try:
            url = "https://jorgeaguirreflores.com"
            Console.log(f"🔥 Pre-Warming Global Edge: {url}", "🔥")
            # Wait a few seconds for Vercel to reflect the push
            time.sleep(10)
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                version_match = re.search(r'\?v=(\d+)', resp.text)
                new_version = version_match.group(1) if version_match else "Unknown"
                Console.success(f"PRODUCCIÓN ACTUALIZADA: Versión Atómica {new_version} activa.")
            else:
                Console.warning(f"Pre-Warm status: {resp.status_code}")
        except Exception as e:
            Console.warning(f"Pre-Warm failed: {e}")

        print(f"\n{Console.GREEN}🌟 System is Live: https://jorgeaguirreflores.com{Console.ENDC}")
    else:
        Console.error(f"Push Failed: {stderr}")

if __name__ == "__main__":
    main()
