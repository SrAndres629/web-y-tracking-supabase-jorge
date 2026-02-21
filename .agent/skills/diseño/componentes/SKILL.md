---
name: diseño-componentes
description: Sub-skill para la gestión de componentes UI (Botones, Tarjetas, Efectos). Úsala para consultar o crear nuevas clases de diseño premium.
---

# Gestión de Componentes UI

## Goal
Crear y mantener componentes de interfaz que sigan la estética de lujo y alta conversión del sitio.

## Instructions
1. **Consultar Existentes**: Antes de crear uno nuevo, usa `python3 scripts/design_manager.py list` para ver qué componentes ya existen.
2. **Cumplir Patrones**: Asegúrate de que los componentes usen las variables de la skill `marca` (como `var(--luxury-gold)`).
3. **Definición**: Los componentes deben definirse dentro de la capa `@layer components` de Tailwind para mantener la especificad correcta.

## Constraints
- No usar valores hexadecimales directos; referenciar siempre a tokens de la marca.
- Mantener los nombres de clases en kebab-case y con prefijos descriptivos (ej: `btn-`, `card-`).
