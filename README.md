# NWA Hydro-Compute MCP 💧

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![MCP](https://img.shields.io/badge/Protocol-MCP-green)
![Status](https://img.shields.io/badge/Status-War_Room_Mode-red)

**The specialized hydrological computational engine for the [Nicaragua Weather Archive](https://github.com/datanicaragua).**

_Built for the [Hugging Face MCP 1st Birthday Hackathon](https://huggingface.co/MCP-1st-Birthday) (Winter 2025)_

</div>

---

## 🚀 The Vision

**NWA Hydro-Compute** is not just another weather wrapper. It is a domain-specific **Intelligence Layer** designed to bridge the gap between raw climate data and actionable agronomic advice.

While generic bots answer _"Is it raining?"_, NWA Hydro-Compute answers **"What is the water stress risk for my crop?"** by combining deterministic science with semantic reasoning.

## 🏆 Hackathon Tracks & Eligibility

We are submitting this project to the following tracks:

| Track                      | Integration / Justification                                                                                                          |
| :------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| **Track 1: Building MCP**  | A robust **FastMCP Server** (`src/nwa_hydro`) exposing atomic tools for Data Fusion and Science. Compatible with **Claude Desktop**. |
| **Track 2: MCP in Action** | A **Gradio 6 Web UI** (`app.py`) that consumes these tools to visualize drought risk graphs.                                         |
| **Google Gemini Prize**    | **Core Integration.** We use **Gemini 2.5 Flash Lite** as an expert agronomist to interpret numerical ETo data into textual advice.   |

## 🌟 Key Differentiators

### 1. The "Smart Integrator" Stack

We don't reinvent the wheel. We orchestrate the best tools:

- **Data:** **Open-Meteo ERA5** (API) + **Local CSV Fallback** (Resilience).
- **Science:** **Hargreaves-Samani ETo Model** (native FAO-56 math) for deterministic water demand calculation.
- **Intelligence:** **Google Gemini 2.5 Flash Lite** for semantic reasoning with JSON schema enforcement.
- **Visualization:** **Plotly Express + Gradio 6** dual-axis chart (precipitation supply vs. ETo demand) with dark-mode readability.

### 2. Data Fusion Architecture

Most hackathon projects break if the API goes down. Ours features a **Fail-Safe Fusion Engine**:

- _Primary:_ Live API Fetch.
- _Fallback:_ Automatically switches to the NWA Local Archive (`data/local_station.csv`) if the API is unreachable or if ground-truth calibration is requested.

## 📂 Repository Structure

We follow **Clean Architecture** principles to separate Transport (MCP) from Logic (Domain).

```text
nwa-hydro-mcp/
├── app.py                  # Gradio Frontend (The Web Demo)
├── src/nwa_hydro/          # The MCP Server Package
│   ├── server.py           # FastMCP Entrypoint
│   └── tools/              # Atomic Logic
│       ├── fusion.py       # Data Fetching (API + CSV)
│       ├── science.py      # Hargreaves ETo Logic
│       └── intelligence.py # Gemini 2.5 Lite Integration
├── docs/                   # Strategy & Architecture Documentation
└── pyproject.toml          # PEP 621 Configuration
```

## 🛠️ Quick Start

### Prerequisites

- Python 3.10+
- `uv` or `pip`
- A Google AI Studio API Key (for the Intelligence layer)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/datanicaragua/nwa-hydro-mcp.git
    cd nwa-hydro-mcp
    ```

2.  **Set up the environment:**

    ```bash
    # Create virtual env
    python -m venv .venv
    # Activate (Windows PowerShell)
    .\.venv\Scripts\Activate.ps1
    # Install dependencies
    pip install -e .
    ```

3.  **Run the Server (MCP Mode):**

    ```bash
    # Starts the MCP server on stdio (for Claude Desktop)
    python src/nwa_hydro/server.py
    ```

4.  **Run the Demo (Web Mode):**

    ```bash
    # Starts the Gradio UI
    python app.py
    ```

### What's New in V5.0 (Scientific Gold Edition)

- Command Center layout with **site presets** (Matagalpa / El Crucero / Custom) that auto-fill coordinates.
- **Dual-axis Plotly Express chart** (bars = precipitation supply, line = ETo demand) with dark-mode grid/labels.
- **Progressive loading:** KPIs and charts render immediately; Gemini insight streams in a second step with a loading placeholder.
- **Skeleton KPIs** on first load to avoid blank dashboards; auto-load triggers the default analysis at page open.
- **Risk badges** in the Gemini insight (🔴/🟡/🟢) and an **About** accordion citing Hargreaves-Samani (1985), ERA5 reanalysis, and toolchain credits (Pandas, Plotly, Gradio).
- Footer links to **Gemini 2.5 Flash Lite, FastMCP, Claude Desktop, Open-Meteo API**, and the GitHub repo.

## 🗺️ 72-Hour Roadmap

- [x] **Phase 1: Architecture** (Strategy & Scaffolding Complete)
- [x] **Phase 2: Core Logic** (Data Fusion & Hargreaves Implementation)
- [x] **Phase 3: Intelligence** (Gemini Integration)
- [x] **Phase 4: UI Polish V5** (Command Center + About accordion + footer credits)
- [ ] **Phase 5: Deployment** (Hugging Face Spaces & Video)

---

<div align="center">
Built with ❤️ by <a href="https://github.com/datanicaragua">Data Nicaragua</a>
</div>

## 👥 Author

**Gustavo Ernesto Martínez Cárdenas** _Lead Data Scientist & Architect at NWA_

[![GitHub](https://img.shields.io/badge/GitHub-gustavoemc-black?logo=github)](https://github.com/gustavoemc)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/gustavoernestom)

## Development Setup
See `CONTRIBUTING.md` for setup, testing, and run commands.
