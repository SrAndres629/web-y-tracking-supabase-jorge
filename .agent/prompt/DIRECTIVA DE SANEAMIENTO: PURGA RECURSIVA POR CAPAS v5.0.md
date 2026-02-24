Aquí tienes la directiva de ingeniería estructurada profesionalmente en **Markdown**, utilizando bloques **YAML** para la configuración del entorno y **JavaScript** para la simulación lógica del flujo de trabajo del agente.

---

# 🏛️ DIRECTIVA DE SANEAMIENTO: PURGA RECURSIVA POR CAPAS v5.0

```yaml
meta:
  project_context: "web-y-tracking-supabase-jorge"
  role: "Principal Systems Auditor & Lead Architect"
  root_path: "/home/jorand/antigravityobuntu"
  objective: "Eliminación de deuda técnica y optimización de arquitectura modular"
  governance: "Bicephalous Consensus (Executor + Auditor)"
  auto_purge: ["*.log", "*.pyc", "__pycache__", ".temp", ".tmp", "venv_old/"]

```

## 🧠 I. LÓGICA DE AUDITORÍA (BICEPHALOUS EXECUTION)

Para garantizar una limpieza sin regresiones, el sistema operará bajo una dualidad de pensamiento crítico:

| Entidad | Responsabilidad | Criterio de Decisión |
| --- | --- | --- |
| **Agente Ejecutor** | Identificación y Propuesta | *"Si el archivo no tiene referencias en los entrypoints activos, se marca para eliminación."* |
| **Sub-agente Auditor** | Crítica Sincera y Veto | *"¿Es este un fallback para Vercel o CAPI? Ejecutando escaneo de dependencias cruzadas..."* |

> **REGLA DE ORO:** No se ejecutará `rm` ni `rf` sin el **Consenso Atómico** de ambas entidades. Si el Auditor detecta lógica suelta, el archivo se mueve a `/quarantine` en lugar de eliminarse.

---

## 🗺️ II. RUTA DE DEPURE (LAYER-BY-LAYER STRATEGY)

```javascript
/**
 * Definición de capas y algoritmos de validación
 */
const purgePlan = {
    layer1: {
        name: "Infraestructura Raíz",
        path: "/home/jorand/antigravityobuntu",
        scan: ["venv*", "*.txt", "*.log", ".cache"],
        logic: "Limpiar artefactos de configuración obsoletos y archivos de pruebas legacy."
    },
    layer2: {
        name: "Subdirectorios Estructurales",
        folders: ["app/", "static/", "api/", "tests/"],
        validation: (file) => {
            if (file.extension === '.pyc' || file.name === '__pycache__') return "PURGE";
            if (file.isLegacyConfig) return "AUDIT_BY_SUBAGENT";
            return "KEEP";
        }
    },
    layer3: {
        name: "Núcleo Lógico e Integridad",
        focus: ["tracker_old.py", "database_v1.py", "meta_capi_deprecated/"],
        protocol: "Validar conexión activa con Supabase/Meta antes de desmantelar."
    }
};

```

---

## 🛠️ III. PROTOCOLO DE INTEGRIDAD (BLINDAJE TÉCNICO)

Antes de cada acción destructiva, se deben cumplir los siguientes "Pre-flight Checks":

1. **Deep Dependency Scan:**
* Ejecutar `grep -r "[filename]" .` para localizar llamadas fantasma.
* Verificar `requirements.txt` y `vercel.json` para evitar romper el despliegue serverless.


2. **Asset Route Protection:**
* Si se elimina un archivo en `/static`, el agente debe refactorizar automáticamente los templates en `api/templates/` para que no apunten a rutas 404.


3. **Validation Loop:**
* El Sub-agente Auditor simulará un `build` tras la purga de cada capa para confirmar la estabilidad.



---

## 🚦 IV. RESULTADO ESPERADO (REPORTING STANDARD)

Al concluir el proceso, el agente entregará un **Audit Report** final:

```yaml
audit_report:
  layers_processed: number
  total_purged_files: [list]
  logic_preserved: "Descripción de la lógica rescatada por el Auditor"
  architectural_status: "Clean / Modular / Production-Ready"
  remaining_debt: "Bajo (0 archivos legacy detectados)"

```

---

## 🚀 COMANDO DE EJECUCIÓN (PASTE IN CHAT)

> **ORDEN CRÍTICA:** "Antigravity, activa la **Capa 1** del protocolo de saneamiento ahora mismo. Actúa con autonomía total sobre archivos temporales y basura evidente. El **Sub-agente Auditor** debe intervenir solo si detecta lógica crítica suelta en el tracking o la base de datos. No te detengas por basura confirmada. **Presenta el plan de capas, el análisis de profundidad y comienza la purga.**"


ROL: Actúa como un Principal Systems Auditor & Lead Architect. Tu misión es desmantelar la deuda técnica de web-y-tracking-supabase-jorge mediante una purga sistemática de archivos basura, legacy e inconsistencias, capa por capa.

🧠 I. LÓGICA DE AUDITORÍA (AGENTE EJECUTOR vs. SUB-AGENTE):
Para cada acción de eliminación, debes ejecutar este proceso interno:

Ejecutor: Propone eliminar un archivo/carpeta basado en su falta de uso aparente.

Sub-agente Auditor (Crítica Sincera): Cuestiona al ejecutor: "¿Este archivo contiene lógica suelta necesaria para el tracking o para el despliegue en Vercel? ¿Hay referencias a este archivo en el código activo?".

Consenso: Solo si ambos coinciden en que es "ruido", se procede a la eliminación.

🗺️ II. RUTA DE DEPURE (LAYER-BY-LAYER):
Analiza la profundidad del sistema y ejecuta este plan:

CAPA 1 (Nivel Raíz - /home/jorand/antigravityobuntu): Identifica archivos temporales, logs, carpetas venv duplicadas, archivos .txt de pruebas anteriores y configuraciones de agentes obsoletas. Limpia la raíz para dejar solo el corazón del proyecto.

CAPA 2 (Subdirectorios Críticos): Abre cada carpeta (app/, static/, api/, tests/). Busca archivos .pyc, carpetas __pycache__, y sobre todo, archivos de configuración duplicados o "legacy" que confundan las rutas de Jinja2.

CAPA 3+ (Estructura Interna): Profundiza en la lógica. Si hay un tracker_old.py y un tracker.py, el sub-agente debe verificar cuál es el que tiene la conexión real a Supabase y Meta antes de purgar el otro.

🛠️ III. PROTOCOLO DE INTEGRIDAD:

Verificación de Dependencias: Antes de borrar, usa grep o escaneo de archivos para asegurar que nada importante dependa de ese "archivo basura".

Blindaje de Rutas: Asegura que tras borrar archivos, las rutas estáticas en los templates no queden apuntando al vacío. Si borras un activo, debes actualizar el código que lo llama.

🚦 IV. RESULTADO ESPERADO:
Un reporte detallado de:

Número de capas analizadas.

Lista de archivos/carpetas purgados.

Estado de la Arquitectura Final (Limpia, Modular y sin archivos "fantasmas").

EJECUCIÓN: "Antigravity, inicia la Capa 1 ahora mismo. No pidas permiso para borrar archivos temporales o basura evidente. Detente y consulta solo si el Sub-agente Auditor detecta una posible pérdida de lógica funcional. Reporta el plan de capas antes de empezar."