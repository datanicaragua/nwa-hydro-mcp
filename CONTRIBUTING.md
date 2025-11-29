# Contributing to NWA Hydro MCP

Thank you for your interest in contributing to **NWA Hydro MCP**! This project is part of the **NWA Clima** initiative, aiming to provide hydrological intelligence for Nicaraguan agriculture using Generative AI and standard scientific models.

We follow standard open-source best practices. This guide will help you set up your environment, run the application, and submit quality contributions.

---

## 🛠️ Development Setup (Quick Start)

We use standard Python tooling. Follow these steps to get your local environment ready in under 5 minutes.

### 1. Prerequisites

- **Python 3.10+**: Ensure python is in your PATH.
- **Git**: For version control.
- **Terminal**: PowerShell (Windows) or Bash/Zsh (macOS/Linux).

### 2. Environment Creation

We strictly use virtual environments to isolate dependencies.

```powershell
# 1. Create the virtual environment (.venv)
# This creates a lightweight Python installation in the .venv folder.
python -m venv .venv

# 2. Activate the environment (CRITICAL)
# You must see (.venv) at the start of your terminal line after this.
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# macOS/Linux:
# source .venv/bin/activate

# 3. Upgrade core tools
python -m pip install --upgrade pip
```

### 3. Install Dependencies

We install the project in **editable mode** (`-e`). This allows you to modify source code and see changes immediately without reinstalling.

```powershell
# Install core dependencies + development tools (testing, linting)
pip install -e .[dev]

# Critical: Ensure latest Google Generative AI SDK for schema support
pip install -U google-generativeai
```

### 4. Configure Secrets (API Keys)

This project requires a **Google Gemini API Key** for the Intelligence layer.

- **Get a Key**: [Google AI Studio](https://aistudio.google.com/) (Free Tier is sufficient).

### Option A: Temporary (Current Session)

```powershell
$env:GOOGLE_API_KEY = "AIzaSyD_YOUR_KEY_HERE"
```

### Option B: Persistent (Recommended)

Create a `.env` file in the project root (this file is git-ignored).

```ini
GOOGLE_API_KEY=AIzaSyD_YOUR_KEY_HERE
```

---

## 🧪 Quality Assurance (The "Definition of Done")

Before submitting a Pull Request, ensure your code passes these checks. We use **Ruff** for linting and **pytest** for testing.

### 1. Run Unit Tests

Validates the core logic (Physics, Schemas, Server wiring).

```powershell
python -m pytest
```

### 2. Verify Full Stack (Smoke Test)

Runs a script that actually calls the API and calculates ETo to ensure the pipeline is connected.

```powershell
python tests/verify_stack.py
```

_Expected Output:_ `✅ Insight Generation Success...`

### 3. Linting & Formatting

We enforce strict style rules. Run this to automatically fix formatting issues.

```powershell
python -m ruff check --fix .
```

### 4. Architectural Checklist

Before submitting code, ensure:

- **Async/Await:** All I/O bound functions (API calls) are `async`.
- **Type Safety:** Data classes (Pydantic) are used for strict validation.
- **No Secrets:** No hardcoded API keys in the source.
- **Clean Output:** No `Finish Reason: SAFETY` errors in the logs (use the Lite model + JSON Schema).

---

## 🚀 Running the Application

Due to our modular architecture (`src/nwa_hydro/...`), you **must** inject the `PYTHONPATH` for imports to work correctly. We provide **cross-platform scripts** to handle this automatically.

### 🛠️ Developer Scripts (Recommended)

We provide utility scripts in the `scripts/` folder that handle environment variables and port conflicts automatically. **Use these instead of manual commands.**

#### Run MCP Inspector (Backend Test)

Validates tool definitions and server connectivity. The helper script automatically
activates the virtual environment, sets `PYTHONPATH=src`, and clears ports `6274/6277`
before launching FastMCP.

**Windows (PowerShell):**

```powershell
.\scripts\dev_inspector.ps1
```

**Mac/Linux (Bash):**

```bash
chmod +x scripts/dev_inspector.sh  # First time only
./scripts/dev_inspector.sh
```

- Open the URL printed in the terminal (includes auth token).
- You should see the MCP Inspector interface.

#### Run Gradio App (Frontend Demo)

Launches the web interface for end-user interaction. The script mirrors the MCP helper
by activating the venv, exporting `PYTHONPATH=.`, and restarting Gradio on a clean port.

**Windows (PowerShell):**

```powershell
.\scripts\dev_gradio.ps1
```

**Mac/Linux (Bash):**

```bash
chmod +x scripts/dev_gradio.sh  # First time only
./scripts/dev_gradio.sh
```

- Open your browser at: `http://127.0.0.1:7860`
- You should see the "nwa-hydro-mcp" interface.

### 📝 Manual Commands (Advanced)

If you prefer running commands manually:

**Windows (PowerShell):**

```powershell
$env:PYTHONPATH = "src"; fastmcp dev src/nwa_hydro/server.py
$env:PYTHONPATH = "."; python app.py
```

**Mac/Linux (Bash):**

```bash
PYTHONPATH=src fastmcp dev src/nwa_hydro/server.py
PYTHONPATH=. python app.py
```

---

## 🔧 Troubleshooting & Diagnostics

Derived from **Technical Note NT-002**, here are solutions to common integration issues.

### Gradio 6 (Hackathon Edition)

We are using a pre-release version of Gradio. Standard documentation may lag behind the codebase. If you encounter `TypeError` regarding arguments in `gr.Blocks` or `launch()`, use this script to inspect available parameters:

```python
# diagnostic.py
import gradio as gr
import inspect
print(inspect.signature(gr.Blocks))
print(inspect.signature(gr.Blocks.launch))
```

### Common Issues Matrix

| Symptom                                                    | Probable Cause                                                | Fix                                                                                                                                         |
| :--------------------------------------------------------- | :------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------ |
| **`ImportError: relative import...`**                      | Running script without package context.                       | Ensure `$env:PYTHONPATH` is set (see above).                                                                                                |
| **`AttributeError: ...response_schema`**                   | Outdated Google SDK.                                          | `pip install -U google-generativeai`                                                                                                        |
| **`Finish Reason: SAFETY`**                                | Model hallucinating danger in scientific text.                | We use `gemini-2.5-flash-lite` to mitigate this.                                                                                            |
| **`429 Too Many Requests`**                                | Open-Meteo API rate limit.                                    | The app includes `asyncio.sleep(0.25)` throttling.                                                                                          |
| **`ERR_CONNECTION_REFUSED` opening MCP Inspector**         | FastMCP binds to IPv6 loopback and the browser/VPN blocks it. | Run the helper script (forces IPv4) and, if VPN/firewall still blocks `127.0.0.1`, temporarily allow local traffic or disable the VPN.      |
| **Inspector shows "Invalid origin" or "Connection Error"** | Proxy form missing latest address/token.                      | Copy the `Inspector Proxy Address` and `Proxy Session Token` printed by the script, paste them into the left panel, then click **Connect**. |
| **Ports 6274/6277 already in use**                         | Previous inspector crashed, zombie node process remains.      | Re-run `scripts/dev_inspector.*` (it cleans ports) or kill `node.exe` manually before starting again.                                       |

---

## 📂 Project Structure

- **`src/nwa_hydro/`**: Core application logic.
  - **`tools/`**: The three pillars of the system.
    - `fusion.py`: Data fetching (Open-Meteo + CSV fallback).
    - `science.py`: Physics engine (FAO-56 Hargreaves).
    - `intelligence.py`: LLM integration (Gemini).
  - **`server.py`**: FastMCP server definition and tool registration.
- **`app.py`**: The frontend UI (Gradio).
- **`tests/`**: Unit and integration tests.
- **`docs/`**: Documentation and strategic plans.

---

## 🤝 Contribution Workflow

1. **Fork & Clone**: Clone the repo to your local machine.
2. **Branch**: Create a feature branch (`git checkout -b feature/amazing-idea`).
3. **Code**: Implement your changes.
4. **Verify**: Run `pytest` and `ruff check`.
5. **Commit**: Use clear, descriptive commit messages.
6. **Push & PR**: Push to your fork and open a Pull Request against `main`.

### Best Practices

- **Keep it Simple**: Avoid over-engineering. We prioritize shipping working code.
- **Test Driven**: If you fix a bug, add a test case that reproduces it.
- **No Secrets**: NEVER commit API keys or credentials.

---

Happy Coding! 🌿💧

---

## 🌐 Language Standards

To ensure collaboration and accessibility for the global hackathon judges:

- **Code & Comments:** All source code, inline comments, and docstrings must be in **English**.
- **User-Facing Strings:** All output messages, UI labels, and error payloads must be in **English**.
- **Documentation:** READMEs and architectural docs should be written in **English**.

_Non-compliance may result in PR rejection._
