#!/usr/bin/env python3
import os

def audit_skills(skills_dir=".agent/skills"):
    print(f"🕵️ Auditing skills in {skills_dir}...\n")
    
    required_dirs = ["scripts", "references", "resources", "assets"]
    skills = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]
    
    total_skills = len(skills)
    issues_found = 0
    
    for skill in skills:
        skill_path = os.path.join(skills_dir, skill)
        missing = []
        for d in required_dirs:
            if not os.path.exists(os.path.join(skill_path, d)):
                missing.append(d)
        
        has_skill_md = os.path.exists(os.path.join(skill_path, "SKILL.md"))
        
        if missing or not has_skill_md:
            issues_found += 1
            print(f"❌ [LEGACY] {skill}:")
            if missing:
                print(f"   - Missing directories: {', '.join(missing)}")
            if not has_skill_md:
                print(f"   - Missing SKILL.md")
        else:
            print(f"✅ [ELITE] {skill}")
            
    print(f"\nAudit complete. {total_skills} skills scanned, {issues_found} need attention.")

if __name__ == "__main__":
    audit_skills()
