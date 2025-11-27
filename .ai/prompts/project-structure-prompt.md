@workspace /new

**ACT AS:** Senior Python Architect & Open Source Maintainer.
**CONTEXT:** We are bootstrapping a new repository `nwa-hydro-mcp` for the "Hugging Face MCP Hackathon".
**ORGANIZATION:** Data Nicaragua (Private repo initially, public release later).
**GOAL:** Establish a "Gold Standard" project structure compliant with Clean Architecture, PEP 8, and Modern Python packaging standards.

**YOUR TASK:**
Please generate the content for the following 5 critical files. Use markdown code blocks for each file so I can easily copy-paste them.

### 1. `.ai/context/PROJECT_MANIFEST.md`

Create a "Project Memory" file that serves as the single source of truth for AI agents (like you) and developers. It must include:

- **Project Vision:** "Hydro-Compute MCP Server to provide hydrological intelligence to AI Agents."
- **Stack:** Python 3.10+, FastMCP (mcp SDK), Pandas, Xarray.
- **Hackathon URL:** `https://huggingface.co/MCP-1st-Birthday`
- **Architecture:** Explain the folder structure (`src/`, `docs/`, `tests/`).
- **Roadmap:** Phase 1 (Setup), Phase 2 (Hydro Tools), Phase 3 (Integration/Demo).

### 2. `pyproject.toml` (PEP 621 Compliant)

Generate a modern configuration file using `hatchling` or `setuptools` as the build backend.

- **Dependencies:** `mcp`, `pandas`, `xarray`, `python-dotenv`, `pydantic`.
- **Dev Dependencies:** `pytest`, `ruff` (for linting/formatting).
- **Metadata:** Name: `nwa-hydro-mcp`, Version: `0.1.0`, Authors: "Data Nicaragua".

### 3. `LICENSE`

Generate the full text of the **Apache License 2.0**. This is required for the Hackathon submission.

### 4. `src/nwa_hydro/server.py`

Create a robust "Hello World" MCP Server using **FastMCP**.

- Include comprehensive docstrings (Google Style).
- Create one sample tool: `get_server_health()` that returns a JSON status.
- Ensure it uses explicit type hinting (critical for MCP).

### 5. `.vscode/settings.json`

Generate workspace settings to enforce quality automatically:

- Enable "Format on Save".
- Set `ruff` as the default formatter and linter.
- Configure file exclusions for `__pycache__` and `.ai/`.

**CONSTRAINT:** Ensure all code is production-ready, modular, and ready for the initial `git commit`.
