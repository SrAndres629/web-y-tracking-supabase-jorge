# AI Context & System Architecture

> **Purpose**: This document provides high-signal context for AI agents (Gemini, Copilot, Cursor) analyzing this repository. It summarizes the system's architecture, critical components, and verification protocols.

## 🧠 System Overview
**Project**: Jorge Aguirre Flores - Web & High-Fidelity Tracking System
**Core Goal**: Precision tracking of ad conversions (Meta CAPI) with mathematical proof of integrity.
**Tech Stack**:
- **Backend**: FastAPI (Python 3.12+), Serverless (Vercel Adapter via Mangum).
- **Database**: Supabase (PostgreSQL) / SQLite (Local/Dev).
- **Frontend**: Jinja2 Templates + TailwindCSS (Performance-Oriented).
- **Infrastructure**: Cloudflare (Edge Caching), Redis (Deduplication/Rate Limiting).

## 🛡️ "Silicon Valley" Verification Protocol
The repository enforces a strict **Zero-Defect Policy** via `tests/` and `git_sync.py`.
- **The Iron Gate**: Deployment is BLOCKED if `pytest -W error` fails. No warnings allowed.
- **Mathematical Proofs (`tests/unit/test_tracking_math.py`)**:
    - Uses `hypothesis` property-based testing.
    - **Proves**: Deduplication Idempotency (f(f(x)) = f(x)), Hashing Consistency, Collision Resistance.
- **Placeholder Audit (`tests/test_placeholders.py`)**: Scans for "INSERT_KEY", "TODO", etc., to prevent AI hallucinations in prod.

## 📂 Key File Map
| Path                               | Purpose                                                                                 | Criticality |
| :--------------------------------- | :-------------------------------------------------------------------------------------- | :---------- |
| `git_sync.py`                      | **Deployment Orchestrator**. Runs the Iron Gate, syncs git, deploys to Vercel.          | 🚨 CRITICAL  |
| `app/routes/tracking_routes.py`    | **Core Tracking Logic**. Handles pixel events, CAPI conversion, and data normalization. | 🚨 CRITICAL  |
| `tests/unit/test_tracking_math.py` | **Mathematical Proofs**. The source of truth for tracking integrity.                    | 🚨 CRITICAL  |
| `app/config.py`                    | Centralized configuration (Pydantic). Handles env vars and defaults.                    | HIGH        |
| `app/database.py`                  | Database connection factory. Includes **Deterministic Guard** (SQLite fallback).        | HIGH        |
| `api/templates/layouts/base.html`  | Base HTML layout. Contains SEO meta tags and script injections.                         | MEDIUM      |

## 🚀 Deployment Pipeline (`git_sync.py`)
1.  **Environment Check**: Verifies `pytest`, `hypothesis` installed.
2.  **The Iron Gate**: Runs full test suite in strict mode.
3.  **Stage & Commit**: Saves local state.
4.  **Sync & Rebase**: Pulls remote changes linearly.
5.  **Push**: Triggers Vercel deployment.
6.  **Purge**: Clears Cloudflare Edge Cache.

## ⚠️ AI Context Constraints
- **Ignored Files**: `venv/`, `__pycache__/`, `.env` (Secrets), `*.log`.
- **Focus Areas**: Start analysis at `app/routes/` for logic or `tests/` for verification.
