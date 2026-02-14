# TASK: KIMI - CODE HYGIENE & REFACTORING

**Contexto:**
Tu auditoría encontró duplicación de código vergonzosa. Vamos a limpiar la casa.

**Archivos Permitidos:**
- `main.py`
- `app/routes/tracking_routes.py`
- `app/routes/pages.py`

**Objetivo:**
1.  **MAIN.PY:** Elimina el bloque duplicado de `logging.basicConfig`.
2.  **TRACKING_ROUTES.PY:** Elimina los imports duplicados de `app.database`.
3.  **IP EXTRACTION (DRY):** Detectaste lógica de extracción de IP duplicada en `pages.py` y `tracking_routes.py`. Crea (o sugiere en el reporte) una función helper `get_client_ip(request)` en un lugar común (ej. `app/utils.py` o `app/middleware/`) y úsala.

**Definición de Éxito:**
-   Archivos sin bloques de código repetidos.
-   Código más limpio y mantenible.
-   Reporte `report_kimi.md` con los diffs o acciones tomadas.
