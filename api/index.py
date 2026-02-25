import os
import sys
from pathlib import Path

# Fix path resolution for imports
root = Path(__file__).parent.parent
if str(root) not in sys.path:
    sys.path.append(str(root))

# 🚀 Pure Entry Point for Vercel
from main import app

# app es expuesto para Vercel/Serverless
__all__ = ["app"]
