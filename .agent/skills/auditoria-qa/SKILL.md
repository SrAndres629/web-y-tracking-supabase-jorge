---
name: auditoria-qa
description: La "conciencia técnica" del frontend. Se encarga de verificar la integridad visual, accesibilidad (WCAG), responsividad (8px grid) y salud de las rutas.
---

# 🛡️ Auditoría & QA - Jorge Aguirre Flores

## Propósito
Garantizar que cada cambio en el frontend sea de nivel **Silicon Valley**, sin errores técnicos, visuales o de accesibilidad. Actúa como el filtro final antes de dar por terminado un cambio.

## 🔎 Protocolo de Verificación
Esta skill se activa automáticamente después de cualquier cambio en `diseño`, `estructura` o `marca`.

### 1. Integridad de Rutas (404 Check)
- Verifica que cada `url_for` o ruta estática apunte a un recurso existente.
- Comprueba la integración de archivos `.webp` y sus fallbacks.

### 2. Rigor Visual (The 8px Rule)
- Inspecciona los archivos CSS en busca de "magic numbers" (ej. `padding: 17.5px`).
- Asegura que todos los espaciados sigan múltiplos de 8px (o 4px para micro-ajustes).

### 3. Responsividad & Overflows
- Detecta contenedores con anchos fijos que puedan romper el layout en móviles.
- Verifica que no exista **horizontal scroll** no deseado.

### 4. Accesibilidad (WCAG)
- Revisa el contraste de los textos (especialmente los dorados sobre negro).
- Asegura que todas las imágenes tengan atributos `alt` descriptivos.

## Instructions
1. **Auditoría Preventiva**: Antes de ejecutar un cambio, analiza si este puede romper la responsividad.
2. **Auditoría Post-Ejecución**: Ejecuta el comando de validación para confirmar que no se introdujeron errores:
   - `python3 scripts/auditoria_manager.py validate`
3. **Reporte de Fallos**: Si detectas un error, bloquea la finalización de la tarea y reporta el error específico.

## **References & Resources**
- **Standards**: Consulta `.agent/skills/auditoria-qa/resources/QA_CHECKLIST.md` para la lista de verificación obligatoria.
- **Accesibilidad**: Basado en las pautas WCAG 2.1 (Nivel AA).

## Examples
- **Input**: Cambio en el padding del service card.
- **QA Action**: "Detecto que el padding actual es de 20px. Para cumplir con el 8px grid, sugiero ajustarlo a 16px (2rem) o 24px (3rem)."
