import os
import time
import subprocess
import datetime
import shutil
import hashlib
import json

# Configuration
AI_DIR = os.path.dirname(os.path.abspath(__file__))
MOTOR_DIR = os.path.join(AI_DIR, "motor")
SENSORY_DIR = os.path.join(AI_DIR, "sensory")
MEMORY_DIR = os.path.join(AI_DIR, "memory")
HASH_FILE = os.path.join(MEMORY_DIR, "codebase_hash.json")

# The Recursive Audit Prompt
AUDIT_TASK_TEMPLATE = """# TASK: AUTONOMOUS SUPERVISOR - SYSTEM IMPROVEMENT LOOP

**Objective:** Scan the CHANGED FILES and the latest sensory reports to find bugs, tech debt, or optimization opportunities.

**Changed Files to Analyze:**
{changed_files}

**Action Required:**
If you find something to fix, generate a TASK file in the standard format.
"""

def log(msg, symbol="👁️"):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {symbol} [SUPERVISOR] {msg}")

def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""

def get_codebase_diff():
    """Returns list of changed files since last scan"""
    # Define interesting extensions and exclude dirs
    extensions = {".py", ".md", ".json", ".html", ".js", ".css"}
    exclude_dirs = {".ai", "__pycache__", ".git", "venv", "node_modules"}

    current_hashes = {}
    PROJECT_ROOT = os.path.dirname(AI_DIR) # Assumes .ai is in root

    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, PROJECT_ROOT)
                current_hashes[rel_path] = get_file_hash(path)

    # Load old hashes
    old_hashes = {}
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            old_hashes = json.load(f)

    # Find changes
    changed = []
    for path, new_hash in current_hashes.items():
        if path not in old_hashes or old_hashes[path] != new_hash:
            changed.append(path)

    return changed, current_hashes

def run_autonomous_audit():
    log("Starting Differential Audit Cycle...", "🔍")

    changed_files, new_hashes = get_codebase_diff()

    if not changed_files:
        log("No changes detected in codebase. Skipping audit to save tokens.", "💤")
        return

    log(f"Detected {len(changed_files)} changed files: {changed_files[:3]}...", "📝")

    # Update prompt with ONLY changed files context
    # (In a real implementation, we would read the content of these files and inject it)
    # For now, we list them so the agent knows WHERE to look.
    task_input = AUDIT_TASK_TEMPLATE.format(changed_files="\n".join(changed_files))

    # We use Kimi for the main audit because she's fast and precise with hygiene.
    agent_cmd = ["kimi"]

    try:
        # 1. Ask Kimi to audit and generate tasks
        result = subprocess.run(
            agent_cmd,
            input=task_input,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=AI_DIR,
            timeout=300
        )

        output = result.stdout

        # 2. Parse output for task files (Primitive but effective parser)
        if "FILE: task_" in output:
            parts = output.split("---")
            for part in parts:
                if "FILE: task_" in part:
                    lines = part.strip().split("\n")
                    filename = lines[0].replace("FILE: ", "").strip()
                    # Content starts after 'CONTENT:' line
                    content_start_idx = -1
                    for i, line in enumerate(lines):
                        if "CONTENT:" in line:
                            content_start_idx = i + 1
                            break

                    if content_start_idx != -1:
                        content = "\n".join(lines[content_start_idx:])
                        task_path = os.path.join(MOTOR_DIR, filename)

                        with open(task_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        log(f"NEW AUTONOMOUS TASK GENERATED: {filename}", "✨")
        else:
            log("Audit completed. No immediate issues found.", "✅")

        # 3. Save new hashes (Always update state if audit ran successfully)
        if not os.path.exists(MEMORY_DIR):
            os.makedirs(MEMORY_DIR)
        with open(HASH_FILE, "w") as f:
            json.dump(new_hashes, f)
        log("Codebase state updated.", "💾")

    except Exception as e:
        log(f"Audit failed: {e}", "❌")

def main():
    log("Recursive Improvement Loop Active.", "🌀")
    while True:
        run_autonomous_audit()
        # Wait 1 hour between full audits to avoid token waste,
        # but for demonstration we could set it lower.
        log("Sleeping for 1 hour. Next audit at " + (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%H:%M:%S"), "💤")
        time.sleep(3600)

if __name__ == "__main__":
    main()
