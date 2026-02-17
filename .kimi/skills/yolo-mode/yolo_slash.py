#!/usr/bin/env python3
"""
Slash command handler para /yolo en Kimi CLI
"""

import json
import logging
import sys
from pathlib import Path

# Configurar logger para yolo_slash.py
logger = logging.getLogger(__name__)

# Asegurar que podemos importar el modo YOLO
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from .ai.modes.yolo_mode import ActionCategory, ThoughtLevel, create_yolo_mode
except ImportError:
    # Fallback si no está en el path
    pass

YOLO_CONFIG_PATH = Path(".ai/modes/yolo_config.json")
YOLO_STATE_PATH = Path(".ai/modes/yolo_state.json")


def load_state():
    """Carga el estado actual del modo YOLO"""
    if YOLO_STATE_PATH.exists():
        with open(YOLO_STATE_PATH, "r") as f:
            return json.load(f)
    return {"active": False, "thought_level": "deep"}


def save_state(state):
    """Guarda el estado del modo YOLO"""
    YOLO_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(YOLO_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def activate_yolo(thought_level="deep"):
    """Activa el modo YOLO"""
    state = {
        "active": True,
        "thought_level": thought_level,
        "activated_at": __import__("time").time(),
    }
    save_state(state)

    levels = {"surface": "🌊", "standard": "📊", "deep": "🔍", "profound": "🧠", "meta": "🌌"}

    emoji = levels.get(thought_level, "🚀")

    return f"""
{emoji} ════════════════════════════════════════════════════════════ {emoji}
                    MODO YOLO ACTIVADO
{emoji} ════════════════════════════════════════════════════════════ {emoji}

🧠 Nivel de Pensamiento: {thought_level.upper()}
📊 Confianza Mínima: 75%
🔄 Rollback Automático: Habilitado
📝 Logging: Activado en .ai/modes/logs/

Comportamiento:
• Análisis profundo antes de cada acción
• Autoaceptación cuando confianza > 75%
• Escalación humana en casos críticos
• Plan de rollback siempre generado

Para desactivar: /yolo off
"""


def deactivate_yolo():
    """Desactiva el modo YOLO"""
    state = load_state()
    state["active"] = False
    state["deactivated_at"] = __import__("time").time()
    save_state(state)

    return """
✋ ════════════════════════════════════════════════════════════ ✋
                   MODO YOLO DESACTIVADO
✋ ════════════════════════════════════════════════════════════ ✋

Volviendo al modo manual estándar.
Todas las acciones requerirán confirmación explícita.
"""


def show_stats():
    """Muestra estadísticas del modo YOLO"""
    state = load_state()
    logs_dir = Path(".ai/modes/logs")

    if logs_dir.exists():
        decisions = list(logs_dir.glob("yolo_*.json"))
        total = len(decisions)
    else:
        total = 0

    status = "🟢 ACTIVO" if state.get("active") else "🔴 INACTIVO"

    return f"""
📊 ════════════════════════════════════════════════════════════ 📊
              ESTADÍSTICAS DEL MODO YOLO
📊 ════════════════════════════════════════════════════════════ 📊

Estado: {status}
Nivel Actual: {state.get("thought_level", "N/A")}
Decisiones Totales: {total}
Logs: .ai/modes/logs/

Para activar: /yolo [surface|standard|deep|profound|meta]
Para desactivar: /yolo off
"""


def main():
    """Punto de entrada para el slash command"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if not args or args[0] in ["help", "--help", "-h"]:
        logger.info("""
Uso: /yolo [nivel|off|stats]

Niveles de pensamiento:
  surface    - Análisis rápido (< 5s)
  standard   - Análisis estándar (5-15s)
  deep       - Pensamiento profundo (15-30s) [default]
  profound   - Pensamiento extendido (30-60s)
  meta       - Análisis meta-cognitivo (60s+)

Comandos:
  off        - Desactivar modo YOLO
  stats      - Ver estadísticas
  help       - Mostrar esta ayuda
""")
        return

    command = args[0].lower()

    valid_levels = ["surface", "standard", "deep", "profound", "meta"]

    if command in valid_levels:
        logger.info(activate_yolo(command))
    elif command == "off":
        logger.info(deactivate_yolo())
    elif command == "stats":
        logger.info(show_stats())
    else:
        logger.error(f"❌ Nivel desconocido: {command}")
        logger.info(f"Niveles válidos: {', '.join(valid_levels)}")


if __name__ == "__main__":
    main()
