# Antigravity Skills: Concepts & Guidelines

## Introducción a las Habilidades (Skills)

La creación de una habilidad en Antigravity sigue una estructura de directorio y un formato de archivo específicos. Esta estandarización garantiza que las habilidades sean portátiles y que el agente pueda analizarlas y ejecutarlas de manera confiable.

## Estructura de Directorios

Las habilidades pueden definirse en dos ámbitos:
- **Ámbito del espacio de trabajo**: `<workspace-root>/.agent/skills/`. Específicas del proyecto.
- **Ámbito global**: `~/.gemini/antigravity/skills/`. Disponibles en todos los proyectos.

Estructura típica:
```text
my-skill/
├── SKILL.md      # El archivo de definición (obligatorio)
├── scripts/      # [Opcional] Scripts en Python, Bash o Node
├── references/   # [Opcional] Documentación o plantillas
└── assets/       # [Opcional] Recursos estáticos (imágenes)
```

## El archivo SKILL.md

Este archivo es el "cerebro" de la Skill. Se compone de:
1. **YAML Frontmatter**: Metadatos (nombre y descripción). La descripción es vital para que el agente sepa cuándo activar la habilidad.
2. **Cuerpo en Markdown**: Instrucciones detalladas, objetivos, ejemplos y restricciones.

---

## Niveles de Habilidades

### Nivel 1: El router básico (git-commit-formatter)
Solo instrucciones. El agente sigue reglas para formatear una salida (ej. Conventional Commits).

### Nivel 2: Utilización de recursos (license-header-adder)
Usa archivos en `resources/` para evitar redundancia y alucinaciones en textos estáticos largos.

### Nivel 3: Aprendizaje con ejemplos (json-to-pydantic)
Usa patrones de *few-shot learning* mediante archivos en `examples/` para guiar al modelo.

### Nivel 4: Lógica procedimental (database-schema-validator)
Delega la validación o procesamiento a scripts deterministas en `scripts/` usando `run_command`.

### Nivel 5: El arquitecto (adk-tool-scaffold)
Combina scripts, plantillas y ejemplos para tareas complejas de generación de código o estructuras.
