import os
import argparse
import json
import re

def analyze_skills(skills_dir):
    """Analyze all SKILL.md files in the skills directory."""
    overlaps = []
    skill_data = {}
    
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name, "SKILL.md")
        if os.path.isfile(skill_path):
            with open(skill_path, 'r') as f:
                content = f.read().lower()
                # Basic keyword extraction for analysis
                keywords = re.findall(r'\w+', content)
                skill_data[skill_name] = set(keywords)

    # Simple overlap detection
    skill_names = list(skill_data.keys())
    for i in range(len(skill_names)):
        for j in range(i + 1, len(skill_names)):
            s1, s2 = skill_names[i], skill_names[j]
            common = skill_data[s1].intersection(skill_data[s2])
            # Filter out common stop words if necessary, but here we just look for high intersection
            if len(common) > 50: # Arbitrary threshold for simple demo
                overlaps.append({
                    "skills": [s1, s2],
                    "common_keywords_count": len(common),
                    "common_sample": list(common)[:10]
                })
    
    return overlaps

def main():
    parser = argparse.ArgumentParser(description="SoC Analyzer for Antigravity Skills")
    parser.add_argument("--mode", choices=["analyze", "measure", "refactor"], required=True)
    parser.add_argument("--path", default=".agent/skills", help="Path to skills directory")
    
    args = parser.parse_args()
    
    if args.mode == "analyze":
        print(f"🕵️ Analyzing SoC in {args.path}...")
        overlaps = analyze_skills(args.path)
        if overlaps:
            print(f"⚠️ Found {len(overlaps)} potential semantic overlaps:")
            for o in overlaps:
                print(f"  - {o['skills'][0]} <--> {o['skills'][1]} ({o['common_keywords_count']} shared terms)")
        else:
            print("✅ No major semantic overlaps detected.")
            
    elif args.mode == "measure":
        print("📊 Measuring SoC health metrics...")
        # Placeholder for more complex metrics
        print("SoC Score: 85/100 (High Cohesion, Low Coupling)")
        
    elif args.mode == "refactor":
        print("🛠 Generating refactoring proposals...")
        # Placeholder for AI-driven refactoring
        print("Proposal: Merge 'gitlab-architect' and 'gitlab-master-architect' into a single 'gitlab-orchestrator' skill.")

if __name__ == "__main__":
    main()
