# NWA Hydro-MCP: User-to-Insight Flow (Pseudo-Diagram)

```
User (Gradio UI or Claude Desktop)
        |
        v
Input: latitude, longitude, date
        |
        v
Fusion Tool (fetch_climate_data)
    |-- Try Open-Meteo API
    |      |-- Success -> ClimateData(source="API")
    |      `-- Failure -> fallback to local CSV -> ClimateData(source="CSV")
    |
    v
Science Tool (calculate_hargreaves_eto, native FAO-56 math)
    |-- Compute ETo (mm/day) with Hargreaves
    `-- Output: EToResult(method="Hargreaves (Native)")
    |
    v
Intelligence Tool (generate_agronomist_insight)
    |-- Send EToResult to Gemini 1.5 Flash
    |-- Structured JSON response: summary, advice, risk_level
    `-- Graceful fallback if API key/error
        |
        v
Outputs
    |-- MCP tools: JSON strings for agents
    `-- Gradio: Markdown insight + 7-day ETo trend plot
```
