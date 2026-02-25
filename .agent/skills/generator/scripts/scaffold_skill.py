#!/usr/bin/env python3
import argparse
import os
import sys

def scaffold_skill(name, description, target_dir):
    """
    Scaffolds a new Antigravity skill with ELITE architecture.
    """
    skill_path = os.path.normpath(os.path.join(target_dir, name))

    if os.path.exists(skill_path):
        print(f"Error: Skill '{name}' already exists at {skill_path}")
        sys.exit(1)

    # Elite structure: Scripts, References (Best Practices), Resources (Assets/Templates), Assets (Media)
    subdirs = {
        "scripts": "Automation and helper scripts for {name}.",
        "references": "Technical documentation and best practices for {name}.",
        "resources": "Reusable templates, schemas, and configurations for {name}.",
        "assets": "Media assets and binary files for {name}."
    }

    try:
        os.makedirs(skill_path)
        for subdir, desc in subdirs.items():
            dir_path = os.path.join(skill_path, subdir)
            os.makedirs(dir_path)
            # Create a professional README.md for each subdirectory
            with open(os.path.join(dir_path, "README.md"), "w") as f:
                f.write(f"# {subdir.title()}\n\n{desc.format(name=name)}\n")

        # Create the Gold Standard SKILL.md
        skill_md_path = os.path.join(skill_path, "SKILL.md")
        title = name.replace("-", " ").title()

        template = f"""# {title} 🚀

## Goal
{description}

## Reference Documentation
- **Service**: [Official Documentation URL]
- **MCP Server**: [Relevant MCP Server Name]

## 🛠 Subskills & Modules

### 1. [Module Name] (Responsibility)
Detailed description of what this module does.
- **When to invoke**: Usage trigger.
- **Action**: Tool call or script execution.

### 2. [Next Module]
- **When to invoke**: Usage trigger.

---

## 🚀 Professional Usage Prompts

### For [Action]:
> "Prompt example for the agent..."

---

## 💡 Practical Integration: [Skill] vs. [Alternative]

| Feature | {title} (ELITE) | Standard Approach |
| :--- | :--- | :--- |
| **Recency** | Real-time docs. | Training cutoff. |
| **Precision** | Automated scripts. | Manual steps. |

## 🕹 Example Execution Flow
1. **Trigger**: Event description.
2. **Action**: Subskill execution.
3. **Synthesis**: Response format.

## ⚠️ Constraints
- **Rule**: Critical constraint.
"""
        with open(skill_md_path, "w") as f:
            f.write(template)

        print(f"Successfully scaffolded ELITE skill '{name}' at {skill_path}")

    except Exception as e:
        print(f"Error creating skill: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new ELITE Antigravity skill")
    parser.add_argument("name", help="Name of the skill (kebab-case)")
    parser.add_argument("description", help="Skill mission statement")
    parser.add_argument("--dir", default=".agent/skills", help="Skill storage directory")

    args = parser.parse_args()
    # Resolve target directory relative to current working directory
    target = os.path.abspath(args.dir)
    scaffold_skill(args.name, args.description, target)
