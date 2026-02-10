"""
🏗️ Core Layer - Utilities transversales al dominio.

Este módulo contiene utilidades puras que no dependen de ninguna capa,
pero son usadas por todas. Siguiendo el principio de Stable Dependencies:
- Ningún otro módulo debe depender de Core
- Core no debe depender de ningún otro módulo de la aplicación
"""

from app.core.result import Result, Ok, Err
from app.core.decorators import retry, circuit_breaker, timed

__all__ = [
    "Result",
    "Ok", 
    "Err",
    "retry",
    "circuit_breaker",
    "timed",
]
