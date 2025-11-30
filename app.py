from datetime import datetime, timedelta
from textwrap import dedent

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

import gradio as gr
import pandas as pd
import plotly.express as px

from src.nwa_hydro.tools.fusion import fetch_climate_data, fetch_climate_range
from src.nwa_hydro.tools.intelligence import generate_agronomist_insight
from src.nwa_hydro.tools.science import calculate_hargreaves_eto
from src.nwa_hydro.schemas import EToResult


SITES = {
    "Matagalpa (Coffee High - 1400m)": (12.9256, -85.9189),
    "El Crucero (Coffee Low - 900m)": (11.9903, -86.3087),
    "Custom Coordinates": None,
}

OCEAN_STYLE = """
<style>
:root {
  --ocean-bg: #0b1221;
  --ocean-panel: #111a2e;
  --ocean-accent: #4f7df3;
  --ocean-accent-soft: #9bc2ff;
  --ocean-text: #e9f1ff;
  --ocean-muted: #9fb0c7;
  --kpi-temp: #ff8a5c;
  --kpi-precip: #4f7df3;
  --kpi-humidity: #7dd3fc;
}
body {background: var(--ocean-bg); color: var(--ocean-text);}
.kpi-row {display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 14px;}
.kpi-card {background: linear-gradient(145deg, #111a2e, #0e182b); padding: 16px 18px; border-radius: 14px; display: flex; align-items: center; gap: 12px; box-shadow: 0 8px 26px rgba(0,0,0,0.35); min-height: 84px;}
.kpi-icon {font-size: 22px; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.35));}
.kpi-label {text-transform: uppercase; letter-spacing: 0.6px; font-size: 11px; color: var(--ocean-muted); margin-bottom: 4px;}
.kpi-value {font-size: 26px; font-weight: 800; color: var(--ocean-text); line-height: 1.1;}
.kpi-temp .kpi-value {color: var(--kpi-temp);}
.kpi-precip .kpi-value {color: var(--kpi-precip);}
.kpi-humidity .kpi-value {color: var(--kpi-humidity);}
.panel {background: var(--ocean-panel); border-radius: 14px; padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.25);}
.header-title {font-size: 28px; font-weight: 800; margin: 0;}
.subtle {color: var(--ocean-muted);}
.cta-btn button {width: 100%; background: linear-gradient(135deg, #4f7df3, #6a5cf5); color: white; font-weight: 800; letter-spacing: 0.3px; border: 1px solid rgba(255,255,255,0.12); box-shadow: 0 10px 24px rgba(79,125,243,0.35);}
.cta-btn button:hover {transform: translateY(-1px); box-shadow: 0 14px 30px rgba(79,125,243,0.45);}
.cta-btn button:active {transform: translateY(0);}
.hero {background: linear-gradient(135deg, #0c284f, #122c63 55%, #172a4d); border-radius: 14px; padding: 14px 18px; color: #e9f1ff; box-shadow: 0 10px 28px rgba(0,0,0,0.35); margin-bottom: 12px;}
.hero-title {font-size: 24px; font-weight: 800; margin: 0;}
.hero-sub {color: var(--ocean-accent-soft); font-weight: 600; margin-top: 4px;}
.footer {text-align: center; color: var(--ocean-muted); margin-top: 16px; font-size: 13px;}
.footer a { color: #e9f1ff !important; text-decoration: underline; font-weight: 600; transition: color 0.2s ease-in-out; }
.footer a:visited,
.footer a:active { color: #e9f1ff !important; }
.footer a:hover { color: #9bc2ff !important; text-decoration: underline; }

.custom-accordion .icon { color: #9bc2ff !important; }
.custom-accordion { background: #18233a !important; border-radius: 8px; border: 1px solid #4f7df3; }
.custom-accordion button { color: #e9f1ff !important; font-weight: 700; }
</style>
"""

ABOUT_MD = """
### 1. Application Purpose
The **Nicaragua Weather Archive** is a visualization tool designed to facilitate access to and analysis of historical meteorological data. Its goal is to **empower citizens, students, farmers, and researchers** by enabling them to explore climate trends and make data-driven decisions.

### 2. Data Source
- **Primary Provider:** Data is sourced via the [Open-Meteo API](https://open-meteo.com/).
- **Source Model:** **ERA5**, the fifth-generation atmospheric reanalysis of the global climate by **ECMWF**.
- **What is "Reanalysis"?** Think of ERA5 as a high-tech "climate historian." It combines billions of observations (satellites, ground stations) with advanced physics models to reconstruct past weather globally, even in areas without stations.

### 3. Calculation Methodology
- **Mean Temp:** The true average of 24 hourly estimates (not just (Max+Min)/2).
- **Total Precipitation:** Cumulative sum for the selected period.
- **ETo (Evapotranspiration):** Calculated using the **Hargreaves-Samani (1985)** equation, calibrated for regional conditions when direct radiation data are missing.

### 4. Accuracy & Limitations
- **Nature of Data:** High-quality *estimates* for a grid area (~11km resolution), not single-point measurements.
- **Resolution:** ERA5-Land (11km) for data from 1950+; ERA5 (30km) for older data.
- **Usage:** Excellent for trends and regional analysis. Complementary to local rain gauges.

### 5. Credits & Tools
- **Developer:** Gustavo Ernesto Martínez Cárdenas
- **AI Stack:** Google Gemini 2.5 Flash Lite, FastMCP, Claude Desktop.
- **Python Stack:** Pandas, Plotly, Gradio.
- **Last Updated:** November 2025
"""


def _safe_float(value, default=0.0) -> float:
    try:
        if value is None:
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


async def analyze_hydro(lat: float, lon: float, date_str: str):
    """
    Returns: mean_temp, precip, humidity, df_plot (Date/ETo/Precipitation), eto_json, md_output.
    """
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        start_date_str = (target_date - timedelta(days=6)).strftime("%Y-%m-%d")
        # Try fetching range first (single call)
        try:
            range_results = await fetch_climate_range(lat, lon, start_date_str, date_str)
        except Exception:
            range_results = []

        # Derive day-of record
        day_climate = None
        if range_results:
            day_climate = next((c for c in range_results if c.date == date_str), range_results[-1])
        else:
            # Fallback: single-day fetch
            try:
                day_climate = await fetch_climate_data(lat, lon, date_str)
            except Exception:
                day_climate = None

        # Primary KPIs
        mean_temp = _safe_float(getattr(day_climate, "tmean", None))
        precip = _safe_float(getattr(day_climate, "precipitation", None))
        humidity = _safe_float(getattr(day_climate, "humidity", None))

        # ETo + AI insight
        eto_result = calculate_hargreaves_eto(day_climate) if day_climate else None

        # Chart rows from range results (or empty)
        rows: list[dict[str, float | str]] = []
        for res in range_results:
            eto_val = 0.0
            try:
                eto_val = _safe_float(calculate_hargreaves_eto(res).eto)
            except Exception:
                eto_val = 0.0
            rows.append(
                {
                    "Date": res.date,
                    "ETo": eto_val,
                    "Precipitation": _safe_float(getattr(res, "precipitation", 0.0)),
                }
            )

        df_plot = pd.DataFrame(rows).sort_values("Date") if rows else pd.DataFrame({"Date": [], "ETo": [], "Precipitation": []})

        eto_json = eto_result.model_dump_json() if eto_result else None
        placeholder_md = (
            "## 🌿 Agronomist Insight\n\n"
            "**Summary:** Calculating insight with Gemini...\n\n"
            "**Advice:** Please wait while AI completes analysis.\n\n"
            "**Risk Level:** ⏳\n\n"
            "**ETo Value:** -- mm/day"
        )

        return mean_temp, precip, humidity, df_plot, eto_json, placeholder_md

    except Exception as e:  # noqa: BLE001
        empty_df = pd.DataFrame(columns=["Date", "ETo", "Precipitation"])
        return 0.0, 0.0, 0.0, empty_df, None, f"Error: {str(e)}"


def render_kpis(mean_temp: float, precip: float, humidity: float):
    def card(label: str, value: float, unit: str, icon: str, extra_class: str = "") -> str:
        if value is None:
            display = "--"
        else:
            display = f"{value:.1f}{unit}"
        return f"""
        <div class="kpi-card {extra_class}">
            <div class="kpi-icon">{icon}</div>
            <div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{display}</div>
            </div>
        </div>
        """

    temp_card = card("Mean Temp", mean_temp, "°C", "🌡️", "kpi-temp")
    precip_card = card("Precipitation", precip, " mm", "🌧️", "kpi-precip")
    humidity_card = card("Avg. Humidity", humidity, "%", "💧", "kpi-humidity")
    return temp_card, precip_card, humidity_card


def render_chart(df_plot: pd.DataFrame | None):
    if df_plot is None or getattr(df_plot, "empty", True):
        df_plot = pd.DataFrame({"Date": [], "ETo": [], "Precipitation": []})

    df_plot = df_plot.copy()
    df_plot["Date"] = pd.to_datetime(df_plot["Date"]).dt.strftime("%Y-%m-%d")

    bar_fig = px.bar(
        df_plot,
        x="Date",
        y="Precipitation",
        labels={"Precipitation": "Precipitation (mm)", "Date": "Date"},
        title="Water Balance (7-Day Trend)",
        opacity=0.8,
        color_discrete_sequence=["#4f7df3"],
    )
    # Rename bar trace for clarity
    if bar_fig.data:
        bar_fig.data[0].name = "Precipitation (Supply)"
    line_fig = px.line(
        df_plot,
        x="Date",
        y="ETo",
        markers=True,
        color_discrete_sequence=["#ff5c5c"],
    )
    for trace in line_fig.data:
        trace.yaxis = "y2"
        trace.name = "ETo Demand (Loss)"
        bar_fig.add_trace(trace)

    bar_fig.update_traces(
        hovertemplate="Date: %{x}<br>Precipitation: %{y:.2f} mm<extra></extra>",
        selector=dict(type="bar"),
    )
    bar_fig.update_traces(
        hovertemplate="Date: %{x}<br>ETo: %{y:.2f} mm/day<extra></extra>",
        selector=dict(mode="lines+markers"),
    )
    bar_fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        bargap=0.25,
        margin=dict(t=60, b=40, l=40, r=50),
        xaxis=dict(title="Date", showgrid=True, gridcolor="#374151", tickangle=-15),
        yaxis=dict(title="Precipitation (mm)", rangemode="tozero", zeroline=True, zerolinecolor="#4f7df3", gridcolor="#374151"),
        yaxis2=dict(
            title="ETo (mm/day)",
            overlaying="y",
            side="right",
            showgrid=False,
            rangemode="tozero",
        ),
    )
    return bar_fig


def show_loading():
    return gr.update(value="⏳ Loading Gemini insight...", visible=True)


def hide_loading():
    return gr.update(value="", visible=False)


def _select_site(choice: str, current_lat: float, current_lon: float):
    coords = SITES.get(choice)
    if coords is None:
        return current_lat, current_lon
    return coords


async def generate_insight_only(lat: float, lon: float, date_str: str, eto_json: str | None):
    """Generate insight separately to avoid blocking chart rendering."""
    try:
        eto_result = None
        if eto_json:
            try:
                eto_result = EToResult.model_validate_json(eto_json)
            except Exception:
                eto_result = None

        if eto_result is None:
            # Fallback: recompute quickly
            climate = await fetch_climate_data(lat, lon, date_str)
            eto_result = calculate_hargreaves_eto(climate)

        insight = await generate_agronomist_insight(eto_result)
        risk_badge = {
            "High": "<span style='color:#ef4444;font-weight:800'>🔴 HIGH</span>",
            "Medium": "<span style='color:#f59e0b;font-weight:800'>🟡 MEDIUM</span>",
            "Low": "<span style='color:#22c55e;font-weight:800'>🟢 LOW</span>",
        }.get(getattr(insight, "risk_level", None), getattr(insight, "risk_level", "Unknown"))

        md_output = dedent(
            f"""
            ## 🌿 Agronomist Insight

            **Summary:** {getattr(insight, "summary", "Data unavailable")}

            **Advice:** {getattr(insight, "advice", "No advice available")}

            **Risk Level:** {risk_badge}

            **ETo Value:** {getattr(insight, "eto_value", 0.0):.2f} mm/day
            """
        ).strip()

        return md_output

    except Exception as exc:  # noqa: BLE001
        return f"Error generating insight: {exc}"

# Initial skeleton cards must be defined before UI construction
_SKELETON_MEAN, _SKELETON_PRECIP, _SKELETON_HUMIDITY = render_kpis(None, None, None)

# Gradio UI
with gr.Blocks(title="nwa-hydro-mcp Command Center") as demo:
    gr.HTML(OCEAN_STYLE)
    gr.HTML(
        """
        <div class="hero">
            <div class="hero-title">💧 nwa-hydro-mcp: Hydrological Intelligence Command Center</div>
            <div class="hero-sub">Scientific Gold Edition • Powered by ERA5 Reanalysis + Hargreaves-Samani (1985)</div>
        </div>
        """
    )

    mean_state = gr.State()
    precip_state = gr.State()
    humidity_state = gr.State()
    df_state = gr.State()
    eto_state = gr.State()

    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            with gr.Group(elem_classes="panel"):
                site_select = gr.Radio(
                    label="📍 Select Monitoring Site",
                    choices=list(SITES.keys()),
                    value="Matagalpa (Coffee High - 1400m)",
                )
                date_input = gr.Textbox(
                    label="Date (YYYY-MM-DD)",
                    value=datetime.now().strftime("%Y-%m-%d"),
                    placeholder="YYYY-MM-DD",
                    info="Format: YYYY-MM-DD",
                )
                with gr.Accordion("Advanced Coordinates", open=False, elem_classes="custom-accordion"):
                    lat_input = gr.Number(label="Latitude", value=12.9256)
                    lon_input = gr.Number(label="Longitude", value=-85.9189)
                btn = gr.Button("Analyze Water Deficit", variant="primary", elem_classes="cta-btn")

        with gr.Column(scale=3):
            gr.Markdown("### Dashboard")
            with gr.Row(elem_classes="kpi-row"):
                mean_card = gr.Markdown(_SKELETON_MEAN)
                precip_card = gr.Markdown(_SKELETON_PRECIP)
                humidity_card = gr.Markdown(_SKELETON_HUMIDITY)
            loading_msg = gr.Markdown(visible=False)
            plot_output = gr.Plot(label="Water Balance Chart")
            output_md = gr.Markdown(label="Gemini Insight")

    # About + footer
    with gr.Row():
        with gr.Column():
            with gr.Accordion("ℹ️ About the Application, Methodology & Data Sources", open=False, elem_classes="custom-accordion"):
                gr.Markdown(ABOUT_MD)
            gr.HTML(
                """
                <div class="footer">
                    🚀 Powered by: <strong>Google Gemini 2.5 Flash Lite</strong> • <strong>FastMCP</strong> • <strong>Claude Desktop</strong> • <strong>Open-Meteo API</strong><br/>
                    <a href="https://github.com/datanicaragua/nwa-hydro-mcp" target="_blank">GitHub Repo</a> • <a href="https://open-meteo.com/" target="_blank">Open-Meteo</a> • <a href="https://pandas.pydata.org/" target="_blank">Pandas</a> • <a href="https://plotly.com/python/" target="_blank">Plotly</a> • <a href="https://gradio.app/" target="_blank">Gradio</a>
                </div>
                """
            )

    # Event wiring
    btn.click(
        show_loading,
        outputs=loading_msg,
        queue=False,
    ).then(
        analyze_hydro,
        inputs=[lat_input, lon_input, date_input],
        outputs=[mean_state, precip_state, humidity_state, df_state, eto_state, output_md],
    ).then(
        render_kpis,
        inputs=[mean_state, precip_state, humidity_state],
        outputs=[mean_card, precip_card, humidity_card],
    ).then(
        render_chart,
        inputs=df_state,
        outputs=plot_output,
    ).then(
        generate_insight_only,
        inputs=[lat_input, lon_input, date_input, eto_state],
        outputs=output_md,
    ).then(
        hide_loading,
        outputs=loading_msg,
        queue=False,
    )

    # Auto-load demo with defaults on page load
    demo.load(
        analyze_hydro,
        inputs=[lat_input, lon_input, date_input],
        outputs=[mean_state, precip_state, humidity_state, df_state, eto_state, output_md],
    ).then(
        render_kpis,
        inputs=[mean_state, precip_state, humidity_state],
        outputs=[mean_card, precip_card, humidity_card],
    ).then(
        render_chart,
        inputs=df_state,
        outputs=plot_output,
    ).then(
        generate_insight_only,
        inputs=[lat_input, lon_input, date_input, eto_state],
        outputs=output_md,
    )

    site_select.change(
        _select_site,
        inputs=[site_select, lat_input, lon_input],
        outputs=[lat_input, lon_input],
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True, theme=gr.themes.Soft())
