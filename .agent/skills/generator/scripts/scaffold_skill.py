#!/usr/bin/env python3
import argparse
import os
import sys


def scaffold_skill(name, description, target_dir):
    """
    Scaffolds a new Antigravity skill structure.
    """
    skill_path = os.path.join(target_dir, name)

    if os.path.exists(skill_path):
        print(f"Error: Skill '{name}' already exists at {skill_path}")
        sys.exit(1)

    directories = ["scripts", "references", "assets", "resources"]

    try:
        os.makedirs(skill_path)
        for d in directories:
            os.makedirs(os.path.join(skill_path, d))

        # Create initial SKILL.md
        skill_md_path = os.path.join(skill_path, "SKILL.md")

        # Determine title from name
        title = name.replace("-", " ").title()

        template = f"""---
name: {name}
description: {description}
---

# {title}

## Goal
A brief description of what this skill aims to accomplish.

## Instructions
1. **Initial Step**: Describe what the AI should do first.
2. **Execution**: Describe how to use scripts in `scripts/` or resources in `resources/`.
3. **Completion**: How to present the final output.

## Examples
- **Input**: "Example user request"
- **Output**: "Example AI response following the skill's logic"

## Constraints
- List any behaviors to avoid or strict rules to follow.
"""
        with open(skill_md_path, "w") as f:
            f.write(template)

        print(f"Successfully scaffolded skill '{name}' at {skill_path}")

    except Exception as e:
        print(f"Error creating skill: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new Antigravity skill")
    parser.add_argument("name", help="Name of the skill (kebab-case recommended)")
    parser.add_argument("description", help="Activation description for the skill")
    parser.add_argument("--dir", default=".agent/skills", help="Directory where skills are stored")

    args = parser.parse_args()

    # Resolve target directory based on project root if running from within project
    # For now, assume relative to execution path or provide absolute path
    scaffold_skill(args.name, args.description, args.dir)
