# TASK: OPTIMIZATION IMPLEMENTATION

## 🛑 PERMISSIONS (STRICT)
- **WRITE ACCESS:** `app/config.py`, `.ai/sensory/optimization_report_codex.md`
- **READ ONLY:** `app/`, `tests/`

## 🧠 OBJECTIVE
Implement safe optimizations identified by Gemini/Kimi without breaking existing tests.
You are the **IMPLEMENTATION SPECIALIST**.

## ⛓️ CHAIN OF THOUGHT
1.  **Review Sensory Data:** Check `.ai/sensory/` for any "High Confidence" findings from Gemini or Kimi.
2.  **Target:** Focus on `app/config.py` to ensure `settings` export is clean (fixing the root cause of the previous `NameError` permanently if needed).
3.  **Verify:** Run `pytest tests/05_senior_audit/test_live_infrastructure.py` locally before finishing.
4.  **Report:** Create `optimization_report_codex.md`.

## 📝 OUTPUT
- Fix any remaining configuration smells in `app/config.py`.
- Report actions in `optimization_report_codex.md`.
