import os
import subprocess

def start_phoenix():
    print("Starting Arize Phoenix local collector...")
    # Default port is 6006
    try:
        subprocess.run(["python3", "-m", "phoenix.server.main", "serve"], check=True)
    except KeyboardInterrupt:
        print("\nPhoenix server stopped.")
    except Exception as e:
        print(f"Failed to start Phoenix: {e}")

if __name__ == "__main__":
    start_phoenix()
