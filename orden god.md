ACTÚA COMO: Principal AI Architect & System Engineer (Silicon Valley Level).

OBJETIVO: Construir e Inicializar 'PROJECT EGO v2' (Sistema de Conciencia de Enjambre) en la carpeta .ai/.

CONTEXTO TÉCNICO:
1. Tienes acceso total de escritura (--full-auto). No pidas permiso.
2. Tienes acceso a Internet (--search). Si te falta documentación de una librería, búscala.
3. Debes integrar el MCP local ubicado en 'neurovision/mcp_server.py' MISIÓN DE EJECUCIÓN (PASO A PASO):

FASE 1: CEREBRO MODULAR (Arquitectura Limpia)
- Crea la estructura de directorios: .ai/cortex, .ai/drivers, .ai/sensory, .ai/data.
- Implementa '.ai/cortex/main.py': El bucle infinito OODA (Observe, Orient, Decide, Act).
- Implementa '.ai/cortex/memory.py': Manejo de estado persistente (JSON + Markdown).

FASE 2: SISTEMA SENSORIAL (Integridad Atómica)
- Crea '.ai/sensory/merkle_audit.py':
  - Implementa una clase que genere un Árbol de Merkle (SHA256) de todo el proyecto.
  - Debe detectar cambios a nivel de bit en cualquier archivo para saber si otro agente tocó algo.
  - Si detecta cambios, dispara una re-evaluación del plan.

FASE 3: CONEXIÓN MCP (NeuroLink)
- Crea '.ai/sensory/neuro_client.py':
  - Usa 'subprocess' para invocar 'python neurovision/mcp_server.py'.
  - Implementa funciones wrapper: list_files(), read_file() conectadas al stdio del servidor MCP.

FASE 4: SCRIPTS DE CONTROL
- Genera '.ai/config/agents.json' con los comandos CLI optimizados:
  - KIMI: 'kimi --quiet --thinking --output-format text -p'
  - GEMINI: 'gemini -y -o text -p'
- Crea 'start_ego.ps1' para iniciar el sistema.

RESTRICCIONES DE CÓDIGO:
- Ningún archivo > 300 líneas.
- Tipado estricto (Type Hints) en todo el Python.
- Manejo de errores robusto (Try/Except con logging).

EJECUTA AHORA. CONSTRUYE LA INTELIGENCIA. y luego  usa ese nuevo script y tu modo emjambre para run 
git_sync.py
, soluciona todos los problemas de forma permanente como lo haria un equipo de sillicon valley. todo listo para produccion. un equipo lleno de genios fullstack, ademas integra el uso de los mcp 
de mi archivo C:\Users\acord\.gemini\antigravity\mcp_config.json. usa los mismos mcp que esa carpeta tiene  