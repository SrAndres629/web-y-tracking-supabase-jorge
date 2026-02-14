# SKILL: GEMINI CLI PROTOCOL

## description
Interaction protocol for the Gemini CLI agent.

## syntax
```bash
gemini -p "YOUR PROMPT HERE"
```

## implementation details
- **Non-Interactive:** Requires `-p` flag to avoid opening TUI.
- **Argument Passing:** Content should be passed as a command line argument, NOT stdin.
- **Path:** `C:\Users\acord\AppData\Roaming\npm\gemini.cmd` (Windows)
