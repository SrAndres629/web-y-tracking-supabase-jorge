# TASK: ARCHITECTURAL INTEGRITY AUDIT

## 🛑 PERMISSIONS (STRICT)
- **WRITE ACCESS:** `.ai/sensory/integrity_report_kimi.md`
- **READ ONLY:** `app/`, `main.py`, `.ai/skills/`

## 🧠 OBJECTIVE
Assimilate the codebase structure and find structural inconsistencies.
You are the **ARCHITECTURE ARCHITECT**.

## ⛓️ CHAIN OF THOUGHT
1.  **Scan Logic:** strict audit of imports in `app/services.py`, `app/tracking.py`, and `app/routes/`.
2.  **Async/Sync Harmony:** Verify that no *blocking* database calls (sync `def`) are being called from *async* routes without `run_in_threadpool`. this is CRITICAL for performance.
3.  **Error Handling:** Check if `try/except` blocks in `main.py` actually catch the exceptions raised in low-level modules.
4.  **Meta-Skill Check:** Verify if `meta_skill_engineering.md` is strictly followed in any new skill creation.

## 📝 OUTPUT
- Create `integrity_report_kimi.md` in `.ai/sensory/` with findings.
