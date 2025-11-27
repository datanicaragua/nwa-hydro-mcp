# AGENTS.md: NWA War Room Protocol

> **Standard:** [agents.md](https://agents.md) > **Context:** 72h Hackathon Sprint
> **Source of Truth:** Refer strictly to `.ai/context/PROJECT_MANIFEST.md` for project scope.

## 🤖 Agent Roster & Roles

This project utilizes a multi-model orchestration strategy. Agents must adhere to their specific roles to avoid conflict.

| Agent / CLI            | Role              | Superpower                   | Responsibility                                                                                           |
| :--------------------- | :---------------- | :--------------------------- | :------------------------------------------------------------------------------------------------------- |
| **Gemini Code Assist** | **The Architect** | Massive Context Window (1M+) | analyzing `NT_000`, designing `schemas.py`, generating high-level logic and integration strategies.      |
| **GitHub Copilot**     | **The Builder**   | IDE Integration / Speed      | Autocomplete, boilerplate generation, writing unit tests (`pytest`), and refactoring specific functions. |
| **Claude CLI**         | **The Reviewer**  | Reasoning / Nuance           | Code review, security auditing, and generating user-facing documentation (README/Video Scripts).         |
| **Codex CLI**          | **The Executor**  | Shell / Terminal             | Running scripts, managing git operations, and executing file system scaffolding.                         |

## ⚡ Operational Directives

1.  **Read First:** Before any output, ingest `PROJECT_MANIFEST.md`.
2.  **No Hallucinations:** If a library is not in `pyproject.toml`, do not suggest it.
3.  **War Room Mode:** Be concise. Code over chatter. Solutions over theory.
4.  **Tech Stack Lock:**
    - Backend: `fastmcp`
    - Frontend: `gradio` (v6)
    - AI: `google-generativeai`

## 🛡️ Safety Rails

- **Secrets:** Never output `.env` content.
- **Destructive Actions:** Ask for permission before `rm` or overwriting existing non-empty files.
