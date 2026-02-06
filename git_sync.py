import subprocess
import sys
import os
import datetime
import json
import urllib.request
import urllib.error
import argparse

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

def main():
    parser = argparse.ArgumentParser(description="Silicon Valley Deployment Pipeline")
    parser.add_argument("--force", action="store_true", help="Force push even if clean")
    parser.add_argument("message", nargs="?", default=None, help="Commit message")
    args = parser.parse_args()

    print(f"\n{Console.BOLD}🧠 [VERCEL-SYNC] Initializing Optimized Deployment Protocol...{Console.ENDC}\n")

    # 1. SYNC
    Console.log("Synchronizing with Registry...", "📡")
    run_cmd("git fetch origin", cwd=REPO_PATH)
    
    # 2. PULL REBASE (Avoid Merge Bubbles)
    Console.log("Integrating Latest Code...", "🔄")
    success, _, stderr = run_cmd("git pull origin main --rebase", cwd=REPO_PATH, exit_on_fail=False)
    if not success and "conflict" in stderr.lower():
        Console.error("CRITICAL: Merge Conflict Detected. Resolve manually.")
        sys.exit(1)

    # 3. STAGE
    Console.log("Staging Local Logic...", "📦")
    run_cmd("git add .", cwd=REPO_PATH)

    # 4. CHECK STATUS
    success, output, _ = run_cmd("git status --porcelain", cwd=REPO_PATH)
    has_changes = bool(output.strip())

    if not has_changes and not args.force:
        # Check if local is ahead of remote
        s_local, local_sha, _ = run_cmd("git rev-parse HEAD", cwd=REPO_PATH)
        s_remote, remote_sha, _ = run_cmd("git rev-parse origin/main", cwd=REPO_PATH)
        
        if local_sha.strip() == remote_sha.strip():
            Console.success("SYSTEM SYNCED. No changes to deploy.")
            Console.info("Use --force to trigger empty commit & deploy.")
            return
        else:
            Console.log(f"Pending Push: Local is ahead of Remote.", "⬆️")
    
    # 5. COMMIT (If needed)
    if has_changes or args.force:
        time_str = datetime.datetime.now().strftime('%H:%M')
        default_msg = f"feat: optimization sync {time_str}"
        msg = args.message if args.message else default_msg
        
        if not has_changes and args.force:
            msg += " (FORCED)"
            Console.log(f"Forcing Empty Commit: '{msg}'", "⚠️")
            run_cmd(f'git commit --allow-empty -m "{msg}"', cwd=REPO_PATH, exit_on_fail=True)
        elif has_changes:
            Console.log(f"Committing: '{msg}'", "📝")
            run_cmd(f'git commit -m "{msg}"', cwd=REPO_PATH, exit_on_fail=True)

    # 6. PUSH
    Console.log("Pushing to GitHub & Triggering Vercel...", "🚀")
    success, _, stderr = run_cmd("git push -u origin main", cwd=REPO_PATH)
    
    if success:
        Console.success("DEPLOYMENT INITIATED")
        Console.log("Waiting for Vercel Build...", "⏳")
        print(f"🔗 Live at: https://jorgeaguirreflores.com")
        
        # 7. CLOUDFLARE PURGE
        purge_cloudflare_cache()
    else:
        Console.error(f"Push Failed: {stderr}")

if __name__ == "__main__":
    main()
