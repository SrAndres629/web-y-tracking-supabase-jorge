import os
import shutil
import time
import logging
from pathlib import Path
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
    "temp_data": PROJECT_ROOT / "tmp"
}

# Ensure directories exist
for d in TARGET_DIRS.values():
    d.mkdir(parents=True, exist_ok=True)

# Ignore patterns (don't react to changes in these folders)
IGNORE_DIRS = [".git", "venv", ".venv", "node_modules", ".agent", ".gemini", "__pycache__", ".vercel", ".pytest_cache"]

class WardenHandler(FileSystemEventHandler):
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
        
        # Security checks: Ignore deep nested files, we only care about root clutter
        if filepath.parent != PROJECT_ROOT:
            return
            
        # Ignore specific crucial root files
        if filepath.name in [".env", ".env.production", "pyproject.toml", "README.md", ".gitignore", ".gitlab-ci.yml", "pytest.ini", "main.py", "requirements.txt", "alembic.ini"]:
            return
            
        # Ignore hidden files
        if filepath.name.startswith("."):
            return

        time.sleep(0.5) # Wait for file to fully write

        try:
            target_path = None
            
            # Rule 1: Logs and TXT files
            if filepath.suffix in [".log", ".txt"]:
                target_path = TARGET_DIRS["logs"] / filepath.name
                
            # Rule 2: Deployment & Migration Scripts
            elif filepath.suffix == ".py" and (filepath.name.startswith("deploy_") or filepath.name.startswith("migration_")):
                target_path = TARGET_DIRS["deploy_scripts"] / filepath.name
                
            # Rule 3: Experimental / Temp Scripts
            elif filepath.suffix == ".py" and ("temp" in filepath.name or filepath.name.startswith("test_")):
                target_path = TARGET_DIRS["experimental_scripts"] / filepath.name
                
            # Rule 4: Loose Data files
            elif filepath.suffix in [".json", ".csv"]:
                # Exclude standard framework configs
                if not any(excluded in filepath.name.lower() for excluded in ["package", "config", "vercel.json", "tsconfig.json", "env"]):
                    target_path = TARGET_DIRS["temp_data"] / filepath.name

            # Execute Move
            if target_path:
                shutil.move(str(filepath), str(target_path))
                logging.info(f"🧹 Cleaned up: Moved {filepath.name} to {target_path.parent.name}/")
                
        except Exception as e:
            logging.error(f"⚠️ Could not move {filepath.name}: {e}")

def sweep_root():
    logging.info("🧹 Performing initial sweep of the root directory...")
    handler = WardenHandler()
    for item in PROJECT_ROOT.iterdir():
        if item.is_file():
            handler.process_file(str(item))

if __name__ == "__main__":
    logging.info("👁️ Project Warden Daemon Started.")
    sweep_root()
    logging.info("👁️ Monitoring root for clutter in real-time...")
    event_handler = WardenHandler()
    observer = Observer()
    observer.schedule(event_handler, str(PROJECT_ROOT), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
