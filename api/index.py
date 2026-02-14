"""
🚀 ENTRY POINT - Vercel/Serverless
Responsabilidad ÚNICA: Bootstrap de la aplicación

❌ Error anterior: 81 líneas con 4 responsabilidades
✅ Solución: 15 líneas, solo entry point
📚 Lección: Separar concerns desde el inicio

Este archivo es el punto de entrada para Vercel y entornos serverless.
Toda la lógica de manejo de errores ahora está en:
  app/interfaces/api/middleware/error_handler.py
"""

import sys
import os

# Setup path para imports (único hack permitido en entry point)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Importar aplicación principal
from main import app

# app es expuesto para Vercel/Serverless
__all__ = ["app"]
