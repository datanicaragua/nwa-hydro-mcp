import asyncio
from datetime import datetime, timedelta
from textwrap import dedent

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

import gradio as gr
import pandas as pd
import plotly.express as px

from src.nwa_hydro.tools.fusion import fetch_climate_data
from src.nwa_hydro.tools.intelligence import generate_agronomist_insight
from src.nwa_hydro.tools.science import calculate_hargreaves_eto


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
.footer a {color: var(--ocean-accent-soft); text-decoration: none;}
.footer a:hover {text-decoration: underline;}
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
    Returns: mean_temp, precip, humidity, df_plot (Date/ETo/Precipitation), md_output.
    """
    try:
        # Day-of interest
        climate = await fetch_climate_data(lat, lon, date_str)

        # Primary KPIs
        mean_temp = _safe_float(getattr(climate, "tmean", None))
        precip = _safe_float(getattr(climate, "precipitation", None))
        humidity = _safe_float(getattr(climate, "humidity", None))

        # ETo + AI insight
        eto_result = calculate_hargreaves_eto(climate)
        insight = await generate_agronomist_insight(eto_result)

        # 7-day window (parallel fetch)
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        date_strings = [
            (target_date - timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(6, -1, -1)
        ]
        fetch_tasks = [fetch_climate_data(lat, lon, d) for d in date_strings]
        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        rows: list[dict[str, float | str]] = []
        for idx, result in enumerate(results):
            day = date_strings[idx]
            if isinstance(result, Exception):
                rows.append({"Date": day, "ETo": 0.0, "Precipitation": 0.0})
                continue
            eto_value = 0.0
            try:
                eto_value = _safe_float(calculate_hargreaves_eto(result).eto)
            except Exception:
                eto_value = 0.0
            day_precip = _safe_float(getattr(result, "precipitation", None))
            rows.append({"Date": day, "ETo": eto_value, "Precipitation": day_precip})

        df_plot = pd.DataFrame(rows)

        risk_badge = {
            "High": "<span style='color:#ef4444;font-weight:800'>🔴 HIGH</span>",
            "Medium": "<span style='color:#f59e0b;font-weight:800'>🟡 MEDIUM</span>",
            "Low": "<span style='color:#22c55e;font-weight:800'>🟢 LOW</span>",
        }.get(insight.risk_level, insight.risk_level)

        md_output = dedent(
            f"""
            ## 🌿 Agronomist Insight

            **Summary:** {insight.summary}

            **Advice:** {insight.advice}

            **Risk Level:** {risk_badge}

            **ETo Value:** {insight.eto_value:.2f} mm/day
            """
        ).strip()

        return mean_temp, precip, humidity, df_plot, md_output

    except Exception as e:  # noqa: BLE001
        empty_df = pd.DataFrame(columns=["Date", "ETo", "Precipitation"])
        return 0.0, 0.0, 0.0, empty_df, f"Error: {str(e)}"


def render_kpis(mean_temp: float, precip: float, humidity: float):
    def card(label: str, value: float, unit: str, icon: str, extra_class: str = "") -> str:
        return f"""
        <div class="kpi-card {extra_class}">
            <div class="kpi-icon">{icon}</div>
            <div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value:.1f}{unit}</div>
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
                with gr.Accordion("Advanced Coordinates", open=False):
                    lat_input = gr.Number(label="Latitude", value=12.9256)
                    lon_input = gr.Number(label="Longitude", value=-85.9189)
                btn = gr.Button("Analyze Water Deficit", variant="primary", elem_classes="cta-btn")

        with gr.Column(scale=3):
            gr.Markdown("### Dashboard")
            with gr.Row(elem_classes="kpi-row"):
                mean_card = gr.Markdown(elem_classes="kpi-card kpi-temp")
                precip_card = gr.Markdown(elem_classes="kpi-card kpi-precip")
                humidity_card = gr.Markdown(elem_classes="kpi-card kpi-humidity")
            loading_msg = gr.Markdown(visible=False)
            plot_output = gr.Plot(label="Water Balance Chart")
            output_md = gr.Markdown(label="Gemini Insight")

    # About + footer
    with gr.Row():
        with gr.Column():
            with gr.Accordion("ℹ️ About the Application, Methodology & Data Sources", open=False):
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
        outputs=[mean_state, precip_state, humidity_state, df_state, output_md],
    ).then(
        render_kpis,
        inputs=[mean_state, precip_state, humidity_state],
        outputs=[mean_card, precip_card, humidity_card],
    ).then(
        render_chart,
        inputs=df_state,
        outputs=plot_output,
    ).then(
        hide_loading,
        outputs=loading_msg,
        queue=False,
    )

    site_select.change(
        _select_site,
        inputs=[site_select, lat_input, lon_input],
        outputs=[lat_input, lon_input],
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True, theme=gr.themes.Soft())
