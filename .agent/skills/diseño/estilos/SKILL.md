---
name: diseño-estilos
description: Sub-skill para gestionar la arquitectura del archivo input.css y las capas de estilos globales.
---

# Gestión de Arquitectura CSS

## Goal
Mantener el archivo `input.css` organizado, optimizado y fácil de escalar.

## Instructions
1. **Estructura de Archivo**: [`input.css`](file:///home/jorand/antigravityobuntu/static/src/input.css) debe mantener el orden:
   - Imports de Tokens.
   - Directivas Tailwind (`base`, `components`, `utilities`).
   - Capas personalizadas (`@layer`).
2. **Modificación Segura**: Al añadir nuevos estilos, asegúrate de no duplicar clases existentes.

## Constraints
- No romper las directivas `@tailwind` ya que son esenciales para el proceso de build.
- Limitar el uso de selectores ID; priorizar siempre clases reutilizables.
