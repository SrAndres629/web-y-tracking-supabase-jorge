# TASK: CODEX - LOGIC REPAIR & ALGORITHMS

**Contexto:**
Se detectaron errores de lógica que comprometen la integridad de los datos (Retry Queue falsa y Modelos inconsistentes).

**Archivos Permitidos:**
- `app/retry_queue.py`
- `app/models.py`
- `app/services.py` (Error handling de Turnstile)

**Objetivo:**
1.  **RETRY QUEUE:** La función `_process_single_item` devuelve `True` pero no reenvía el evento. Implementa la lógica real de reenvío (llamada a `send_event` o similar).
2.  **MODELS:** `Visitor.timestamp` es `Optional[str]` pero la DB espera TIMESTAMP. Asegura la coherencia (usa `datetime` en Pydantic y serializa a ISO format).
3.  **TURNSTILE:** Corrige la lógica de `validate_turnstile` para que sea consistente (Fail Close vs Fail Open). Decide una política segura.

**Definición de Éxito:**
-   `retry_queue.py` funcional.
-   `models.py` tipado correctamente.
-   Reporte `report_codex.md` explicando los arreglos lógicos.
