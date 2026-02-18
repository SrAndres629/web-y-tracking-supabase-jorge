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
from pathlib import Path
from typing import Dict, Any, List

# Try importing PyYAML
try:
    import yaml
except ImportError:
    yaml = None

# --- CONFIGURATION ---
AI_DIR = Path(__file__).parent.resolve()
MOTOR_DIR = AI_DIR / "motor"
SENSORY_DIR = AI_DIR / "sensory"
MEMORY_DIR: Path = AI_DIR / "memory"
FAILED_DIR: Path = MEMORY_DIR / "failed"
DONE_DIR: Path = MEMORY_DIR / "done"
CONSENSUS_FILE: Path = MEMORY_DIR / "mvp_consensus.md"

ENV_VARS: Dict[str, str] = os.environ.copy()
ENV_VARS["MCP_CONFIG_FILE"] = str(
    Path.home() / ".gemini/antigravity/mcp_config.json"
)
ENV_VARS["PYTHONUNBUFFERED"] = "1"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] 🌐 [%(name)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger: logging.Logger = logging.getLogger("SYNAPSE")


def log(msg: str, icon: str = "⚡") -> None:
    """Logs a message with a specific icon to the console."""
    logger.info("%s %s", icon, msg)


def ensure_dirs() -> None:
    """Ensures that all required directories for the system exist."""
    for d in [MOTOR_DIR, SENSORY_DIR, MEMORY_DIR, FAILED_DIR, DONE_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    if not CONSENSUS_FILE.exists():
        CONSENSUS_FILE.write_text(
            "# MVP CONSENSUS LOG\n\n- [ ] Phase 1 Complete\n"
            "- [ ] Phase 2 Complete\n- [ ] Functional MVP",
            encoding="utf-8"
        )


# --- UTILS ---
def parse_metadata(content: str) -> Dict[str, Any]:
    """Parses YAML metadata from the beginning of a markdown file."""
    metadata: Dict[str, Any] = {}
    if content.startswith("---"):
        try:
            parts: List[str] = content.split("---", 2)
            if len(parts) >= 3:
                yaml_text: str = parts[1]
                if yaml:
                    metadata = yaml.safe_load(yaml_text) or {}
                else:
                    for line in yaml_text.splitlines():
                        if ":" in line:
                            k, v = line.split(":", 1)
                            metadata[k.strip()] = v.strip().replace(
                                '"', ''
                            ).replace("'", "")
        except Exception:
            pass
    return metadata


def update_metadata(path: Path, metadata: Dict[str, Any]) -> None:
    """Updates the YAML metadata section of a markdown file."""
    try:
        content: str = path.read_text(encoding="utf-8")
        body: str = content
        if content.startswith("---"):
            parts: List[str] = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2]

        new_content: str = "---\n"
        if yaml:
            new_content += yaml.dump(metadata, default_flow_style=False)
        else:
            for k, v in metadata.items():
                if isinstance(v, dict):
                    new_content += f"{k}:\n"
                    # Type hints for manual yaml serialization
                    sk: str
                    sv: Any
                    for sk, sv in v.items():
                        new_content += f"  {sk}: {sv}\n"
                else:
                    new_content += f"{k}: {v}\n"
        new_content += "---\n" + body
        path.write_text(new_content, encoding="utf-8")
    except Exception as e:
        log(f"Metadata Update Failed: {e}", "⚠️")


def create_child_task(
    agent: str, action: str, instruction: str, parent_file: str
) -> None:
    """Creates a new task file for a specific agent as a child of another."""
    filename: str = f"task_{agent}_{action}_{int(time.time())}.md"
    path: Path = MOTOR_DIR / filename
    content: str = f"""---
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
def trigger_neurovision_scan() -> None:
    """Triggers NeuroVision to scan changes."""
    # Assuming neurovision is an MCP tool or script.
    # If standard script: scripts/vision.py
    vision_script: Path = AI_DIR.parent / "scripts" / "vision.py"
    if vision_script.exists():
        try:
            subprocess.Popen(
                [sys.executable, str(vision_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # log("NeuroVision Scan Triggered", "👁️")
        except Exception:
            pass


# --- ASYNC AGENT EXECUTION ---
def run_agent_process(agent_name: str, task_path: Path) -> None:
    """Worker thread function to execute agent without blocking."""
    log(f"Starting Async Agent: {agent_name.upper()}", "🚀")

    start_time: float = time.time()

    try:
        # REAL EXECUTION: Call the scripts/ wrapper
        # We use strict non-interactive flags where possible

        script_path: Path = AI_DIR.parent / "scripts" / agent_name
        if not script_path.exists():
            # Fallback to antigravity direct call if wrapper missing
            cmd: List[str] = [
                sys.executable, "antigravity.py",
                task_path.read_text(encoding="utf-8")
            ]
            # Antigravity doesn't have a YOLO flag yet, it's non-interactive
        else:
            # For Gemini/Codex CLIs, assume they support a non-interactive flag
            # If they are just antigravity wrappers, they pass args through.
            cmd = [
                str(script_path), task_path.read_text(encoding="utf-8")
            ]

        # 🛡️ FORCE AUTONOMY: Set environment to prevent prompts
        env: Dict[str, str] = os.environ.copy()
        env["CI"] = "true"
        env["NON_INTERACTIVE"] = "1"
        env["YOLO_MODE"] = "true"  # Custom flag for our tools

        # Execute Subprocess (Capture output)
        result: subprocess.CompletedProcess[str] = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            cwd=AI_DIR.parent,
            check=False
        )

        if result.returncode == 0:
            log(
                f"Agent {agent_name} Finished "
                f"({time.time() - start_time:.1f}s)", "🏁"
            )
            # Log output to trace
            trace_id: int = int(time.time())
            trace_fn: str = f"trace_{trace_id}_{agent_name}.md"
            trace_file: Path = SENSORY_DIR / trace_fn
            trace_file.write_text(
                f"# SUCCESS: {agent_name}\n## Output:\n{result.stdout}",
                encoding="utf-8"
            )
            # Move to Done
            if task_path.exists():
                shutil.move(str(task_path), str(DONE_DIR / task_path.name))
        else:
            log(f"Agent {agent_name} Failed (Exit {result.returncode})", "❌")
            # Log error
            err_id: int = int(time.time())
            err_file: Path = SENSORY_DIR / f"error_{err_id}_{agent_name}.md"
            err_file.write_text(
                f"# ERROR: {agent_name}\n## Stderr:\n{result.stderr}\n"
                f"## Stdout:\n{result.stdout}",
                encoding="utf-8"
            )
            if task_path.exists():
                shutil.move(str(task_path), str(FAILED_DIR / task_path.name))

        # Trigger Vision Update
        trigger_neurovision_scan()

    except Exception as e:
        log(f"Agent {agent_name} Crashed: {e}", "🔥")
        if task_path.exists():
            shutil.move(str(task_path), str(FAILED_DIR / task_path.name))


def execute_agent_async(agent_name: str, task_path: Path) -> None:
    """Spawns a thread for the agent execution."""
    thread: threading.Thread = threading.Thread(
        target=run_agent_process, args=(agent_name, task_path)
    )
    thread.daemon = True
    thread.start()


# --- HIVE MIND ENGINE ---
def process_hive_mind(
    task_path: Path, metadata: Dict[str, Any], _content: str
) -> None:
    """Manages the autonomous loop with non-blocking logic."""
    auto_data: Dict[str, Any] = dict(metadata.get("autonomous_mode", {}))
    if not auto_data:
        auto_data = {"enabled": True, "status": "PLANNING"}

    status: str = str(auto_data.get("status", "PLANNING"))

    if status == "PLANNING":
        log("Phase 1: KIMI Planning...", "📐")
        create_child_task(
            "kimi", "plan", f"Plan for {task_path.name}", task_path.name
        )
        auto_data["status"] = "WAITING_PLAN"
        metadata["autonomous_mode"] = auto_data
        update_metadata(task_path, metadata)

    elif status == "WAITING_PLAN":
        found: bool = False
        for f in DONE_DIR.glob("task_kimi_plan_*.md"):
            if f"parent_task: {task_path.name}" in f.read_text(
                encoding='utf-8'
            ):
                found = True
                break

        if found:
            log("Plan Received. Proceeding to Execution.", "✅")
            auto_data["status"] = "EXECUTING"
            metadata["autonomous_mode"] = auto_data
            update_metadata(task_path, metadata)

    elif status == "EXECUTING":
        log("Phase 2: CODEX Executing...", "🔨")
        create_child_task(
            "codex", "build", f"Build for {task_path.name}", task_path.name
        )
        auto_data["status"] = "WAITING_BUILD"
        metadata["autonomous_mode"] = auto_data
        update_metadata(task_path, metadata)

    elif status == "WAITING_BUILD":
        found = False
        for f in DONE_DIR.glob("task_codex_build_*.md"):
            if f"parent_task: {task_path.name}" in f.read_text(
                encoding='utf-8'
            ):
                found = True
                break

        if found:
            log("Build Complete. Proceeding to Audit.", "✅")
            auto_data["status"] = "AUDITING"
            metadata["autonomous_mode"] = auto_data
            update_metadata(task_path, metadata)

    elif status == "AUDITING":
        log("Phase 3: GEMINI Auditing...", "🧐")
        create_child_task(
            "gemini", "audit", f"Audit {task_path.name}", task_path.name
        )
        auto_data["status"] = "WAITING_AUDIT"
        metadata["autonomous_mode"] = auto_data
        update_metadata(task_path, metadata)

    elif status == "WAITING_AUDIT":
        found: bool = False
        for f in DONE_DIR.glob("task_gemini_audit_*.md"):
            if f"parent_task: {task_path.name}" in f.read_text(
                encoding='utf-8'
            ):
                found = True
                break

        if found:
            log("Audit Complete. MVP Cycle Done.", "🏆")
            shutil.move(str(task_path), str(DONE_DIR / task_path.name))


# --- MAIN LOOP ---
def main() -> None:
    """Main execution loop for the Synapse Hive Mind."""
    log("SYNAPSE v3.0 (Async Hive Mind) Online", "🟢")
    ensure_dirs()

    while True:
        try:
            files: List[Path] = list(MOTOR_DIR.glob("*.md"))
            if not files:
                time.sleep(1)
                continue

            for task_path in files:
                if task_path.name == "task_halt.md":
                    sys.exit(0)

                # Metadata check
                content: str = task_path.read_text(encoding="utf-8")
                metadata: Dict[str, Any] = parse_metadata(content)

                # Parent Task (Autonomous Manager)
                if metadata.get("autonomous_mode"):
                    process_hive_mind(task_path, metadata, content)
                    continue

                # Child/Direct Tasks (Agent Workers)
                # If it's a specific agent task, execute it ASYNC
                fname: str = task_path.name
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
                            shutil.move(
                                str(task_path), str(DONE_DIR / task_path.name)
                            )
                    else:
                        shutil.move(
                            str(task_path), str(FAILED_DIR / task_path.name)
                        )

            # Sleep briefly to prevent CPU spin,
            # but allow threads to run
            time.sleep(1)

        except Exception as e:
            log(f"Synapse Error: {e}", "🔥")
            time.sleep(5)


if __name__ == "__main__":
    main()
