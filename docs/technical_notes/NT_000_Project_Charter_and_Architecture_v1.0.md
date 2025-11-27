# NT_000: Project Charter & Architecture (72h Sprint Edition)

**Date:** November 27, 2025
**Deadline:** November 30, 2025 (CRITICAL)
**Version:** 1.0 (War Room Edition)
**Status:** WAR ROOM MODE / ACTIVE EXECUTION
**Author:** Gustavo Ernesto Martínez Cárdenas (Data Nicaragua)
**Context:** Final Sprint (72 Hours) of MCP's 1st Birthday Hackathon (Winter 2025)

---

## 1. Strategic Pivot: "The Smart Integrator"

Due to the critical 72-hour remaining window, we are executing a focused strategy to maximize prize eligibility and delivery certainty. We move from a "Silver Plan" to a **"Smart Integrator"** strategy.

- **Primary Target:** **Google Gemini Award ($30k credits)** + **Main Track Prizes**.
- **Host Alignment:** Demonstration of the MCP Server using **Anthropic's Claude Desktop App** (Track 1) and a custom **Gradio Web UI** (Track 2).
- **Strategic Exclusions:** No Modal, No ElevenLabs, No OpenAI. Focus is on depth of integration, not breadth of APIs.

## 2. Scope: The "NWA Hydro-Intelligence" Stack

### 2.1. The MCP Backend (Geo-Processor)

A FastMCP server (`src/nwa_hydro/server.py`) exposing 3 atomic tools:

1.  **Tool A (Data): `fetch_climate_data`**
    - **Logic:** Hybrid fetch mechanism. Prioritizes **Open-Meteo ERA5 API** but automatically falls back to `data/local_station.csv` (NWA Archive simulation).
    - **Goal:** Robustness and Data Fusion demonstration.
2.  **Tool B (Science): `calculate_hargreaves_eto`**
    - **Logic:** Scientific implementation using `pyeto` library based on FAO-56 standards. Inputs: $T_{min}, T_{max}, T_{mean}, Lat$.
    - **Goal:** Domain expertise ("Compute over Retrieval").
3.  **Tool C (Intelligence): `generate_agronomist_insight`**
    - **Logic:** Orchestrates a call to **Google Gemini 1.5 Flash**.
    - **Prompt:** _"Analyze this water deficit (Precipitation - ETo) and provide a 3-bullet executive recommendation for a coffee farmer in Central America."_
    - **Goal:** Qualify for Google Prize ($30k) and "Creative" category.

### 2.2. The Frontend (Web Demo)

A **Gradio 6** interface hosted on Hugging Face Spaces (`app.py`).

- **Visuals:** `gr.Plot` displaying comparative time-series (Precipitation vs. ETo).
- **Insight:** `gr.Markdown` displaying Gemini's semantic recommendation.
- **Architecture:** The Gradio app imports the MCP server logic directly (as a Python library) to bypass protocol latency for the web demo, while the MCP Server remains compatible with Claude Desktop.

## 3. 72-Hour Roadmap (Daily Targets)

| Day        | Goal             | Deliverable Definition                                                          |
| :--------- | :--------------- | :------------------------------------------------------------------------------ |
| **Thu 27** | **Core Logic**   | Server running locally. Tools 1 (Fusion) & 2 (Science) passing `mcp-inspector`. |
| **Fri 28** | **Intelligence** | Tool 3 (Gemini) integrated. Basic Gradio UI (`app.py`) connected to logic.      |
| **Sat 29** | **Integration**  | Deploy to HF Spaces. Verify Claude Desktop connection locally.                  |
| **Sun 30** | **Submission**   | 3-min Video recording, README tags validation, Social Post.                     |

## 4. Repository Architecture & File Standard

Adheres to Clean Architecture, incorporating the new Intelligence module.

```text
nwa-hydro-mcp/
├── .ai/                        # [AI Governance]
│   ├── context/                # PROJECT_MANIFEST.md
├── data/                       # [Data Layer]
│   └── local_station.csv       # Fallback dataset (Nicaragua ground truth)
├── docs/                       # [Documentation]
│   ├── technical_notes/        # NT Series (This file)
│   └── strategy/               # Strategic Assets
├── src/                        # [Source Code]
│   └── nwa_hydro/              # Main Python Package
│       ├── __init__.py
│       ├── server.py           # FastMCP Entrypoint
│       ├── config.py           # Env Vars (GEMINI_API_KEY)
│       ├── schemas.py          # Pydantic Models (Data Contracts)
│       └── tools/              # [Domain Logic Layer]
│           ├── __init__.py
│           ├── fusion.py       # Data Fetching (API + CSV)
│           ├── science.py      # Pyeto/Hargreaves Logic
│           └── intelligence.py # Google Gemini Logic
├── tests/                      # [QA]
├── app.py                      # Gradio Frontend (Entrypoint for HF Spaces)
├── pyproject.toml              # Deps: mcp, gradio, google-generativeai, pyeto
└── README.md                   # Public Landing Page

```

## 5\. Development Stack

- **Runtime:** Python 3.10+
- **Protocol:** `mcp` (FastMCP)
- **AI Models:** Google Gemini 1.5 Flash (`google-generativeai`)
- **Scientific Libs:** `pyeto`, `pandas`, `xarray`
- **Frontend:** `gradio` (v6)

## 📚 Resources & References

- [Open-Meteo Docs](https://open-meteo.com/)
- [Google AI Studio](https://aistudio.google.com/) (For API Keys)
- [PyETo Documentation](https://pyeto.readthedocs.io/)

<!-- end list -->
