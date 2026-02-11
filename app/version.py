"""
📌 SINGLE SOURCE OF TRUTH para versión

❌ Error anterior: 3 versiones diferentes en distintos archivos
✅ Solución: Un archivo, múltiples referencias
📚 Lección: La versión debe estar en un solo lugar
"""

VERSION = "3.0.0"
VERSION_MAJOR = 3
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_STRING = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"

__all__ = ["VERSION", "VERSION_MAJOR", "VERSION_MINOR", "VERSION_PATCH", "VERSION_STRING"]
