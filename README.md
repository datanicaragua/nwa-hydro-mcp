# NWA Hydro-Compute MCP 💧

> **Current Status:** 🏗️ Architecture Complete. Implementation Phase (Track 1 & 2).
> **Event:** [Hugging Face MCP 1st Birthday Hackathon](https://huggingface.co/MCP-1st-Birthday) > **Organization:** [Data Nicaragua](https://github.com/datanicaragua)

## 🚀 The Vision

**NWA Hydro-Compute** is not just another weather bot. It is a specialized **Hydrological Computational Engine** designed to bridge the gap between Large Language Models (LLMs) and rigorous scientific analysis.

Built as a satellite module for the **Nicaragua Weather Archive (NWA)** ecosystem, this project utilizes the **Model Context Protocol (MCP)** to expose deterministic tools to AI Agents, enabling them to answer complex questions like _"What is the water stress risk for this crop?"_ rather than just _"Is it raining?"_.

## 🌟 Key Differentiators

1.  **Scientific Compute Layer:** Implements the **Hargreaves Evapotranspiration Model (ETo)** to calculate water demand, going beyond simple data retrieval.
2.  **Data Fusion Engine:** Intelligently orchestrates data retrieval between the **Open-Meteo ERA5 API** and a **Local CSV Archive** (simulating ground station data fallback).
3.  **Agentic Native:** Designed from the ground up to be consumed by Claude Desktop, Gemini, and IDEs via standard MCP transport (`stdio`).

## 📂 Documentation & Architecture

We follow a strict **Clean Architecture** and **Context Anchoring** workflow.

- **[NT_000: Project Charter & Architecture](docs/technical_notes/NT_000_Project_Charter_and_Architecture_v1.0.md)**
  - _The "Silver Plan": Detailed scope of the Hargreaves implementation and folder topology._
- **[NT_001: AI-Driven Workflow & Security](docs/technical_notes/NT_001_AI_Driven_DevSecOps_Workflow_v1.0.md)**
  - _Our methodology for "Context Anchoring" and managing private-to-public release cycles._
- **[Strategic Plan (PDF)](docs/strategy/Plan_Estrategico_v1.0.pdf)**
  - _Original business case and hackathon strategy._

## 🛠️ Technology Stack

- **Protocol:** [Model Context Protocol (MCP)](https://modelcontextprotocol.io) (FastMCP)
- **Language:** Python 3.10+
- **Scientific Core:** `pyeto` (FAO-56 standards), `pandas`, `xarray`
- **Infrastructure:** Local-first development (`.venv`)

## 🗺️ Roadmap (17-Day Sprint)

- [x] **Phase 1: Architecture & Strategy** (✅ Done)

  - Defined "Bronze/Silver" Tool Scope.
  - Established Project Memory (`.ai/context`).
  - Configured Dev Environment (PEP 621).

- [ ] **Phase 2: Core Implementation (The Backend)** (🚧 In Progress)

  - **Tool A (Bronze):** `fetch_climate_timeseries` (Fusion Logic: API + CSV).
  - **Tool B (Silver):** `calculate_eto_hargreaves` (Scientific Logic).

- [ ] **Phase 3: Integration & Demo (The Frontend)**
  - Build Gradio 6 UI for visualization.
  - Record Demo Video: "AI Agent analyzing Nicaragua's drought risk".
  - Final Submission to Hugging Face Spaces.

---

_Built with ❤️ by [Data Nicaragua](https://github.com/datanicaragua) for the Open Source Community._
