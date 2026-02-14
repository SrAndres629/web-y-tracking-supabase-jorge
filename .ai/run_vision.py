import sys
import os
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from core.vision.server import start_server

if __name__ == "__main__":
    print("Starting Optic Nerve on port 8888...")
    start_server()
