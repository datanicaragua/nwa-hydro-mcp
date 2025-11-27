# Strategic Business Case: NWA Hydro-Compute (v2.0 War Room)

**Date:** November 27, 2025
**Status:** ACTIVE
**Version:** 2.0 (War Room Edition)
**Author:** Gustavo Ernesto Martínez Cárdenas (Data Nicaragua)
**Context:** Pitch Narrative for Hackathon Judges of MCP's 1st Birthday Hackathon (Winter 2025)
**Replaces:** `Plan_Estrategico_v1.0.pdf`

---

## 1. The Core Problem: "Generic Weather Bots"

The current market of AI weather assistants is saturated with "Retrieval Wrappers".

- **The Competitor:** A bot that simply calls OpenWeatherMap API and says: _"It will rain 50mm tomorrow."_
- **The Flaw:** This is raw data, not actionable insight. It answers _"What is the weather?"_ but fails to answer _"What does this mean for my crop?"_.

## 2. The NWA Solution: "Domain Compute Engine"

**NWA Hydro-Compute** is not a wrapper; it is a computational engine.
We differentiate by shifting the value proposition from **Data Retrieval** to **Scientific Computation**.

### The "Compute vs. Retrieval" Thesis

| Feature          | Competitor (Generic Bot) | NWA Hydro-Compute (Our Solution)          |
| :--------------- | :----------------------- | :---------------------------------------- |
| **Function**     | `get_forecast()`         | `calculate_water_balance()`               |
| **Data Source**  | Single API (Fragile)     | **Data Fusion** (API + Local Archive)     |
| **Insight**      | "It rained 10mm"         | "The water deficit is -5mm (Stress Risk)" |
| **Intelligence** | Generic LLM Chat         | **Gemini Agronomist** (Domain Expert)     |

## 3. How We Win (The Prize Strategy)

Our strategy maximizes points across the Judging Criteria by targeting specific high-value vectors:

### A. "Real-World Impact" (Google Prize Target)

By implementing the **Hargreaves Evapotranspiration Model**, we demonstrate a vertical use case (Agriculture) that is deeper than general-purpose assistants.

- **The Hook:** We use **Google Gemini** not to write poems, but to interpret hydro-climatic deficits for farmers. This qualifies us for the **$30k Gemini Prize** in the "Creative/Consumer" category.

### B. "Polished UI/UX" (Gradio Target)

Instead of a chaotic dashboard, we deliver a focused **Single-Page Application (SPA)** using **Gradio 6**.

- **Visuals:** A dedicated `gr.Plot` showing the "Supply vs. Demand" (Precipitation vs. ETo) curve.
- **Simplicity:** No login, no complex setup. Just "Select Municipality -> Get Insight".

### C. "Technical Complexity" (Main Track Target)

We demonstrate **Data Fusion**. Most hackathon projects break if the API goes down. Ours seamlessly falls back to the `local_station.csv` (NWA Archive), proving architectural robustness and "Enterprise-grade" thinking.

## 4. The 72-Hour Execution Pivot

To ensure delivery of this vision by November 30, we have scoped the project to a **"Smart Integrator"** model:

1.  **No Reinventing Wheels:** We use `pyeto` for science, `gradio` for UI, and `gemini` for intelligence.
2.  **No Infrastructure Overhead:** We exclude cloud orchestration (Modal) to ensure zero deployment friction on Hugging Face Spaces.
3.  **Focus on "The Demo Moment":** Every line of code written must serve the 3-minute video pitch. If it can't be shown in the video, it is out of scope.

---

## 5. Conclusion

**NWA Hydro-Compute** wins by being **Smarter**, not Bigger.
We don't need 10 APIs. We need **One Science** (Hargreaves), **One Intelligence** (Gemini), and **One Fusion Engine** (MCP). This is the path to the podium.
