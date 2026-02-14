"""
SYNAPSE v3.0: THE HIVE MIND ORCHESTRATOR (PROMETHEUS PROTOCOL - ASYNC)
======================================================================
Manages the autonomic nervous system of the project with ASYNC ORCHESTRATION.
Orchestrates the Kimi (Plan) -> Antigravity (Act) -> Gemini (Audit) loop.
Features:
- Non-blocking Agent Execution (Threading)
- Real-time NeuroVision Integration
- Consensus Engine
"""

import os
import sys
import time
import shutil
import logging
import subprocess
import threading
import json
from pathlib import Path
from datetime import datetime

# Try importing PyYAML
try:
    import yaml
except ImportError:
    yaml = None

# --- CONFIGURATION ---
AI_DIR = Path(__file__).parent.resolve()
MOTOR_DIR = AI_DIR / "motor"
SENSORY_DIR = AI_DIR / "sensory"
MEMORY_DIR = AI_DIR / "memory"
FAILED_DIR = MEMORY_DIR / "failed"
DONE_DIR = MEMORY_DIR / "done"
CONSENSUS_FILE = MEMORY_DIR / "mvp_consensus.md"

ENV_VARS = os.environ.copy()
ENV_VARS["MCP_CONFIG_FILE"] = str(Path.home() / ".gemini/antigravity/mcp_config.json")
ENV_VARS["PYTHONUNBUFFERED"] = "1"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] 🌐 [%(name)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("SYNAPSE")

def log(msg, icon="⚡"):
    logger.info(f"{icon} {msg}")

def ensure_dirs():
    for d in [MOTOR_DIR, SENSORY_DIR, MEMORY_DIR, FAILED_DIR, DONE_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    if not CONSENSUS_FILE.exists():
        CONSENSUS_FILE.write_text("# MVP CONSENSUS LOG\n\n- [ ] Phase 1 Complete\n- [ ] Phase 2 Complete\n- [ ] Functional MVP", encoding="utf-8")

# --- UTILS ---
def parse_metadata(content):
    metadata = {}
    if content.startswith("---"):
        try:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_text = parts[1]
                if yaml:
                    metadata = yaml.safe_load(yaml_text) or {}
                else:
                    for line in yaml_text.splitlines():
                        if ":" in line:
                            k, v = line.split(":", 1)
                            metadata[k.strip()] = v.strip().replace('"', '').replace("'", "")
        except Exception: pass
    return metadata

def update_metadata(path, metadata):
    try:
        content = path.read_text(encoding="utf-8")
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2]
        
        new_content = "---\n"
        if yaml:
            new_content += yaml.dump(metadata, default_flow_style=False)
        else:
            for k, v in metadata.items():
                if isinstance(v, dict):
                    new_content += f"{k}:\n"
                    for subk, subv in v.items():
                        new_content += f"  {subk}: {subv}\n"
                else:
                    new_content += f"{k}: {v}\n"
        new_content += "---\n" + body
        path.write_text(new_content, encoding="utf-8")
    except Exception as e:
        log(f"Metadata Update Failed: {e}", "⚠️")

def create_child_task(agent, action, instruction, parent_file):
    filename = f"task_{agent}_{action}_{int(time.time())}.md"
    path = MOTOR_DIR / filename
    content = f"""---
parent_task: {parent_file}
created_by: synapse
timestamp: {time.time()}
status: pending
---
# TASK: {action}
**Agent:** {agent}
**Instruction:** {instruction}
"""
    path.write_text(content, encoding="utf-8")
    log(f"Dispatched Task: {filename}", "📨")

# --- NEUROVISION INTEGRATION ---
def trigger_neurovision_scan():
    """Triggers NeuroVision to scan changes."""
    # Assuming neurovision is an MCP tool or script. 
    # If standard script: scripts/vision.py
    vision_script = AI_DIR.parent / "scripts" / "vision.py"
    if vision_script.exists():
        try:
            subprocess.Popen([sys.executable, str(vision_script)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # log("NeuroVision Scan Triggered", "👁️")
        except: pass

# --- ASYNC AGENT EXECUTION ---
def run_agent_process(agent_name, task_path):
    """Worker thread function to execute agent without blocking."""
    log(f"Starting Async Agent: {agent_name.upper()}", "🚀")
    
    start_time = time.time()
    
    try:
        # REAL EXECUTION: Call the scripts/ wrapper
        # We use strict non-interactive flags where possible
        
        script_path = AI_DIR.parent / "scripts" / agent_name
        if not script_path.exists():
            # Fallback to antigravity direct call if wrapper missing
            cmd = [sys.executable, "antigravity.py", task_path.read_text(encoding="utf-8")]
            # Antigravity doesn't have a YOLO flag yet, but it's non-interactive by default unless -i passed
        else:
            # For Gemini/Codex CLIs, assume they support a non-interactive flag if they wrap real tools
            # If they are just antigravity wrappers, they pass arguments through.
            # We append a "NON-INTERACTIVE" instruction to the prompt if possible, or rely on environment
            cmd = [str(script_path), task_path.read_text(encoding="utf-8")]

        # 🛡️ FORCE AUTONOMY: Set environment to prevent prompts
        env = os.environ.copy()
        env["CI"] = "true" 
        env["NON_INTERACTIVE"] = "1"
        env["YOLO_MODE"] = "true" # Custom flag for our tools
        
        # Execute Subprocess (Capture output)
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            env=env,
            cwd=AI_DIR.parent
        )
        
        if result.returncode == 0:
            log(f"Agent {agent_name} Finished ({time.time() - start_time:.1f}s)", "🏁")
            # Log output to trace
            trace_file = SENSORY_DIR / f"trace_{int(time.time())}_{agent_name}_success.md"
            trace_file.write_text(f"# SUCCESS: {agent_name}\n## Output:\n{result.stdout}", encoding="utf-8")
             # Move to Done
            if task_path.exists():
                shutil.move(str(task_path), str(DONE_DIR / task_path.name))
        else:
            log(f"Agent {agent_name} Failed (Exit {result.returncode})", "❌")
            # Log error
            err_file = SENSORY_DIR / f"error_{int(time.time())}_{agent_name}.md"
            err_file.write_text(f"# ERROR: {agent_name}\n## Stderr:\n{result.stderr}\n## Stdout:\n{result.stdout}", encoding="utf-8")
            if task_path.exists():
                shutil.move(str(task_path), str(FAILED_DIR / task_path.name))

        # Trigger Vision Update
        trigger_neurovision_scan()
        
    except Exception as e:
        log(f"Agent {agent_name} Crashed: {e}", "🔥")
        if task_path.exists():
            shutil.move(str(task_path), str(FAILED_DIR / task_path.name))

def execute_agent_async(agent_name, task_path):
    """Spawns a thread for the agent."""
    thread = threading.Thread(target=run_agent_process, args=(agent_name, task_path))
    thread.daemon = True
    thread.start()

# --- HIVE MIND ENGINE ---
def process_hive_mind(task_path, metadata, content):
    """Manages the autonomous loop with non-blocking logic."""
    
    auto_data = metadata.get("autonomous_mode", {})
    if not isinstance(auto_data, dict): auto_data = {"enabled": True, "status": "PLANNING"}
    
    status = auto_data.get("status", "PLANNING")
    
    # If we are waiting for a child task, we shouldn't spam new ones.
    # WE need to check if the child task is done. 
    # For MVP, we'll implement a simple sequential state machine in the Parent File.
    
    if status == "PLANNING":
        log("Phase 1: KIMI Planning...", "📐")
        create_child_task("kimi", "plan", f"Plan for {task_path.name}", task_path.name)
        auto_data["status"] = "WAITING_PLAN"
        metadata["autonomous_mode"] = auto_data
        update_metadata(task_path, metadata)
        
    elif status == "WAITING_PLAN":
        # Check if plan is done (scan done dir)
        # Identify child task ID? For simplicity, we assume if we see a Kimi plan in done, we proceed.
        # This logic needs to be robust. 
        # For this MVP script, we just auto-advance after a delay or file check.
        # Let's auto-advance state if we find *any* kimi plan in DONE that mentions this parent.
        found = False
        for f in DONE_DIR.glob("task_kimi_plan_*.md"):
            if f"parent_task: {task_path.name}" in f.read_text():
                found = True
                break
        
        if found:
            log("Plan Received. Proceeding to Execution.", "✅")
            auto_data["status"] = "EXECUTING"
            metadata["autonomous_mode"] = auto_data
            update_metadata(task_path, metadata)
            
    elif status == "EXECUTING":
        log("Phase 2: CODEX Executing...", "🔨")
        create_child_task("codex", "build", f"Build for {task_path.name}", task_path.name)
        auto_data["status"] = "WAITING_BUILD"
        metadata["autonomous_mode"] = auto_data
        update_metadata(task_path, metadata)

    elif status == "WAITING_BUILD":
        found = False
        for f in DONE_DIR.glob("task_codex_build_*.md"):
            if f"parent_task: {task_path.name}" in f.read_text():
                found = True
                break
        
        if found:
            log("Build Complete. Proceeding to Audit.", "✅")
            auto_data["status"] = "AUDITING"
            metadata["autonomous_mode"] = auto_data
            update_metadata(task_path, metadata)

    elif status == "AUDITING":
        log("Phase 3: GEMINI Auditing...", "🧐")
        create_child_task("gemini", "audit", f"Audit {task_path.name}", task_path.name)
        auto_data["status"] = "WAITING_AUDIT"
        metadata["autonomous_mode"] = auto_data
        update_metadata(task_path, metadata)

    elif status == "WAITING_AUDIT":
        found = False
        for f in DONE_DIR.glob("task_gemini_audit_*.md"):
            if f"parent_task: {task_path.name}" in f.read_text():
                found = True
                break
        
        if found:
            log("Audit Complete. MVP Cycle Done.", "🏆")
            shutil.move(str(task_path), str(DONE_DIR / task_path.name))

# --- MAIN LOOP ---
def main():
    log("SYNAPSE v3.0 (Async Hive Mind) Online", "🟢")
    ensure_dirs()
    
    while True:
        try:
            files = list(MOTOR_DIR.glob("*.md"))
            if not files:
                time.sleep(1)
                continue
                
            for task_path in files:
                if task_path.name == "task_halt.md":
                    sys.exit(0)
                
                # Metadata check
                content = task_path.read_text(encoding="utf-8")
                metadata = parse_metadata(content)
                
                # Parent Task (Autonomous Manager)
                if metadata.get("autonomous_mode"):
                    process_hive_mind(task_path, metadata, content)
                    continue
                
                # Child/Direct Tasks (Agent Workers)
                # If it's a specific agent task, execute it ASYNC
                fname = task_path.name
                if "kimi" in fname:
                    execute_agent_async("kimi", task_path)
                elif "codex" in fname or "antigravity" in fname:
                    execute_agent_async("codex", task_path)
                elif "gemini" in fname:
                    execute_agent_async("gemini", task_path)
                else:
                    # User directive?
                    if "user" in fname:
                         log(f"User Directive found: {fname}", "👤")
                         # Add autonomous mode if missing
                         if not metadata.get("autonomous_mode"):
                             create_child_task("kimi", "plan", content, fname)
                             shutil.move(str(task_path), str(DONE_DIR / task_path.name))
                    else:
                        shutil.move(str(task_path), str(FAILED_DIR / task_path.name))
                        
            # Sleep briefly to prevent CPU spin, 
            # but allow threads to run
            time.sleep(1) 
            
        except Exception as e:
            log(f"Synapse Error: {e}", "🔥")
            time.sleep(5)

if __name__ == "__main__":
    main()
