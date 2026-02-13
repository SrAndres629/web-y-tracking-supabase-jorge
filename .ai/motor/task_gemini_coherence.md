# TASK: DEEP DATA FLOW COHERENCE AUDIT

## 🛑 PERMISSIONS (STRICT)
- **WRITE ACCESS:** `.ai/sensory/coherence_report_gemini.md`
- **READ ONLY:** `app/`, `main.py`, `.env` (Check for secrets but DO NOT EDIT)

## 🧠 OBJECTIVE
Verify that data flows logically from Input -> Processing -> Output without mutation errors or type mismatches.
You are the **DATA FLOW SPECIALIST**.

## ⛓️ CHAIN OF THOUGHT
1.  **Map the Flow:** Trace variables from `tracking_routes.py` -> `services.py` -> `database.py`.
2.  **Identify Weak Points:** Where can a `None` value crash the app? Where is a Type mismatch possible?
3.  **Cross-Reference:** Check if Kimi has reported any import cycles in `.ai/sensory/`.
4.  **Report:** Generate a markdown report.

## 📝 INSTRUCTIONS
- **Trace the 'Lead' Event:** Follow a `Lead` event from the API call in `tracking_routes.py` through to `database.save_visitor` and `meta_capi.send_event`.
- **Identify Gaps:**
  - Are we validating `email` format before database insertion?
  - are we handling `None` values for optional fields like `custom_data` correctly in `meta_capi`?
  - Is there any risk of SQL injection in `database.py`?
- **Output:** Create `coherence_report_gemini.md` in `.ai/sensory/` with findings.
