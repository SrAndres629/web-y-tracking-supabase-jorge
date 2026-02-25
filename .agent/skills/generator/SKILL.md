# Skill Generator 🏗️

## Goal
Design, scaffold, and audit elite Antigravity skills. This skill ensures all new capabilities follow the "Gold Standard" architecture: professional `SKILL.md`, functional `scripts/`, deep `references/`, and reusable `resources/`.

## Reference Documentation
- **Service**: Internal Antigravity Architecture
- **Tooling**: `generator/scripts/scaffold_skill.py` (Elite Scaffolder)

## 🛠 Subskills & Modules

### 1. Architect (Scaffolding)
Generate a new skill with full folder hierarchy and professional templates.
- **When to invoke**: When tasked with creating a new specialized capability.
- **Action**: Use `python3 .agent/skills/generator/scripts/scaffold_skill.py "<name>" "<description>"`.

### 2. Quality Guardian (Auditing)
Audit existing skills for compliance with the Gold Standard.
- **When to invoke**: When the user requests a skill system health check or before a release.
- **Action**: Use `python3 .agent/skills/generator/scripts/audit_skills.py`.

### 3. Librarian (Organization)
Maintain the global registry of skills and ensure consistent naming conventions (kebab-case).
- **When to invoke**: During cleanup or refactoring phases.

---

## 🚀 Professional Usage Prompts

### For Skill Creation:
> "Scaffold a new ELITE skill named `cloudflare-security`. It should focus on Turnstile integration and WAF rules. Ensure the description mentions zero-trust architecture."

### For System Audit:
> "Run a global audit of all skills. Report any legacy skill that is missing the `/scripts` or `/references` directories."

---

## 🕹 Example Execution Flow
1. **Trigger**: "Create a skill for GitLab management."
2. **Action**: Run `scaffold_skill.py "gitlab-manager" "..."`.
3. **Synthesis**: "Skill `gitlab-manager` created with ELITE architecture. Ready for content population."

## ⚠️ Constraints
- **Structure**: Never create a skill without the 4 core subdirectories.
- **Documentation**: All `SKILL.md` files must include a "Professional Usage Prompts" section.
- **Naming**: Use `kebab-case` for skill directory names.