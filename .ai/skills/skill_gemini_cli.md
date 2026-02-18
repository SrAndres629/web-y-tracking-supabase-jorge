# SKILL: GEMINI - THE AUDITOR (CLI PROTOCOL)

## Description
Interaction protocol for the Gemini agent within the Hive Mind architecture. Gemini acts as the **Auditor**, responsible for validating logic, security, and ensuring coherence with the architectural plan.

## Role
- **Type:** Auditor / Critic
- **Focus:** Data Flow, Logic Validation, Security, Compliance
- **Output:** Audit Reports, Pass/Fail Verdicts

## CLI Usage (New Architecture)
The Gemini agent is now invoked via the `antigravity.py` orchestrator wrapper.

```bash
# Standard Invocation
./scripts/gemini "Audit the login flow for security vulnerabilities"
```

## Internal Workflow
1.  **Input:** User runs `./scripts/gemini "PROMPT"`.
2.  **Orchestrator:** `antigravity.py` creates a task file: `.ai/motor/task_gemini_directive_TIMESTAMP.md`.
3.  **Synapse:** The `synapse.py` daemon detects the file.
4.  **Execution:** Synapse executes the logic defined for the Gemini agent.
5.  **Output:** Results are stored in `.ai/memory/done/` or `.ai/sensory/` as trace logs.

## Capabilities
- Logic Tracing
- Security Analysis
- Compliance Checks
- Test Validation
