# SKILL: CODEX - THE BUILDER (CLI PROTOCOL)

## Description
Interaction protocol for the Codex agent within the Hive Mind architecture. Codex acts as the **Executor**, translating plans and architectural designs into functional code.

## Role
- **Type:** Implementation Specialist / Builder
- **Focus:** Code Generation, Refactoring, Bug Fixing, Algorithms
- **Output:** Source code files (`.py`, `.ts`, etc.), Unit Tests

## CLI Usage (New Architecture)
The Codex agent is now invoked via the `antigravity.py` orchestrator wrapper.

```bash
# Standard Invocation
./scripts/codex "Implement the user login endpoint"
```

## Internal Workflow
1.  **Input:** User runs `./scripts/codex "PROMPT"`.
2.  **Orchestrator:** `antigravity.py` creates a task file: `.ai/motor/task_codex_directive_TIMESTAMP.md`.
3.  **Synapse:** The `synapse.py` daemon detects the file.
4.  **Execution:** Synapse executes the logic defined for the Codex agent (Code Gen/Refactor).
5.  **Output:** Modified files in the codebase, execution logs in `.ai/sensory/`.

## Capabilities
- Implementation of Functions/Classes
- Refactoring Existing Code
- Writing Unit Tests
- Optimization
