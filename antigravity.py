import argparse
import datetime
import os
import sys

import yaml

# Configuration
AI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ai")
MOTOR_DIR = os.path.join(AI_DIR, "motor")


def create_task(prompt, autonomous_mode=False, thinkers=1, workers=2, agent="user"):
    """Creates a task file from a user prompt."""
    if not os.path.exists(MOTOR_DIR):
        os.makedirs(MOTOR_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    action_type = "directive" if agent == "user" else "manual"
    task_filename = f"task_{agent}_{action_type}_{timestamp}.md"
    task_filepath = os.path.join(MOTOR_DIR, task_filename)

    # --- METADATA (YAML Front Matter) ---
    metadata = {
        "task_id": f"user-{timestamp}",
        "created_at": datetime.datetime.now().isoformat(),
        "status": "pending",
        "parent_task": None,
    }
    if autonomous_mode:
        metadata["autonomous_mode"] = {
            "enabled": True,
            "thinkers": thinkers,
            "workers": workers,
            "status": "PLANNING",  # Initial state for autonomous mode
        }

    # --- CONTENT ---
    task_content = f"""
# TASK: USER DIRECTIVE

**Objective:**
{prompt}

**Action Required:**
This is a high-level directive from the user. 
1.  **Analyze** the objective.
2.  **Break it down** into a sequence of smaller, actionable tasks for other agents (codex, gemini, kimi).
3.  **Generate** the corresponding `task_AGENT_ACTION.md` files in the motor cortex.
"""

    # --- WRITE FILE with YAML Front Matter ---
    with open(task_filepath, "w", encoding="utf-8") as f:
        f.write("---\n")
        yaml.dump(metadata, f, default_flow_style=False)
        f.write("---\n")
        f.write(task_content)

    print(f"✅ Task created: {task_filename}")
    if autonomous_mode:
        print("🤖 Autonomous mode activated.")
    print("⏳ `synapse.py` will now process this task.")


def main():
    """Main entry point for the antigravity orchestrator."""
    parser = argparse.ArgumentParser(
        description="Antigravity: AI Agent Orchestrator. "
        "Provide a high-level objective and the Hive Mind will execute it."
    )
    parser.add_argument(
        "prompt", type=str, nargs="?", help="The high-level objective for the AI agents."
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Enter interactive mode to provide a multi-line prompt.",
    )
    # --- AUTONOMOUS MODE ARGUMENTS ---
    parser.add_argument(
        "--modo-autonomo",
        dest="autonomous_mode",
        action="store_true",
        help="Activate the autonomous mode with thinkers and workers.",
    )
    parser.add_argument(
        "--pensadores", type=int, default=1, help="Number of 'thinker' agents for planning."
    )
    parser.add_argument(
        "--trabajadores", type=int, default=2, help="Number of 'worker' agents for execution."
    )

    parser.add_argument(
        "-a",
        "--agent",
        type=str,
        default="user",
        help="Target agent (user, kimi, codex, gemini, manual).",
    )

    args = parser.parse_args()

    prompt = ""
    if args.interactive:
        print("📝 Enter your multi-line prompt (Ctrl+D or Ctrl+Z on Windows to save):")
        prompt = sys.stdin.read()
    elif args.prompt:
        prompt = args.prompt
    else:
        parser.print_help()
        sys.exit(1)

    if not prompt.strip():
        print("❌ Error: Prompt cannot be empty.")
        sys.exit(1)

    create_task(
        prompt.strip(),
        autonomous_mode=args.autonomous_mode,
        thinkers=args.pensadores,
        workers=args.trabajadores,
        agent=args.agent,
    )


if __name__ == "__main__":
    main()
