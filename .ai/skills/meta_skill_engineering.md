# META-SKILL: SKILL ENGINEERING (RECURSIVE CAPABILITY)

> "Give a man a fish, and you feed him for a day. Teach a man to fish, and you feed him for life."

## 1. The Concept
This skill allows the Hive Mind (Agravity, Gemini, Kimi, Codex) to **expand its own capabilities** by creating new, reusable Skills. Instead of asking the user how to do something repeatedly, we document the process once and refer to it forever.

## 2. Skill Structure (`.ai/skills/SKILL_NAME.md`)
Every skill must follow this strict template to be understandable by all agents:

```markdown
# SKILL: [NAME]

## description
[Brief summary of what this skill does]

## prerequisites
- [Tool/Library needed]
- [Access level needed]

## protocol
1. [Step 1]
2. [Step 2]
   - *Example Command:* `run ...`
3. [Step 3]

## verification
- How to check if the skill was executed correctly.
```

## 3. The "Skill Factory" Protocol
When the User asks for a new ability (e.g., "Learn to deploy to Docker", "Learn to Audit SEO"):

1.  **Analyze Pattern:** Identify the repeated steps required to achieve the goal.
2.  **Abstract:** Generalized specific file paths to variables (e.g., `TARGET_FILE`).
3.  **Document:** Create the `.ai/skills/skill_[name].md` file.
4.  **Register:** Notify all agents (via a shared context update or just finding it in the folder) that a new skill exists.

## 4. Usage Directives for Agents
- **Gemini:** If you are asked to "Create a Skill", use this protocol.
- **Kimi:** If you find a gap in documentation, suggest creating a Skill.
- **Codex:** If you execute a complex bash sequence more than twice, convert it into a shell script referenced by a Skill.

## 5. Example: "Stop Terminal" Skill
**Context:** User needs to stop `synapse.py` remotely.
**Skill File:** `.ai/skills/skill_remote_shutdown.md`
**Content:**
> To stop the Hive Mind, create a file named `task_halt.md` in `.ai/motor/`. The system will detect it and `sys.exit(0)`.

---
**Status:** ACTIVE
**Version:** 1.0
