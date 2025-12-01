---
title: NWA Hydro Compute
emoji: 💧
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "6.0.1"
app_file: app.py
pinned: false
license: apache-2.0
tags:
  - building-mcp-track-01
  - mcp-in-action-track-01
short_description: Precision Water Risk Engine for Nicaragua
---

# NWA Hydro-Compute: Precision Water Risk Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![MCP](https://img.shields.io/badge/Protocol-MCP-green)
![Status](https://img.shields.io/badge/Status-Released_v1.0-success)

Hydro-Compute Dashboard v1.0](docs/images/nwa-dashboard-ui-v1.png)
<em>Figure 1: Live Dashboard v1.0 featuring Maplibre Geospatial Integration and Real-time Water Balance Analysis.</em>

**The specialized hydrological computational engine for the [Nicaragua Weather Archive](https://github.com/datanicaragua).**

_Built for the [Hugging Face MCP 1st Birthday Hackathon](https://huggingface.co/MCP-1st-Birthday) (Winter 2025)_

### 📺 Video Tour
[![NWA Hydro-Compute Demo](https://img.youtube.com/vi/pqjqM5uAjC8/0.jpg)](https://www.youtube.com/watch?v=pqjqM5uAjC8)

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
| **Google Gemini Prize**    | **Core Integration.** We use **Gemini 2.5 Flash Lite** as an expert agronomist to interpret numerical ETo data into textual advice.  |

## 🌟 Key Differentiators

### 1. The "Smart Integrator" Stack

We don't reinvent the wheel. We orchestrate the best tools:

- **Data:** **Open-Meteo ERA5** (API) + **Local CSV Fallback** (Resilience).
- **Science:** **Hargreaves-Samani ETo Model** (native FAO-56 math) for deterministic water demand calculation.
- **Intelligence:** **Google Gemini 2.5 Flash Lite** for semantic reasoning with JSON schema enforcement.
- **Visualization:** **Plotly Express + Gradio 6** dual-axis chart (precipitation supply vs. ETo demand) with Dark Mode UI readability and Geospatial Visualization via **Maplibre** for site context.

### 2. Data Fusion Architecture

Most hackathon projects break if the API goes down. Ours features a **Fail-Safe Fusion Engine**:

- _Primary:_ Live API Fetch.
- _Fallback:_ Automatically switches to the NWA Local Archive (`data/local_station.csv`) if the API is unreachable or if ground-truth calibration is requested.

## 🏗️ System Architecture

The v1.0 pipeline ingests Open-Meteo ERA5 data, normalizes it through the fusion engine, computes Hargreaves-Samani ETo, and serves both the Maplibre front-end and Gemini insights while falling back to the local archive when needed.

![System Architecture and Data Flow](docs/images/nwa-system-architecture-v1.png)
<em>Figure 2: End-to-End Data Pipeline: From Open-Meteo ingestion to Gemini 2.0 Flash insights.</em>

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

## 🛡 V5.1 "Command Center" Release Features

- **Interactive Map Context:** Location inputs are paired with Maplibre geospatial visualization, site presets (Matagalpa/Dry Corridor), and visual context for sponsors.
- **Dual-Axis Intelligence:** Plotly charts explicitly show the gap between **Supply** (Precipitation bars) and **Demand** (ETo line) in a specialized Dark Mode UI.
- **Progressive Loading:** The UI never freezes; KPIs load instantly while Gemini 2.5 Flash Lite processes the agronomic reasoning asynchronously.
- **Scientific Transparency:** Full disclosure of the Hargreaves-Samani methodology and ERA5 data sources directly in the UI "About" accordion.

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
