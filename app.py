import asyncio
from datetime import datetime, timedelta
from textwrap import dedent

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

import gradio as gr
import pandas as pd

from src.nwa_hydro.tools.fusion import fetch_climate_data
from src.nwa_hydro.tools.intelligence import generate_agronomist_insight
from src.nwa_hydro.tools.science import calculate_hargreaves_eto


async def analyze_hydro(lat, lon, date_str):
    try:
        # 1. Fetch Data for the specific date
        climate = await fetch_climate_data(lat, lon, date_str)

        # 2. Calculate ETo
        eto_result = calculate_hargreaves_eto(climate)

        # 3. Get Insight
        insight = await generate_agronomist_insight(eto_result)

        # 4. Generate Graph Data (Last 7 days) - PARALLEL FETCHING
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        date_strings = [
            (target_date - timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(6, -1, -1)
        ]

        # Fetch all 7 days in parallel for performance (~7x faster)
        # fetch_tasks = [fetch_climate_data(lat, lon, d) for d in date_strings]
        # results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        # Fetch sequencially to respect API rate limits
        results = []
        for d in date_strings:
            try:
                res = await fetch_climate_data(lat, lon, d)
                results.append(res)
                await asyncio.sleep(0.25) # <--- Pausa de 0.25 segs para no saturar
            except Exception as e:
                results.append(e)

        # Process results
        dates = []
        etos = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
            try:
                r = calculate_hargreaves_eto(result)
                dates.append(date_strings[i])
                etos.append(r.eto)
            except Exception:
                continue

        # Use Pandas DataFrame for robust Gradio plotting
        df = pd.DataFrame({"Date": dates, "ETo (mm/day)": etos})

        # Format output
        md_output = dedent(
            f"""
            ## 🌿 Agronomist Insight

            **Summary:** {insight.summary}

            **Advice:** {insight.advice}

            **Risk Level:** {insight.risk_level}

            **ETo Value:** {insight.eto_value:.2f} mm/day
            """
        ).strip()

        return md_output, df

    except Exception as e:
        return f"Error: {str(e)}", pd.DataFrame()

# Gradio UI
with gr.Blocks(title="nwa-hydro-mcp") as demo:
    gr.Markdown("# 💧 nwa-hydro-mcp: Hydrological Intelligence")

    with gr.Row():
        with gr.Column():
            lat_input = gr.Number(
                label="Latitude",
                value=12.8654,
            )  # Default: Matagalpa
            lon_input = gr.Number(
                label="Longitude",
                value=-85.2072,
            )
            date_input = gr.Textbox(
                label="Date (YYYY-MM-DD)",
                value=datetime.now().strftime("%Y-%m-%d"),
            )
            btn = gr.Button(
                "Analyze Water Deficit",
                variant="primary",
            )

        with gr.Column():
            output_md = gr.Markdown(label="Insight")
            output_plot = gr.LinePlot(
                x="Date",
                y="ETo (mm/day)",
                title="Reference Evapotranspiration Trend",
                tooltip=["Date", "ETo (mm/day)"]
            )

    btn.click(
        analyze_hydro,
        inputs=[lat_input, lon_input, date_input],
        outputs=[output_md, output_plot],
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True, theme=gr.themes.Soft())
