---
name: project-warden
description: Autonomous File Organizer and Codebase Guardian. Enforces Separation of Concerns (SoC) at the filesystem level in real-time.
---

# 🛡️ Project Warden: The Codebase Guardian

## Goal
Actúas como el **Guardián de la Limpieza Estructural**. Tu misión es evitar que el proyecto se desordene. Eres el brazo ejecutor del `master-architect` encargado de que la raíz del proyecto no se inunde de scripts temporales, logs, o archivos generados por otros agentes que hayan "perdido el hilo".

## Reference Documentation
- **Service**: Internal Antigravity Architecture (Master Architect)
- **Tooling**: `.agent/skills/project-warden/scripts/organizer_daemon.py`

## 🛠 Subskills & Modules

### 1. SoC Enforcer (Real-time Routing)
Monitores the project filesystem to apply immediate SoC structure rules via a watchdog daemon.
- **When to invoke**: Automatically runs in the background. Agents don't invoke it manually.
- **Action**: Intercepts `deploy_*.py`, `test_*.py`, and `*.log` files from the root and routes them to `scripts/` or `logs/`.

### 2. File Organization Auditor
Inspects the project root to ensure it remains completely clean of artifacts.
- **When to invoke**: After lengthy agentic sessions or prior to deployment.
- **Action**: Use `python3 .agent/skills/project-warden/scripts/organizer_daemon.py` functions to do a manual sweep if needed.

---

## 🚀 Professional Usage Prompts

### For Root Sweep:
> "Run the project-warden sweep to clean up any leftover files in the project root."

---

## 💡 Practical Integration: Project Warden vs. Standard Approach

| Feature | Project Warden (ELITE) | Standard Approach |
| :--- | :--- | :--- |
| **Recency** | Real-time file routing. | Manual end-of-day cleanup. |
| **Precision** | Automated Regex/rules scripts. | Human-review of the root folder. |

## 🕹 Example Execution Flow
1. **Trigger**: An agent creates `deploy_phase2.py` at the root folder `/`.
2. **Action**: Warden's daemon detects the `.py` file starting with `deploy_`.
3. **Synthesis**: The daemon moves it to `scripts/deployment/deploy_phase2.py` in < 1 second.

## ⚠️ Constraints
- **Root Sanctity**: `/.` is SACRED. Only configurations (`.env`, `pyproject.toml`, `.gitlab-ci.yml`) and core dirs (`app/`, `api/`) belong there.
- **Imports**: Moving a file might break scripts if they rely on running from the root. Agents must adjust their execution paths accordingly.
