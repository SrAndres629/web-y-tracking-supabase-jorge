import subprocess
import sys
import os
import datetime

# --- CONFIGURATION ---
# Use the current directory as base path to avoid hardcoded "monorepo" issues
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
REMOTE_BRANCH = "origin/main"
# ---------------------

def run_command(command, cwd=None, check=True, silent=False):
    """Run a shell command and return (success, stdout, stderr)."""
    if not silent:
        print(f"🔹 Executing: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        success = result.returncode == 0
        if not success and check:
            print(f"❌ Error in '{command}':\n{result.stderr.strip()}")
        return success, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        print(f"❌ Critical Exception: {e}")
        return False, "", str(e)

def get_git_hash(ref, cwd):
    success, out, _ = run_command(f"git rev-parse {ref}", cwd=cwd, check=False, silent=True)
    return out if success else None

def main():
    print("\n🧠 [VERCEL-SYNC] Initializing Optimized Deployment Protocol...\n")
    
    # 1. Health Check: Fetch Remote State
    print("📡 1. Synchronizing with Registry...")
    success, _, _ = run_command("git fetch origin", cwd=REPO_PATH)
    
    # 2. Pull (Linear History Strategy)
    print("🔄 2. Integrating Latest Code...")
    success, _, stderr = run_command("git pull origin main --rebase", cwd=REPO_PATH, check=False)
    if not success:
        if "conflict" in stderr.lower():
            print("🚨 CRITICAL: Merge Conflict Detected.")
            return

    # 3. Stage Changes
    print("📦 3. Staging Local Logic...")
    run_command("git add .", cwd=REPO_PATH)

    # Check for meaningful changes
    success, status_porcelain, _ = run_command("git status --porcelain", cwd=REPO_PATH, silent=True)
    has_changes = bool(status_porcelain.strip())
    
    if not has_changes:
        local_sha = get_git_hash("HEAD", REPO_PATH)
        remote_sha = get_git_hash(REMOTE_BRANCH, REPO_PATH)
        if local_sha == remote_sha:
            print("✅ SYSTEM SYNCED. Local & Remote are in parity.")
            return
        print(f"⬆️  Pending Push: Local ({local_sha[:7]}) > Remote")
    else:
        # 4. Smart Commit
        commit_msg = sys.argv[1] if len(sys.argv) > 1 else f"feat: optimization sync {datetime.datetime.now().strftime('%H:%M')}"
        print(f"📝 4. Committing: '{commit_msg}'")
        success, _, _ = run_command(f'git commit -m "{commit_msg}"', cwd=REPO_PATH)
        if not success: return

    # 5. Atomic Push & Vercel Trigger
    print("🚀 5. Pushing to GitHub & Deploying to Vercel...")
    success, stdout, stderr = run_command("git push -u origin main", cwd=REPO_PATH)
    
    if success:
        print("\n✅ DEPLOYMENT INITIATED")
        print(f"🔗 Live at: https://web-y-tracking-supabase-jorge.vercel.app")
        print("� Monitoring: vercel logs")
    else:
        print(f"\n❌ SYNC FAILED: {stderr}")

if __name__ == "__main__":
    main()
