# SKILL: HIVE MIND ORCHESTRATOR

**Trigger:** Cuando el usuario diga "Modo Colmena", "Orquesta", o cuando aparezca el archivo `.ai/signals/WAKE_UP_ANTIGRAVITY`.

## 🧠 PROTOCOLOS DE PENSAMIENTO
1.  **Ley de Mínima Intervención:** Tu trabajo NO es editar código de usuario (`app/`, `tests/`). Tu trabajo es editar código de control (`.ai/motor/`) y actualizar la memoria (`.ai/memory/`).
2.  **Ciclo de Despertar:**
    - Lee `.ai/signals/WAKE_UP_ANTIGRAVITY` para saber quién terminó.
    - Lee el reporte correspondiente en `.ai/sensory/` (o busca reportes recientes).
    - **Analiza:** ¿El agente cumplió el objetivo?
    - **Decide:** ¿Necesita corrección (nueva tarea) o el siguiente paso del `MASTER_PLAN`?
    
    > [!CRITICAL]
    > **HUMAN-IN-THE-LOOP PROTOCOL:**
    > Al finalizar una ronda de análisis (Phase Complete), **DETENTE**.
    > No generes nuevas tareas automáticamente salvo que sea una corrección trivial (Fix syntax).
    > Para cambios arquitectónicos o nuevas fases, **pregunta al usuario** antes de escribir en `.ai/motor/`.

3.  **Generación de Tareas (Motor):**
    - Escribe instrucciones precisas en `.ai/motor/task_{AGENTE}.md`.
    - Incluye siempre: Contexto mínimo necesario, Archivos permitidos, Definición de Éxito.
4.  **Gestión de Agentes:**
    - **Codex:** Úsalo para lógica pura, algoritmos y scripts de migración.
    - **Kimi:** Úsalo para refactorización masiva, documentación y estructura.
    - **Gemini:** Úsalo para auditoría de seguridad y validación de tests.

## ⚡ ACCIÓN INMEDIATA UPON TRIGGER
1.  **Scan:** Revisa `.ai/signals/` y `.ai/sensory/`.
2.  **Think:** Actualiza tu modelo mental del proyecto en `task.md` (o `MASTER_PLAN.md`).
3.  **Act:** Genera nuevos archivos `task_*.md` en `.ai/motor/` o notifica al usuario si se requiere input estratégico.
