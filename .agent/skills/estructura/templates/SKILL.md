---
name: estructura-templates
description: Sub-skill para gestionar plantillas de páginas específicas y fragmentos reutilizables (components).
---

# Gestión de Plantillas y Componentes HTML

## Goal
Asegurar que las páginas del sitio sigan una estructura modular y hereden correctamente de la base.

## Instructions
1. **Herencia**: Todas las páginas deben comenzar con `{% extends "layouts/base.html" %}`.
2. **Modularidad**: Si un elemento se repite en más de dos páginas, extráelo a un fragmento en `api/templates/components/` e inclúyelo usando `{% include ... %}`.
3. **Análisis**: Usa `python3 scripts/structure_manager.py info <ruta>` para verificar qué bloques está sobrescribiendo una página específica.

## Constraints
- Segurar que no haya IDs duplicados al usar fragmentos reutilizables.
- Mantener la lógica de negocio fuera de las plantillas (usar solo Jinja2 para presentación).
