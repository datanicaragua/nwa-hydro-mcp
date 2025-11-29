# NWA Hydro MCP — Task Tracker

| Task                                      | Owner              | Due Date   | Status       | Notes                                                                                             |
| ----------------------------------------- | ------------------ | ---------- | ------------ | ------------------------------------------------------------------------------------------------- |
| Fusion Tool (Open-Meteo + CSV fallback)   | Gustavo (Data)     | 2025-11-27 | ✅ Completed | `fetch_climate_data` running with API-first + local archive fallback.                             |
| Science Tool (Hargreaves via PyETo)       | Gustavo (Science)  | 2025-11-27 | ✅ Completed | `calculate_hargreaves_eto` matches FAO-56 spec using `pyeto`.                                     |
| Intelligence Tool (Gemini 2.5 Flash Lite) | Gustavo (AI)       | 2025-11-28 | ✅ Completed | `generate_agronomist_insight` now async + JSON schema with `gemini-2.5-flash-lite`.               |
| FastMCP Server wiring (`server.py`)       | Gustavo (Backend)  | 2025-11-27 | ✅ Completed | Tools exposed via FastMCP for Claude Desktop.                                                     |
| Gradio UI (`app.py`) trend + insight view | Gustavo (Frontend) | 2025-11-28 | ✅ Completed | Connected to FastMCP stack, 7-day plot + insight copy polished; HF secrets path verified locally. |
| HF Spaces deployment & secrets            | Ops                | 2025-11-29 | ⏳ Pending   | Package Space assets, push `requirements.txt`, add `GOOGLE_API_KEY` secret.                       |
| Claude Desktop validation (Track 1)       | Ops                | 2025-11-29 | ⏳ Pending   | Run `mcp-inspector` + Claude Desktop demo after deployment.                                       |
| Submission package (video + README tags)  | Comms              | 2025-11-30 | ⏳ Pending   | Record 3-min demo, verify README badges, prep social post.                                        |
