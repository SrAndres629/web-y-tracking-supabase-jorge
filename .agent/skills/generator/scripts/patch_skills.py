#!/usr/bin/env python3
import os

def patch_skill(name, skills_dir=".agent/skills"):
    skill_path = os.path.join(skills_dir, name)
    if not os.path.exists(skill_path):
        print(f"Error: Skill '{name}' not found at {skill_path}")
        return

    subdirs = {
        "scripts": f"Automation and helper scripts for {name}.",
        "references": f"Technical documentation and best practices for {name}.",
        "resources": f"Reusable templates, schemas, and configurations for {name}.",
        "assets": f"Media assets and binary files for {name}."
    }

    print(f"🛠 Patching skill: {name}")
    for subdir, desc in subdirs.items():
        dir_path = os.path.join(skill_path, subdir)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            with open(os.path.join(dir_path, "README.md"), "w") as f:
                f.write(f"# {subdir.title()}\n\n{desc}\n")
            print(f"   + Created directory: {subdir}")

    # Check for SKILL.md
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        title = name.replace("-", " ").title()
        template = f"# {title} 🚀\n\n## Goal\nPlaceholder for legacy skill integration.\n\n## Reference Documentation\n- **Service**: Legacy\n\n## 🛠 Subskills & Modules\n(To be defined during modernization)\n\n---\n\n## 🚀 Professional Usage Prompts\n(To be defined during modernization)\n\n---\n\n## 🕹 Example Execution Flow\n(To be defined)\n\n## ⚠️ Constraints\n- None specified yet.\n"
        with open(skill_md_path, "w") as f:
            f.write(template)
        print(f"   + Created placeholder SKILL.md")

if __name__ == "__main__":
    legacy_skills = ["auditoria-qa", "gitlab-master-architect", "gitlab-duo-expert", "github-master-architect"]
    for skill in legacy_skills:
        patch_skill(skill)
    print("\n✅ Patching complete.")
