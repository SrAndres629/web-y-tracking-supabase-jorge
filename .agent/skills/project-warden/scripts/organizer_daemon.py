import os
import shutil
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - 🛡️ Project Warden - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Determine project Root
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

# Define target architectural directories
TARGET_DIRS = {
    "logs": PROJECT_ROOT / "logs" / "agent_outputs",
    "deploy_scripts": PROJECT_ROOT / "scripts" / "deployment",
    "experimental_scripts": PROJECT_ROOT / "scripts" / "experimental",
    "quarantine": PROJECT_ROOT / "tmp" / "quarantine",
    "temp_data": PROJECT_ROOT / "tmp"
}

# Ensure directories exist
for d in TARGET_DIRS.values():
    d.mkdir(parents=True, exist_ok=True)

# Tickets Inbox
TICKETS_FILE = PROJECT_ROOT / ".agent" / "warden_tickets.json"
if not TICKETS_FILE.exists():
    with open(TICKETS_FILE, "w") as f:
        json.dump([], f)

def emit_ticket(jurisdiction: str, filepath: str, violation: str, action_taken: str, ai_message: str):
    try:
        with open(TICKETS_FILE, "r") as f:
            tickets = json.load(f)
    except Exception:
        tickets = []
        
    ticket = {
        "timestamp": datetime.now().isoformat(),
        "jurisdiction": jurisdiction,
        "file": str(filepath),
        "violation": violation,
        "action_taken": action_taken,
        "ai_action_required": True,
        "ai_message": ai_message
    }
    
    tickets.append(ticket)
    
    with open(TICKETS_FILE, "w") as f:
        json.dump(tickets, f, indent=2)
        
    logging.warning(f"🚨 TICKED ISSUED [{jurisdiction}]: {filepath}")

def wait_for_file_ready(filepath, timeout=5.0):
    """Wait until a file is no longer being written to avoid race conditions."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Attempt to open file exclusively to check if it's locked by another process
            with open(filepath, 'a'):
                pass
            return True
        except IOError:
            time.sleep(0.5)
    return False

class IntelligentWardenHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        self.process_file(event.src_path)
        
    def on_moved(self, event):
        if event.is_directory:
            return
        self.process_file(event.dest_path)

    def process_file(self, filepath_str):
        filepath = Path(filepath_str)
        
        # Security checks: Ignore deep nested files, we only care about root clutter now
        if filepath.parent != PROJECT_ROOT:
            return
            
        if not wait_for_file_ready(filepath):
            logging.error(f"⏱️ Timeout waiting for {filepath.name} to release lock. Skipping to avoid corruption.")
            return

        if not filepath.exists() or filepath.name.startswith("."):
            return

        try:
            target_path = None
            
            root_allowlist = [".env", ".env.production", "pyproject.toml", "README.md", ".gitignore", ".gitlab-ci.yml", "pytest.ini", "main.py", "requirements.txt", "alembic.ini", "vercel.json", "tsconfig.json", "pyrightconfig.json", "MANIFEST.yaml", "docker-compose.yml", "Dockerfile", "eslint.config.mjs", "package.json", "package-lock.json", "postcss.config.js", "ruff.toml", "tailwind.config.js"]
            
            if filepath.name not in root_allowlist:
                if filepath.suffix in [".log", ".txt"]:
                    target_path = TARGET_DIRS["logs"] / filepath.name
                    shutil.move(str(filepath), str(target_path))
                elif filepath.suffix == ".py" and ("test" in filepath.name or "temp" in filepath.name):
                    target_path = TARGET_DIRS["experimental_scripts"] / filepath.name
                    shutil.move(str(filepath), str(target_path))
                    emit_ticket("root", filepath.name, "Experimental script found in root.", f"Moved to scripts/experimental/", "Verifica si este script debe eliminarse o ser promovido.")
                elif filepath.suffix == ".py" and (filepath.name.startswith("deploy_") or filepath.name.startswith("migration_")):
                    target_path = TARGET_DIRS["deploy_scripts"] / filepath.name
                    shutil.move(str(filepath), str(target_path))
                elif filepath.suffix in [".json", ".csv"]:
                    if not any(excluded in filepath.name.lower() for excluded in ["package", "config", "vercel.json", "tsconfig.json", "env"]):
                        target_path = TARGET_DIRS["temp_data"] / filepath.name
                        shutil.move(str(filepath), str(target_path))
                else:
                    target_path = TARGET_DIRS["quarantine"] / filepath.name
                    shutil.move(str(filepath), str(target_path))
                    emit_ticket("root", filepath.name, "Unknown clutter in root directory.", f"Moved to quarantine", "La raíz es sagrada. Archivo puesto en cuarentena, analízalo.")
                
                if target_path and target_path.exists() and "quarantine" not in str(target_path) and "experimental" not in str(target_path):
                    logging.info(f"🧹 Cleaned up: Moved {filepath.name} to {target_path.parent.name}/")

        except Exception as e:
            logging.error(f"⚠️ Could not process {filepath.name}: {e}")

if __name__ == "__main__":
    logging.info("🧠 Project Warden: Root Intelligence System Active.")
    event_handler = IntelligentWardenHandler()
    observer = Observer()
    
    # Only observe PROJECT_ROOT, no recursion
    observer.schedule(event_handler, str(PROJECT_ROOT), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
