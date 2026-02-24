# Antigravity Skill Ecosystem: Official Structure

## 📁 Directory Layout
Every Elite skill must follow this schema:
- `SKILL.md`: The brain/manual of the skill.
- `scripts/`: Python/Shell scripts for procedural logic (Level 4/5).
- `references/`: Official documentation, whitepapers, and best practices.
- `resources/`: HTML/JS snippets, JSON templates, or binary assets.
- `assets/`: Media files (if any).

## 📄 SKILL.md Anatomy
1. **Frontmatter**: Name and Description (Activation prompt).
2. **Rol/Goal**: Definition of the agent's identity.
3. **OODA Loop / Protocol**: The operational workflow.
4. **Instructions**: Low-level implementation rules.
5. **Métricas de Éxito**: Criteria to close the task.
6. **Constraints**: Safety and brand guardrails.

## 📈 Maturity Levels
- **Level 1 (Prompt)**: Simple instructions.
- **Level 2 (Referenced)**: Uses `references/` for context.
- **Level 3 (Resourced)**: Uses `resources/` for implementation.
- **Level 4 (Procedural)**: Uses `scripts/` to audit or execute.
- **Level 5 (Orchestrator)**: Calls other skills.
