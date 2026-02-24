---
name: jules-architect
description: Expert skill for Google Jules, the asynchronous coding agent. Includes API key configuration and expert task delegation.
---

# Jules Architect

## Goal
To efficiently orchestrate and delegate complex coding tasks to **Jules**, the asynchronous coding agent from Google. This skill manages CLI configuration, session handling, and leverages Jules' ability to solve non-trivial architecture and debugging tasks.

## Instructions

### 1. Configuration & Authentication
Ensure Jules is authenticated using the provided API Key.
- **API Key**: `AQ.Ab8RN6IQXZVqFk9aPQarjfw5C5cayTaHYIDd7Qroo1OkEZQz5g`
- **Setup**: In new environments, run `jules login` or ensure the key is correctly linked to the user's workspace.
- **Reference**: [Jules Getting Started](https://jules.google/docs)

### 2. Session Management
- **New Task**: Use `jules new` to start a new coding session. Describe the task clearly as Jules works best with well-defined PR-sized objectives.
- **Interactive UI**: Use the interactive TUI (Terminal User Interface) to monitor progress, review diffs, and approve/reject plans. Or use `jules teleport` to apply changes locally.
- **Reference**: [Jules CLI Reference](https://jules.google/docs/cli)

### 3. Advanced Workflows
Delegate "tedious" or "hard" tasks identified via other tools:
- **Example**: Analyze logs with `gemini` and pipe the hardest findings to `jules new`.
- **Remote Sessions**: Manage sessions across different machines using `jules remote list/pull`.

## Official Documentation Links
- **Portal**: [jules.google.com](https://jules.google.com)
- **Docs**: [jules.google/docs](https://jules.google/docs)
- **GitHub Action**: [google-labs-code/jules-action](https://github.com/google-labs-code/jules-action)

## Examples

### Input: "Delegate the security fix to Jules"
**Output**: 
1. `jules new "Fix security vulnerabilities in the authentication layer as identified in the security scan"`
2. Wait for Jules to generate a plan and show the session ID.

### Input: "Synchronize local changes with Jules' remote session"
**Output**:
1. `jules remote list`
2. `jules teleport <SESSION_ID>`

## Constraints
- **Asynchronous Awareness**: Remind the user that Jules works in the background and may take time to produce a complete plan.
- **Review Requirement**: Always recommend reviewing Jules' changes via `jules teleport` before committing.
- **Official-First**: Always cross-reference [jules.google/docs](https://jules.google/docs) for the latest CLI commands.
