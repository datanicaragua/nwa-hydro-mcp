# NT_001: AI-Driven War Room Workflow & Context Anchoring - Series NT_000 v1.0

**Date:** November 27, 2025
**Version:** 1.0 (War Room Edition)
**Author:** Gustavo Ernesto Martínez Cárdenas (Data Nicaragua)
**Context:** MCP's 1st Birthday Hackathon (Winter 2025)
**Status:** WAR ROOM MODE / ACTIVE EXECUTION

---

## 1. Introduction: Operation 72 Hours

This document updates the development workflow to align with the **"Smart Integrator" Strategy** defined in `NT_000` (72h Sprint Edition). Due to the critical deadline (Nov 30), the project has shifted from standard Agile development to a **High-Velocity "War Room" Protocol**.

The goal is to execute a complex integration (Gemini + MCP + Gradio) in under 4 days by leveraging aggressive AI Context Anchoring and ruthless scope management.

## 2. The "Context Anchoring" Methodology (Sprint Adaptation)

To prevent "drift" during this high-speed sprint, we rely on a strict **Meta-Prompt Protocol**:

- **The Artifacts:**
  - `NT_000` (The Scope: Gemini + Hargreaves).
  - `PROJECT_MANIFEST.md` (The Rules).
- **The Injection:** Every new chat session with an AI Assistant (Claude/Gemini) **MUST** start with the injection of these two documents.
- **The Rule:** "If it's not in NT_000, it doesn't exist." This prevents the AI from hallucinating features we cut (like Modal or ElevenLabs).

## 3. The Strategic Pivot Protocol (Decision Log)

On November 27, a critical review of the timeline vs. scope revealed a high risk of non-delivery. A **Strategic Pivot** was executed to maximize prize eligibility:

1.  **Scope Cut (The "No" List):**
    - **Modal & ElevenLabs:** Removed from scope. Rationale: High integration risk/latency for a developer new to Gradio.
    - **OpenAI:** Removed. Rationale: Redundant with Gemini/Anthropic.
2.  **Scope Focus (The "Yes" List):**
    - **Google Gemini 1.5:** Elevated to "Critical Path". Rationale: Qualifies for the largest prize pool ($30k) and adds high-value semantic intelligence to the app.
    - **Gradio 6:** Prioritized as the sole Frontend.

## 4. Security & Release Strategy (The Sunday Protocol)

Given the compressed timeline, security discipline is paramount to avoid leaking API Keys (Gemini) in the rush.

1.  **Strict Isolation:**
    - `.env` containing `GEMINI_API_KEY` is git-ignored globally.
    - Hugging Face Spaces Secrets management will be used for deployment, NOT hardcoded strings.
2.  **The "Squash" Release:**
    - We continue working in the **Private** repo (`datanicaragua/nwa-hydro-mcp`).
    - **Sunday Nov 30 (18:00 UTC):** Code Freeze.
    - **Sunday Nov 30 (19:00 UTC):** Execution of `git merge --squash` to create a clean, professional public history before flipping the repository visibility to **Public**.

## 5. Environment & Stack Alignment

To support the "Smart Integrator" stack, the environment has been locked:

- **Virtualization:** `python -m venv .venv` (Active).
- **New Critical Dependencies:**
  - `google-generativeai`: For the Intelligence Tool.
  - `gradio`: For the Web UI.
  - `fastmcp`: For the Backend.
- **Configuration:** `pyproject.toml` has been updated to reflect these non-negotiable requirements.

## 6. Troubleshooting & Lessons Learned

- **Issue:** `TypeError: FastMCP.__init__()` (Legacy).
  - **Status:** Resolved.
- **Issue:** Gradio Learning Curve.
  - **Mitigation:** We are bypassing complex Gradio custom components. We will use standard `gr.Plot` and `gr.Markdown` and import the MCP logic directly into `app.py` to avoid local networking complexity during the demo.

---

## 📚 Resources & References

- [NT_000: Project Charter (72h Sprint Edition)](./NT_000_Project_Charter_and_Architecture_v1.0.md)
- [Google AI Studio API Key Setup](https://aistudio.google.com/)
- [Hugging Face Spaces Secrets Management](https://huggingface.co/docs/hub/spaces-config-secrets)
