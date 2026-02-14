# 🏗️ ARCHITECT MASTER DIRECTIVES: OPERATION CPA DOMINANCE

**FROM:** Senior Ad-System Architect
**TO:** Project Engineer (AI Agent)
**OBJECTIVE:** Finalize deployment and achieve perfect tracking balance for Meta Ads.

## 🔴 CRITICAL DIRECTIVE #1: LOCAL ENVIRONMENT STRESS TEST
Before even touching Vercel, you must verify the isolated root.
1.  **Dependency Integrity**: Run `pip install -r requirements.txt` in the new folder.
2.  **App Boot**: Execute `python main.py` and verify all routes (`/`, `/admin`) load without path errors.
3.  **DB Ping**: Ensure `database.py` establishes a successful ping (Local or Postgres based on .env).

## 🔴 CRITICAL DIRECTIVE #2: TRACKING AUDIT (SIGNAL BALANCE)
The tracking must be "Balanced" (Browser + Server).
1.  **Deduplication Audit**: Locate the `event_id` generation logic. It MUST be unique per session/conversion and match between Pixel (JS) and CAPI (Python).
2.  **Metadata Density**: Ensure the payload includes `fbc`, `fbp`, `client_ip`, and `user_agent`. Without these, Meta's algorithm is blind.
3.  **Payload Validation**: Log a mock conversion and verify the dictionary structure against Meta's Business SDK requirements.

## 🔴 CRITICAL DIRECTIVE #3: PRODUCTION LOCKDOWN & DEPLOY
1.  **Vercel Re-Alignment**: Link to the production environment.
2.  **Env Var Sync**: Verify `DATABASE_URL` (Port 6543) is set.
3.  **Deployment**: Execute `vercel --prod` and capture the final production URL.

## 🔴 CRITICAL DIRECTIVE #4: ANTI-CRASH "BLINDAJE"
1.  **Mandatory Pipeline**: NEVER push directly via `git push`. Always use `python git_sync.py`.
2.  **Integrity first**: Any change to `templates/` or `app/` MUST pass `test_template_integrity.py` and `test_boot_integrity.py`.
3.  **Zero-Tolerance Errors**: If the deployment script fails, you are FORBIDDEN from using `--force` unless the error is a false positive confirmed via manual audit.
4.  **Reference Log**: Document every fix in `ENGINEERING_LOG.md` to prevent regression.

## ⚪ MONITORING PHASE
Once LIVE, you will monitor the logs for any `500` errors. Any database failure at this stage is an ARCHITECTURAL FAIL. Fix immediately.

---
**ACKNOWLEDGE AND EXECUTE PHASE 1 IMMEDIATELY.**
