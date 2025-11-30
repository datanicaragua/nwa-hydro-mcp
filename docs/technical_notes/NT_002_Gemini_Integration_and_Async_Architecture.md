# NT-002: Gemini Integration Fix, Async Architecture & Gradio 6 Diagnostics

| Metadata       | Details                                                |
| :------------- | :----------------------------------------------------- |
| **Date**       | 2025-11-29                                             |
| **Status**     | ✅ Implemented                                         |
| **Core Stack** | Gemini 2.5 Flash Lite, FastMCP, Gradio 6, Python 3.10+ |
| **Context**    | Critical Bug Resolution & Architecture Hardening       |

## 1. Context & Problem Statement

During the integration of the Intelligence Layer with the MCP Server and Gradio Frontend, we encountered three blocking vectors:

1. **Safety Filters:** Gemini 2.5 returning empty responses for agronomic data.
2. **Concurrency:** Synchronous calls blocking the UI/MCP Inspector.
3. **Version Mismatches:** Issues with outdated `google-generativeai` libs and undocumented parameters in **Gradio 6** (e.g., `theme` not accepted by `Blocks`).

## 2. Technical Solution: The "Defense-in-Depth" Strategy

### A. Gemini Safety Bypass (Lite + Schema)

We pivoted to **`gemini-2.5-flash-lite`** combined with strict **JSON Schema Enforcement**.

- **Critical Dependency Fix:** The schema feature requires the latest SDK.

  ```powershell
  pip install -U google-generativeai
  ```

  _Without this update, the `response_schema` parameter causes an `AttributeError`._

### B. Async Architecture Refactoring

Refactored `intelligence.py` and `server.py` to use `async/await`. This prevents the "Live Assistant" from freezing the entire application while waiting for the LLM.

### C. Gradio 6 Inspection & Configuration

Since we are using **Gradio 6**, standard documentation often lags behind the codebase. Findings:

- `theme` is **not** a valid argument to `gr.Blocks` (pass it only to `launch()`).
- Plotly Express is more stable than manual `go.Figure` for `gr.Plot`; we construct dual-axis charts by merging bar+line traces and setting dark-friendly fonts/grid.
- For UX, we separated fast rendering (climate fetch + KPIs + chart) from slow Gemini insight generation. Insight runs in a follow-up step, with placeholders to avoid blocking the UI.

We used Python's `inspect` module to validate parameters for `gr.Blocks` and `launch()` and avoided undocumented args.

## 3\. Operational Command Reference (Windows/PowerShell)

The following commands are the **standard operating procedure** for this project. Prefer the
cross-platform helper scripts in `scripts/` (they activate the venv, set `PYTHONPATH`, and
free ports automatically) and fall back to manual commands only for debugging edge cases.

### 1\. Running the MCP Inspector (Backend Test)

Used to validate the tool definitions (`server.py`) before integrating the UI.

```powershell
.\scripts\dev_inspector.ps1  # Windows
```

```bash
./scripts/dev_inspector.sh    # macOS/Linux
```

Manual fallback (PowerShell):

```powershell
$env:PYTHONPATH = "src"; fastmcp dev src/nwa_hydro/server.py
```

### 2\. Running the Intelligence Module Standalone (Unit Test)

Used to debug Gemini responses in isolation without spinning up the full server.

```powershell
$env:PYTHONPATH = "src"; python -m nwa_hydro.tools.intelligence
```

### 3\. Running the Full Application (Frontend + Backend)

The entry point for the demo.

```powershell
$env:PYTHONPATH = "."; .\.venv\Scripts\python.exe app.py

```

_Note: We use `\.venv\Scripts\python.exe` explicitly to avoid conflicts with global Anaconda installations._

## 4\. Troubleshooting Guide (Lessons Learned)

| Symptom                                             | Probable Cause                                                   | Fix Command / Action                                                                                                                                   |
| :-------------------------------------------------- | :--------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`AttributeError: ...response_schema`**            | Outdated Google SDK.                                             | `pip install -U google-generativeai`                                                                                                                   |
| **`TypeError: BlockContext.__init__() got an unexpected keyword argument 'theme'`** | Passing `theme` to `gr.Blocks` on Gradio 6.                         | Remove `theme` from `Blocks`; pass `theme=` only in `demo.launch(...)`.                                                                                |
| **`ImportError: relative import...`**               | Running script as `__main__` without package context.            | Prepend `$env:PYTHONPATH = "src";`                                                                                                                     |
| **`Finish Reason: SAFETY`**                         | Model hallucinating danger in scientific text.                   | Switch to `gemini-2.5-flash-lite` & enforce JSON.                                                                                                      |
| **`429 Too Many Requests`**                         | Open-Meteo API parallel fetching.                                | Added `asyncio.sleep(0.25)` in data fetch loop.                                                                                                        |
| **Dev Server Failed (FastMCP)**                     | Port locked or relative import error.                            | Use absolute imports in `server.py` (e.g., `from nwa_hydro.schemas...`).                                                                               |
| **Dark chart labels invisible**                     | Default Plotly colors on dark background.                        | Set `font.color='#e5e7eb'`, `gridcolor='#374151'`, transparent `plot_bgcolor/paper_bgcolor` in `render_chart`.                                         |
| **UI blocked ~20s on load (Gemini latency)**        | Insight generation tied to the main fetch.                       | Split UI flow: fetch/render KPIs+chart first; call Gemini in a separate `.then` with a placeholder message.                                            |
| **MCP Inspector `ERR_CONNECTION_REFUSED`**          | Browser/VPN blocks IPv6 loopback while inspector binds to `::1`. | Run the helper script (forces IPv4), temporarily disable VPN/Threat Protection, or allow `127.0.0.1` in the firewall.                                  |
| **Inspector "Invalid origin" / "Connection Error"** | UI missing proxy address/token.                                  | Copy both values printed by the helper script (e.g., `http://127.0.0.1:6277` and session token) into the Connection panel before pressing **Connect**. |

---

_Document generated for NWA Hydro MCP Project - Winter 2025 Hackathon._
