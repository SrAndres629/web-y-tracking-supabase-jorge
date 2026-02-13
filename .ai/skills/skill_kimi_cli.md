# SKILL: KIMI CLI PROTOCOL

## description
Interaction protocol for the Kimi CLI agent.

## syntax
```bash
kimi "YOUR PROMPT HERE"
```

## implementation details
- **Non-Interactive:** Simply pass the prompt as the first argument.
- **Argument Passing:** Content should be passed as a command line argument, NOT stdin.
- **Encoding:** Requires `utf-8` environment.
- **Path:** `C:\Users\acord\.local\bin\kimi.exe` (Windows)
