# AI ORCHESTRATION: The "Tag Team" Workflow (War Room)

This protocol defines the hand-off between agents to maximize speed during the 72h sprint.

## THE "V-FORMATION" WORKFLOW

### 1. Strategy & Design (Gemini Code Assist)

- **Trigger:** New feature start (e.g., "Implement Fusion Tool").
- **Role:** **The Architect**.
- **Task:** Read `NT_000`, design the Pydantic schema in `schemas.py`.

### 2. Implementation (GitHub Copilot)

- **Trigger:** Schema approved.
- **Role:** **The Builder**.
- **Task:** Write the function body in `fusion.py` using `httpx`. Handle standard errors.

### 3. Review & Optimize (Claude CLI / Code)

- **Trigger:** Code written.
- **Role:** **The Reviewer**.
- **Task:** "Review `fusion.py`. Identify edge cases where Open-Meteo API might fail and suggest robust fallback logic."

### 4. Execution (Codex CLI)

- **Trigger:** Code approved.
- **Role:** **The Executor**.
- **Task:** Run tests (`pytest`) and commit changes (`git`).

## CONTEXT INJECTION STRATEGY

All agents must be grounded in the same reality. Ensure these are always in context:

1.  `.ai/context/PROJECT_MANIFEST.md` (The Scope)
2.  `docs/technical_notes/NT_000_Project_Charter_and_Architecture_v1.0.md` (The Logic)
