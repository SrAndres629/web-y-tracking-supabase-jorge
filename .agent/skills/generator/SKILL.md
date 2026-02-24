---
name: generator
description: Use this skill when the user asks to create, generate, or scaffold a new Antigravity skill.
---

# Skill Generator

## Goal
To automate the creation of a new Antigravity skill following the official directory structure and file format.

## Instructions
1. **Identify Skill Requirements**:
   - Extract the `name` (e.g., "my-new-skill") and a brief `description` of what the new skill should do.
   
2. **Execute Scaffolding**:
   - Use the internal script to create the directory structure and initial `SKILL.md`.
   - Run: `python3 .agent/skills/generator/scripts/scaffold_skill.py "<name>" "<description>"`
   
3. **Refine Generated Skill**:
   - Once the folder is created, navigate to `.agent/skills/<name>/SKILL.md`.
   - Complete the `Instructions`, `Examples`, and `Constraints` sections based on the specific goal of the new skill.
   - If the skill requires logic, add scripts to `.agent/skills/<name>/scripts/`.

4. **Reference Concepts**:
   - For detailed guidelines on skill composition (Level 1-5 patterns), refer to `references/CONCEPTS.md` within this skill folder.

## Constraints
- Always use kebab-case for skill names.
- Ensure the description for the new skill is descriptive enough to act as a proper "activation phrase".