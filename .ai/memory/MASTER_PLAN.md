# MASTER PLAN: System Optimization & Hive Mind Integration

## 👤 USER DIRECTIVES (THE CHAIRMAN'S VOICE)
> [!IMPORTANT]
> **This section is the Highest Authority.** 
> Use this area to pause, redirect, or abort operations. Antigravity checks this first.
>
> **Current Order:** "Monitor progress. Do not auto-loop indefinitely. Request approval after Phase 2."

## 📍 CURRENT STATE (AS OF INITIALIZATION)
**Project:** Jorge Aguirre Flores Web Core
**Architecture:** Serverless Hybrid (Vercel FastAPI + Supabase + Redis + Cloudflare)
**Critical Components:**
-   **Tracking:** Dual-layer (Pixel + CAPI) via `app/meta_capi.py`.
-   **Database:** Supabase with Transaction Pooling (`git_sync.py` checks).
-   **Performance:** Edge Caching (Cloudflare) + Async Python.
-   **Orchestration:** Antigravity (Supervisor) + Agents (Codex, Kimi, Gemini) via `.ai/motor`.

## 🎯 STRATEGIC OBJECTIVE (THE ORDER)
"Maximize ROI and Minimize CPM/CPE in Meta Ads through architectural perfection."
*Sub-goals:*
1.  **Perfect Deduplication:** Ensure `event_id` uniqueness and persistence in Redis.
2.  **Infrastructure Integrity:** Zero-defect deployment via `git_sync.py`.
3.  **SEO/Performance:** <100ms TTFB to improve Ad Quality Score.

## 🧠 HIVE MIND ROLES
-   **Codex:** Mathematical Logic & Algorithms (Tracking Math, Deduplication).
-   **Kimi:** Structural & Documentation (SEO, Templates, Performance).
-   **Gemini:** Audit & Security (CAPI integrity, API leaks).
-   **Antigravity:** Orchestrator (Strategy, Task Assignment, Verification).

## 🚀 ROADMAP
### Phase 1: Injection (Current)
- [x] Build Nervous System (`.ai/synapse.py`).
- [x] Initialize Memory (`MASTER_PLAN.md`).
- [x] Define Skill (`.ai/skills/orchestrator.md`).

### Phase 2: First Spark (Completed)
- [x] **Kimi:** Audit Templates for Performance/SEO.
- [x] **Codex:** Verify `app/tracking_math.py` (if exists) or core logic for deduplication.
- [x] **Gemini:** Audit `app/meta_capi.py` for API security.

### Phase 3: "Operation Clean Sweep" (Current - Kimi's Audit Fixes)
**CRITICAL (Immediate Action):**
- [ ] **Gemini:** Fix Hardcoded Secrets (`git_sync.py`, `.env`) & Duplicate Config (`app/config.py`).
- [ ] **Kimi:** Fix Duplicate Logging (`main.py`) & Duplicate Imports (`tracking_routes.py`).
- [ ] **Codex:** Fix Retry Logic (`retry_queue.py`) & Model Inconsistencies (`models.py`).

**MAJOR (Secondary):**
- [ ] Centralize IP Extraction (`middleware`).
- [ ] Unify Audit Mode logic.
- [ ] Fix HTTP Client closure.

### Phase 4: Recursive Improvement
-   Antigravity analyzes reports -> Updates Master Plan -> **STOPS FOR USER APPROVAL** -> Assigns new Tasks.
