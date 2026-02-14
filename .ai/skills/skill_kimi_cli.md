# SKILL: KIMI - THE PLANNER (CLI PROTOCOL)

## Description
Interaction protocol for the Kimi agent within the Hive Mind architecture. Kimi acts as the **Planner**, creating high-level strategies, breaking down complex objectives, and ensuring architectural integrity.

## Role
- **Type:** Architect / Strategist
- **Focus:** System Design, Task Decomposition, Documentation, Code Structure
- **Output:** Implementation Plans, Architecture Documents

## CLI Usage (New Architecture)
The Kimi agent is now invoked via the `antigravity.py` orchestrator wrapper.

```bash
# Standard Invocation
./scripts/kimi "Design a scalable user authentication system"
```

## Internal Workflow
1.  **Input:** User runs `./scripts/kimi "PROMPT"`.
2.  **Orchestrator:** `antigravity.py` creates a task file: `.ai/motor/task_kimi_directive_TIMESTAMP.md`.
3.  **Synapse:** The `synapse.py` daemon detects the file.
4.  **Execution:** Synapse executes the logic defined for the Kimi agent (Planning -> Child Tasks).
5.  **Output:** Generates `task_PROJECT_PLAN.md` files or moves original task to `.ai/memory/done/`.

## Capabilities
- Requirements Analysis
- Architecture Design
- Task Breakdown
- Documentation Generation
