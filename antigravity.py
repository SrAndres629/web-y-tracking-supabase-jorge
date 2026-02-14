
import os
import sys
import argparse
import datetime

# Configuration
AI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ai")
MOTOR_DIR = os.path.join(AI_DIR, "motor")

def create_task(prompt):
    """Creates a task file from a user prompt."""
    if not os.path.exists(MOTOR_DIR):
        os.makedirs(MOTOR_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    task_filename = f"task_user_{timestamp}.md"
    task_filepath = os.path.join(MOTOR_DIR, task_filename)

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

    with open(task_filepath, "w", encoding="utf-8") as f:
        f.write(task_content)

    print(f"✅ Task created: {task_filename}")
    print(f"⏳ `synapse.py` will now process this task.")

def main():
    """Main entry point for the antigravity orchestrator."""
    parser = argparse.ArgumentParser(
        description="Antigravity: AI Agent Orchestrator. "
                    "Provide a high-level objective and the Hive Mind will execute it."
    )
    parser.add_argument(
        "prompt",
        type=str,
        nargs='?',
        help="The high-level objective for the AI agents."
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Enter interactive mode to provide a multi-line prompt."
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

    create_task(prompt.strip())


if __name__ == "__main__":
    main()
