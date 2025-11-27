# PROJECT_MANIFEST: NWA Hydro-Compute MCP

**Date:** November 27, 2025
**Maintainer:** Gustavo Ernesto Martínez Cárdenas (Data Nicaragua)
**Context:** Hugging Face MCP 1st Birthday Hackathon (Winter 2025)
**Role:** Single Source of Truth (SSOT) for AI Agents & Developers
**Status:** WAR ROOM MODE / ACTIVE EXECUTION

---

## Project Vision

**NWA Hydro-Compute** is a specialized computational engine designed to qualify for the **Google Gemini Prize** ($30k) and Main Track awards.

It bridges the gap between raw climate data and actionable agronomic advice by stacking three layers:

1.  **Data Fusion:** Robust fetching (API + CSV Fallback).
2.  **Scientific Compute:** Deterministic Evapotranspiration models (Hargreaves).
3.  **Semantic Intelligence:** **Google Gemini 1.5** acting as an expert agronomist to interpret the data.

## Stack Snapshot (Locked for Sprint)

- **Runtime:** Python 3.10+
- **Protocol:** [Model Context Protocol (MCP)](https://modelcontextprotocol.io) via `fastmcp`.
- **Intelligence:** **Google Gemini 1.5 Flash** (`google-generativeai`).
- **Frontend:** **Gradio 6** (`gradio`) hosted on Hugging Face Spaces.
- **Scientific Core:** `pyeto` (FAO-56 Standards), `pandas`, `xarray`, `numpy`.
- **Configuration:** `python-dotenv` (Secrets), `ruff` (Linting), `pydantic` (Validation).

## Architecture & Folder Topology

- `src/nwa_hydro/` – Core Logic Package.
  - `server.py`: FastMCP entrypoint (Transport Layer).
  - `config.py`: Environment variables (API Keys).
  - `schemas.py`: Shared Pydantic models (Data Contracts).
  - `tools/`: Atomic Logic Modules.
    - `fusion.py`: Data Fetching (Open-Meteo + CSV).
    - `science.py`: Hargreaves ETo Logic.
    - `intelligence.py`: Gemini API Integration.
- `app.py`: **Gradio Frontend Entrypoint.** Imports `src` directly for the web demo.
- `data/`: Local fallback datasets (`local_station.csv`).
- `docs/`: Design artifacts (`NT_000`, `NT_001`).

## Operating Principles (War Room Protocol)

1.  **The "Smart Integrator" Rule:** We do not build everything from scratch. We integrate **Open-Meteo** (Data) and **Gemini** (Insight) to create high perceived value with low code volume.
2.  **Fail-Safe Data Strategy:** The system must _never_ crash due to API downtimes. If Open-Meteo fails, `fusion.py` MUST silently switch to `local_station.csv` (Simulating NWA Archive).
3.  **Direct Integration for Demo:** The `app.py` (Gradio) should import `src.nwa_hydro.tools` directly as python functions. Do NOT attempt to make Gradio talk to the MCP server via `stdio` over the web; it is too fragile for a 3-day deadline.
4.  **Strict Typing:** All data passing between Tools must use Pydantic models defined in `schemas.py`.

## Roadmap (Hackathon Scope: 72-Hour War Room)

| Day / Phase                      | Target System   | Definition of Done (Criteria)                                                                                                                                                         |
| :------------------------------- | :-------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Thu 27** <br> _(Core Backend)_ | **Logic Layer** | 1. `fusion.py` retrieves ERA5 data and normalizes it to Pydantic.<br>2. `science.py` accurately calculates ETo using `pyeto`.<br>3. `server.py` passes `mcp-inspector` tests locally. |
| **Fri 28** <br> _(Intelligence)_ | **Gemini & UI** | 1. `intelligence.py` successfully calls Google Gemini API.<br>2. `app.py` (Gradio) renders a basic static graph from the fusion tool.                                                 |
| **Sat 29** <br> _(Integration)_  | **Deploy**      | 1. Project deployed to Hugging Face Spaces.<br>2. Secrets (`GEMINI_API_KEY`) configured in Space.<br>3. Local Claude Desktop successfully connects to the repository tools.           |
| **Sun 30** <br> _(Submission)_   | **Polish**      | 1. 3-Minute Demo Video recorded.<br>2. README tags (`building-mcp-track-1`, etc.) verified.<br>3. Social Media post published.                                                        |

## Coordination Notes

- **Primary Reference:** `docs/technical_notes/NT_000_Project_Charter_and_Architecture_v1.0.md` contains the specific logic for Hargreaves and Gemini Prompts.
- **Workflow:** Use the "Context Anchoring" meta-prompt before starting any coding task.
- **Testing:** Utilize `mcp-inspector` locally to debug server-client interactions.
- **Security:** NEVER commit `.env`. Use Hugging Face Secrets for the deployment phase.
