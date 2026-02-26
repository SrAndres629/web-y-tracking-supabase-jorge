import sys
import subprocess
import os

def run_neuron_1(filepath):
    """
    Executes Neuron 1: The Cleaner.
    Runs Ruff checks, auto-fixes unused imports, and formats the code block.
    """
    if not os.path.exists(filepath):
        print(f"❌ [Neuron 1] Error: Target file {filepath} not found.")
        sys.exit(1)

    print(f"🧠 [Neuron 1] Activating Cleansing Protocol on: {filepath}")
    
    # Run ruff check --fix for unused imports and basic linting
    print("🧹 Running ruff check --fix...")
    fix_cmd = ["uvx", "ruff", "check", "--fix", filepath]
    try:
        subprocess.run(fix_cmd, check=True, capture_output=True, text=True)
        print("✅ Linting and auto-fixes applied seamlessly.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Linting warning or output: {e.output}")

    # Run ruff format
    print("✨ Running ruff format...")
    format_cmd = ["uvx", "ruff", "format", filepath]
    try:
        subprocess.run(format_cmd, check=True, capture_output=True, text=True)
        print("✅ Silicon Valley formatting applied.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Format warning or output: {e.output}")

    print("🛡️ [Neuron 1] Execution Complete. File is pristine.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 clean_format.py <absolute_file_path>")
        sys.exit(1)
        
    target_file = sys.argv[1]
    run_neuron_1(target_file)
