# TASK: GEMINI - SECURITY & CRITICAL CONFIG FIX

**Contexto:**
La auditoría de Kimi encontró credenciales hardcodeadas y configuraciones duplicadas críticas. Prioridad ALPHA.

**Archivos Permitidos:**
- `git_sync.py`
- `app/config.py`
- `app/meta_capi.py` (para revisar lógica de Audit Mode)

**Objetivo:**
1.  **ELIMINAR SECRETOS:** Remueve `CLOUDFLARE_API_KEY` y emails de `git_sync.py`. Muévelos a `os.getenv()` o falla si no existen.
2.  **CORREGIR CONFIG.PY:** Elimina la línea duplicada de `UPSTASH_REDIS_REST_URL` y asegura que no haya otras redundancias.
3.  **UNIFICAR AUDIT MODE:** Revisa `app/meta_capi.py` y asegúrate de que use la configuración centralizada de `settings` en lugar de leer `os.getenv` directamente si es posible, o al menos que sea consistente.

**Definición de Éxito:**
-   `git_sync.py` limpio de credenciales reales.
-   `app/config.py` limpio de duplicados.
-   Reporte `report_gemini.md` confirmando la limpieza.
