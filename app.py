from datetime import datetime, timedelta
from textwrap import dedent

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

import gradio as gr
import pandas as pd
import plotly.express as px
from geopy.exc import GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim

from src.nwa_hydro.tools.fusion import fetch_climate_data, fetch_climate_range
from src.nwa_hydro.tools.intelligence import generate_agronomist_insight
from src.nwa_hydro.tools.science import calculate_hargreaves_eto
from src.nwa_hydro.schemas import EToResult


DEFAULT_LAT = 12.9256
DEFAULT_LON = -85.9189
DEFAULT_LABEL = "Matagalpa (Coffee High - 1400m)"
SCENARIO_A_LABEL = "☕ Scenario A: High-Altitude Coffee (Matagalpa)"
SCENARIO_B_LABEL = "🌫️ Scenario B: Dry Corridor (El Crucero)"
SCENARIO_PRESETS = {
    SCENARIO_A_LABEL: {"lat": DEFAULT_LAT, "lon": DEFAULT_LON, "zoom": 10, "label": SCENARIO_A_LABEL},
    SCENARIO_B_LABEL: {"lat": 11.9903, "lon": -86.3087, "zoom": 10, "label": SCENARIO_B_LABEL},
}

# Nominatim requires a user_agent; keep timeout tight to avoid blocking UI
_GEOCODER = Nominatim(user_agent="nwa-hydro-hackathon", timeout=5)

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
  --risk-high: #ef4444;
  --risk-med: #f59e0b;
  --risk-low: #22c55e;
}
body {background: var(--ocean-bg); color: var(--ocean-text);}
.kpi-row {display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 10px;}
.kpi-card {background: linear-gradient(145deg, #111a2e, #0e182b); padding: 12px 14px; border-radius: 12px; display: flex; align-items: center; gap: 10px; box-shadow: 0 6px 20px rgba(0,0,0,0.35); min-height: 70px;}
.kpi-icon {font-size: 20px; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.35));}
.kpi-label {text-transform: uppercase; letter-spacing: 0.6px; font-size: 10px; color: var(--ocean-muted); margin-bottom: 2px;}
.kpi-value {font-size: 22px; font-weight: 800; color: var(--ocean-text); line-height: 1.1;}
.kpi-temp .kpi-value {color: var(--kpi-temp);}
.kpi-precip .kpi-value {color: var(--kpi-precip);}
.kpi-humidity .kpi-value {color: var(--kpi-humidity);}
.panel {background: var(--ocean-panel); border-radius: 14px; padding: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.25);}
.header-title {font-size: 24px; font-weight: 800; margin: 0;}
.subtle {color: var(--ocean-muted);}
.cta-btn button {width: 100%; background: linear-gradient(135deg, #4f7df3, #6a5cf5); color: white; font-weight: 800; letter-spacing: 0.3px; border: 1px solid rgba(255,255,255,0.12); box-shadow: 0 10px 24px rgba(79,125,243,0.35);}
.cta-btn button:hover {transform: translateY(-1px); box-shadow: 0 14px 30px rgba(79,125,243,0.45);}
.cta-btn button:active {transform: translateY(0);}
.hero {background: linear-gradient(135deg, #0c284f, #122c63 55%, #172a4d); border-radius: 14px; padding: 12px 20px; color: #e9f1ff; box-shadow: 0 8px 24px rgba(0,0,0,0.35); margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;}
.hero-content { display: flex; flex-direction: column; }
.hero-title {font-size: 22px; font-weight: 800; margin: 0; letter-spacing: -0.5px;}
.hero-sub {color: var(--ocean-accent-soft); font-weight: 500; margin-top: 2px; font-size: 13px; opacity: 0.9;}
.footer {text-align: center; color: var(--ocean-muted); margin-top: 12px; font-size: 12px;}
.footer a { color: #e9f1ff !important; text-decoration: underline; font-weight: 600; transition: color 0.2s ease-in-out; }
.footer a:visited,
.footer a:active { color: #e9f1ff !important; }
.footer a:hover { color: #9bc2ff !important; text-decoration: underline; }

.custom-accordion .icon { color: #9bc2ff !important; }
.custom-accordion { background: #18233a !important; border-radius: 8px; border: 1px solid #4f7df3; margin: 0 auto; width: fit-content; }
.custom-accordion button { color: #e9f1ff !important; font-weight: 700; }

/* Insight Cards Grid */
.insight-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 12px; margin-top: 8px; }
.insight-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px; }
.insight-title { font-size: 11px; text-transform: uppercase; color: var(--ocean-muted); font-weight: 700; margin-bottom: 6px; letter-spacing: 0.5px; }
.insight-body { font-size: 14px; line-height: 1.4; color: #e9f1ff; }
.risk-badge { display: inline-block; padding: 4px 8px; border-radius: 6px; font-weight: 800; font-size: 12px; color: #0b1221; }
.risk-high { background: var(--risk-high); box-shadow: 0 0 10px rgba(239,68,68,0.4); }
.risk-med { background: var(--risk-med); box-shadow: 0 0 10px rgba(245,158,11,0.4); }
.risk-low { background: var(--risk-low); box-shadow: 0 0 10px rgba(34,197,94,0.4); }
.eto-stat { font-size: 24px; font-weight: 800; color: var(--ocean-accent-soft); }
.eto-unit { font-size: 12px; color: var(--ocean-muted); font-weight: 400; }
</style>
"""

ABOUT_MD = """
### 📺 Video Tour & Tutorial
[▶️ **Click here to watch the 2-minute walkthrough**](https://www.youtube.com/watch?v=pqjqM5uAjC8)

### 📚 Documentation
For a deep dive into the architecture, MCP integration, and hackathon tracks, please visit the **[Project README](https://huggingface.co/spaces/datanicaragua/nwa-hydro-mcp/blob/main/README.md)**.

### 1. Application Purpose
The **NWA Hydro-Compute** engine bridges the gap between raw climate data and actionable agronomic advice. It empowers farmers and researchers to answer: *"What is the water stress risk for my crop?"*

### 2. Data Source
- **Primary Provider:** [Open-Meteo API](https://open-meteo.com/) (ERA5 Reanalysis).
- **Model:** **ERA5** by **ECMWF** (Global Climate Reanalysis).
- **Resolution:** ~11km grid (ERA5-Land).

### 3. Scientific Methodology
- **ETo (Evapotranspiration):** Calculated using the **Hargreaves-Samani (1985)** equation (FAO-56 standard for limited data).
- **Water Balance:** Compares **Supply** (Precipitation) vs. **Demand** (ETo) to identify deficit periods.

### 4. AI & Intelligence Layer
- **Reasoning:** **Google Gemini 2.5 Flash Lite** acts as an expert agronomist.
- **Protocol:** Built on **FastMCP** (Model Context Protocol) for standardized tool use.

### 5. Credits
- **Developer:** Gustavo Ernesto Martínez Cárdenas
- **Stack:** Python 3.10, Gradio 6, Plotly, Maplibre.
"""


def _safe_float(value, default=0.0) -> float:
    try:
        if value is None:
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def get_location_from_text(query: str) -> tuple[float, float, str] | None:
    """Geocode a text query; returns (lat, lon, label) or None if not found."""
    if not query or not query.strip():
        gr.Warning("Type a place to search (e.g., 'El Crucero').")
        return None
    bbox_bias = [(-88, 10), (-82, 15)]  # Soft bias toward Nicaragua/Central America
    try:
        location = _GEOCODER.geocode(
            query.strip(),
            exactly_one=True,
            addressdetails=False,
            viewbox=bbox_bias,
            bounded=False,
        )
    except (GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable) as exc:
        gr.Warning(f"Geocoding unavailable right now ({exc}). Try again shortly.")
        return None
    except Exception:
        gr.Warning("Could not fetch that location. Please try a nearby city or add the country name.")
        return None

    if (
        location is None
        or getattr(location, "latitude", None) is None
        or getattr(location, "longitude", None) is None
    ):
        gr.Warning("Location not found. Try a nearby city or add 'Country' to the search.")
        return None

    return (
        float(location.latitude),
        float(location.longitude),
        getattr(location, "address", query.strip()),
    )


def update_map(lat: float, lon: float, label: str | None = None, zoom: float | None = None):
    """Render a simple map with the selected point using open-street-map tiles (Maplibre)."""
    lat = _safe_float(lat, DEFAULT_LAT)
    lon = _safe_float(lon, DEFAULT_LON)
    if label is None:
        if abs(lat - DEFAULT_LAT) < 1e-6 and abs(lon - DEFAULT_LON) < 1e-6:
            title = DEFAULT_LABEL
        else:
            title = "Selected Location"
    else:
        title = label
    map_zoom = zoom if zoom is not None else 10
    df = pd.DataFrame([{"lat": lat, "lon": lon, "label": title}])
    fig = px.scatter_map(
        df,
        lat="lat",
        lon="lon",
        hover_name="label",
        zoom=map_zoom,
        height=350,
        map_style="open-street-map",
    )
    fig.update_traces(
        marker=dict(size=14, color="#4f7df3"),
        customdata=df[["lat", "lon"]],
        hovertemplate="<b>%{hovertext}</b><br>Lat: %{lat:.4f}<br>Lon: %{lon:.4f}<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        clickmode="event+select",
    )
    return fig


def handle_search_location(query: str, current_lat: float, current_lon: float, current_label: str | None):
    """Geocode user text, refresh the map, and update the stored label."""
    result = get_location_from_text(query)
    fallback_label = current_label or "Selected Location"
    if result is None:
        return current_lat, current_lon, update_map(current_lat, current_lon, fallback_label, zoom=9), fallback_label
    lat, lon, label = result
    return lat, lon, update_map(lat, lon, label, zoom=9), label


def _extract_coords_from_event(evt: gr.SelectData) -> tuple[float, float] | None:
    if evt is None:
        return None
    value = getattr(evt, "value", None)
    if isinstance(value, dict):
        points = value.get("points")
        if isinstance(points, list) and points:
            point = points[0]
            lat = point.get("lat") or point.get("y")
            lon = point.get("lon") or point.get("x")
            custom = point.get("customdata")
            if isinstance(custom, (list, tuple)) and len(custom) >= 2:
                lat = custom[0] if custom[0] is not None else lat
                lon = custom[1] if custom[1] is not None else lon
            if lat is not None and lon is not None:
                return _safe_float(lat), _safe_float(lon)
        lat = value.get("lat")
        lon = value.get("lon")
        if lat is not None and lon is not None:
            return _safe_float(lat), _safe_float(lon)
    return None


def handle_map_click(evt: gr.SelectData, current_lat: float, current_lon: float, current_label: str | None):
    """Extract lat/lon from map click, refresh map, and update label state."""
    coords = _extract_coords_from_event(evt)
    fallback_label = current_label or "Selected Location"
    if coords is None:
        return current_lat, current_lon, update_map(current_lat, current_lon, fallback_label, zoom=9), fallback_label
    lat, lon = coords
    label = f"Pinned: {lat:.3f}, {lon:.3f}"
    return lat, lon, update_map(lat, lon, label, zoom=10), label


def apply_scenario(preset_label: str, current_lat: float, current_lon: float):
    """Apply a quick scenario preset; fallback to current coords."""
    preset = SCENARIO_PRESETS.get(preset_label)
    if not preset:
        return current_lat, current_lon, update_map(current_lat, current_lon, "Selected Location", zoom=9)
    lat = preset.get("lat", current_lat)
    lon = preset.get("lon", current_lon)
    label = preset.get("label", preset_label)
    zoom = preset.get("zoom", 10)
    return lat, lon, update_map(lat, lon, label, zoom=zoom)


def set_preset_location(preset_key: str):
    """Helper for UI buttons that maps short keys to scenario presets."""
    key = (preset_key or "").strip().lower()
    label_lookup = {
        "matagalpa": SCENARIO_A_LABEL,
        "crucero": SCENARIO_B_LABEL,
    }
    preset_label = label_lookup.get(key, SCENARIO_A_LABEL)
    preset = SCENARIO_PRESETS.get(preset_label, SCENARIO_PRESETS[SCENARIO_A_LABEL])
    lat = preset.get("lat", DEFAULT_LAT)
    lon = preset.get("lon", DEFAULT_LON)
    zoom = preset.get("zoom", 10)
    label = preset.get("label", preset_label)
    return lat, lon, update_map(lat, lon, label, zoom=zoom), label


async def analyze_hydro(lat: float, lon: float, date_str: str, location_label: str | None = None):
    """
    Returns: dashboard_md, mean_temp, precip, humidity, df_plot, eto_json, md_output.
    """
    location_title = location_label or DEFAULT_LABEL
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

        dashboard_md = f"### 📍 ANALYSIS TARGET: {location_title}"
        return dashboard_md, mean_temp, precip, humidity, df_plot, eto_json, placeholder_md

    except Exception as e:  # noqa: BLE001
        empty_df = pd.DataFrame(columns=["Date", "ETo", "Precipitation"])
        dashboard_md = f"### 📍 ANALYSIS TARGET: {location_title}"
        return dashboard_md, 0.0, 0.0, 0.0, empty_df, None, f"Error: {str(e)}"


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
        height=320,
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
        
        risk_raw = getattr(insight, "risk_level", "Unknown")
        risk_class = "risk-low"
        if "High" in risk_raw: risk_class = "risk-high"
        elif "Medium" in risk_raw: risk_class = "risk-med"
        
        summary = getattr(insight, "summary", "Data unavailable")
        advice = getattr(insight, "advice", "No advice available")
        eto_val = f"{getattr(insight, 'eto_value', 0.0):.2f}"

        html_output = f"""
        <div class="insight-grid">
            <div style="display:flex; flex-direction:column; gap:10px;">
                <div class="insight-card">
                    <div class="insight-title">📋 Executive Summary</div>
                    <div class="insight-body">{summary}</div>
                </div>
                <div class="insight-card">
                    <div class="insight-title">💡 Agronomist Advice</div>
                    <div class="insight-body">{advice}</div>
                </div>
            </div>
            <div style="display:flex; flex-direction:column; gap:10px;">
                <div class="insight-card" style="text-align:center;">
                    <div class="insight-title">⚠️ Irrigation Risk</div>
                    <div style="margin-top:6px;"><span class="risk-badge {risk_class}">{risk_raw.upper()}</span></div>
                </div>
                <div class="insight-card" style="text-align:center; flex-grow:1; display:flex; flex-direction:column; justify-content:center;">
                    <div class="insight-title">💧 ETo Demand</div>
                    <div class="eto-stat">{eto_val}<span class="eto-unit"> mm/day</span></div>
                </div>
            </div>
        </div>
        """
        return html_output

    except Exception as exc:  # noqa: BLE001
        return f"<div class='insight-card'>Error generating insight: {exc}</div>"

# Initial skeleton cards must be defined before UI construction
_SKELETON_MEAN, _SKELETON_PRECIP, _SKELETON_HUMIDITY = render_kpis(None, None, None)

# Gradio UI
with gr.Blocks(title="NWA Hydro-Compute") as demo:
    gr.HTML(OCEAN_STYLE)
    gr.HTML(
        """
        <div class="hero">
            <div class="hero-content">
                <div class="hero-title">💧 NWA Hydro-Compute: Precision Water Risk Engine</div>
                <div class="hero-sub">Scientific Hydrology for Central America • Powered by ERA5 Reanalysis & Generative AI</div>
            </div>
        </div>
        """
    )

    mean_state = gr.State()
    precip_state = gr.State()
    humidity_state = gr.State()
    df_state = gr.State()
    eto_state = gr.State()
    
    # State to hold the current location name
    current_location_state = gr.State(value=DEFAULT_LABEL)

    with gr.Row(equal_height=True):
        with gr.Column(scale=2):
            with gr.Group(elem_classes="panel"):
                with gr.Row():
                    search_box = gr.Textbox(
                        label="Search Location",
                        placeholder="e.g., El Crucero or Matagalpa",
                        scale=4,
                    )
                    search_btn = gr.Button("🔍", scale=1, min_width=60)
                gr.Markdown("*Search local (e.g., 'Jinotega') or global (e.g., 'Napa Valley') to test.*")
                with gr.Row():
                    scenario_a_btn = gr.Button(SCENARIO_A_LABEL, variant="secondary")
                    scenario_b_btn = gr.Button(SCENARIO_B_LABEL, variant="secondary")
                map_plot = gr.Plot(
                    label="📌 Selected Location",
                    value=update_map(DEFAULT_LAT, DEFAULT_LON, DEFAULT_LABEL, zoom=10),
                )
                with gr.Accordion("Advanced Coordinates", open=True, elem_classes="custom-accordion"):
                    lat_input = gr.Number(label="Latitude", value=DEFAULT_LAT)
                    lon_input = gr.Number(label="Longitude", value=DEFAULT_LON)
                date_input = gr.Textbox(
                    label="Date (YYYY-MM-DD)",
                    value=datetime.now().strftime("%Y-%m-%d"),
                    placeholder="YYYY-MM-DD",
                    info="Format: YYYY-MM-DD",
                )
                btn = gr.Button("Analyze Water Deficit", variant="primary", elem_classes="cta-btn")

        with gr.Column(scale=3):
            gr.Markdown("### Dashboard", elem_id="dashboard-header")
            
            # Dynamic Title Component
            dashboard_title = gr.Markdown(f"### 📍 ANALYSIS TARGET: {DEFAULT_LABEL}")

            with gr.Row(elem_classes="kpi-row"):
                mean_card = gr.Markdown(_SKELETON_MEAN)
                precip_card = gr.Markdown(_SKELETON_PRECIP)
                humidity_card = gr.Markdown(_SKELETON_HUMIDITY)
            loading_msg = gr.Markdown(visible=False)
            plot_output = gr.Plot(label="Water Balance Chart")
            
            gr.Markdown("### 🌿 Agronomist Insight")
            output_html = gr.HTML(
                """
                <div class="insight-grid">
                    <div class="insight-card" style="grid-column: span 2;">
                        <div class="insight-body" style="opacity:0.7; text-align:center; padding:20px;">
                            Run analysis to generate AI-powered insights...
                        </div>
                    </div>
                </div>
                """
            )

    # About + footer
    with gr.Row():
        with gr.Column(scale=1):
            pass
        with gr.Column(scale=10):
            with gr.Accordion("ℹ️ About this App: Methods & Data", open=False, elem_classes="custom-accordion"):
                gr.Markdown(ABOUT_MD)
            gr.HTML(
                """
                <div class="footer">
                    🚀 Powered by: <strong>Google Gemini 2.5 Flash Lite</strong> • <strong>FastMCP</strong> • <strong>Claude Desktop</strong> • <strong>Open-Meteo API</strong><br/>
                    <a href="https://github.com/datanicaragua/nwa-hydro-mcp" target="_blank">GitHub Repo</a> • <a href="https://open-meteo.com/" target="_blank">Open-Meteo</a> • <a href="https://pandas.pydata.org/" target="_blank">Pandas</a> • <a href="https://plotly.com/python/" target="_blank">Plotly</a> • <a href="https://gradio.app/" target="_blank">Gradio</a>
                </div>
                """
            )
        with gr.Column(scale=1):
            pass

    # Event wiring
    search_btn.click(
        handle_search_location,
        inputs=[search_box, lat_input, lon_input, current_location_state],
        outputs=[lat_input, lon_input, map_plot, current_location_state],
    )
    search_box.submit(
        handle_search_location,
        inputs=[search_box, lat_input, lon_input, current_location_state],
        outputs=[lat_input, lon_input, map_plot, current_location_state],
    )
    scenario_a_btn.click(
        lambda: set_preset_location("matagalpa"),
        outputs=[lat_input, lon_input, map_plot, current_location_state],
    )
    scenario_b_btn.click(
        lambda: set_preset_location("crucero"),
        outputs=[lat_input, lon_input, map_plot, current_location_state],
    )
    lat_input.change(
        update_map,
        inputs=[lat_input, lon_input],
        outputs=map_plot,
        show_progress=False,
    )
    lon_input.change(
        update_map,
        inputs=[lat_input, lon_input],
        outputs=map_plot,
        show_progress=False,
    )

    btn.click(
        show_loading,
        outputs=loading_msg,
        queue=False,
    ).then(
        analyze_hydro,
        inputs=[lat_input, lon_input, date_input, current_location_state],
        outputs=[dashboard_title, mean_state, precip_state, humidity_state, df_state, eto_state, output_html],
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
        outputs=output_html,
    ).then(
        hide_loading,
        outputs=loading_msg,
        queue=False,
    )

    # Auto-load demo with defaults on page load
    demo.load(
        update_map,
        inputs=[lat_input, lon_input],
        outputs=map_plot,
    ).then(
        analyze_hydro,
        inputs=[lat_input, lon_input, date_input, current_location_state],
        outputs=[dashboard_title, mean_state, precip_state, humidity_state, df_state, eto_state, output_html],
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
        outputs=output_html,
    )

if __name__ == "__main__":
    demo.launch(share=False, inbrowser=True)
