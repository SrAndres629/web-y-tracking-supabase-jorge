# Antigravity SoC Guidelines ⚖️🏗️

## 1. Single Responsibility Principle (SRP) for Skills
Every skill directory in `.agent/skills/` must have a **single, clear semantic domain**.
- **Bad**: `gitlab-master-architect` and `gitlab-architect` overlapping on "CI/CD management".
- **Better**: `gitlab-cicd` and `gitlab-issue-manager`.

## 2. The "Manager" Pattern for MCPs
Multi-tool MCPs should always be consolidated into 3 logical managers to prevent tool proliferation:
1. **Steering**: Navigation, Input, and Orchestration.
2. **Inspection**: Observation, Reading, and Logging.
3. **Analysis**: Profiling, Auditing, and Diagnostics.

## 3. Decoupled Thinking Architecture
- **Prompt vs. Workflow**: If a logical sequence is longer than 10 steps or requires specific dependencies, it should be an `.md` workflow in `.agent/workflows/`, not part of the system prompt.
- **Skill Task Offloading**: Skills should be used for **how** to do things (tool usage, domain logic), while the agent's core context remains focused on **what** to achieve (planning, user alignment).

## 4. Coupling Metrics
- **Cohesion (Internal)**: How much of the skill's logic is focused on the same goal.
- **Coupling (External)**: How many other skills or MCPs this skill depends on.
- **Granularity (Size)**: A skill is "too large" if its `SKILL.md` exceeds 300 lines or addresses more than 5 distinct sub-capabilities.
