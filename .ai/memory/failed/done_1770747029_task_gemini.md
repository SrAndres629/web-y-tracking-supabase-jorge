# TASK: CRITICAL SECURITY & TRACKING FIXES

**Objective:** Secure the codebase and stop bleeding leads/data.

## 1. Security Hardening (Highest Priority)
**Files:** `git_sync.py`, `app/config.py`
**Instructions:**
- **[git_sync.py]** Remove `CLOUDFLARE_API_KEY` and `CLOUDFLARE_EMAIL` literals. Replace with `os.getenv(...)`.
- **[app/config.py]** Remove duplicate `UPSTASH_REDIS_REST_URL` definition.

## 2. Fix Lead Leakage (Tracking)
**File:** `app/routes/tracking_routes.py`
**Context:** We are ignoring leads that have Email but NO Phone.
**Instruction:**
- Locate `if event.event_name == 'Lead' and ctx['phone']:`
- Change to: `if event.event_name == 'Lead' and (ctx['phone'] or ctx['email']):`

## 3. Fix CAPI Blindness (Identity)
**File:** `app/routes/tracking_routes.py`
**Instruction:**
- In `_get_tracking_context`, enable `fb_id` extraction from `fbc` cookie even if `fbclid` query param is missing.
- Ensure `bg_send_meta_event` handles cases where `fbc` is reconstructed from `None` (avoid sending "fb.1.timestamp.None").

## 4. Fix QStash Blindness (Reliability)
**File:** `app/routes/tracking_routes.py`
**Instruction:**
- In `_dispatch_to_capi`, add a "Dead Letter" log if `publish_to_qstash` fails.
- Do NOT just ignore the failure. Log it to `logger.error` so we at least see it in logs.
