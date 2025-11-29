import json
import logging
import time
from datetime import datetime

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()  # Load environment variables from .env file

from nwa_hydro.schemas import AgronomistInsight, ClimateData, EToResult
from nwa_hydro.tools.fusion import fetch_climate_data
from nwa_hydro.tools.intelligence import generate_agronomist_insight
from nwa_hydro.tools.science import calculate_hargreaves_eto

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP Server
# Define the MCP Server with rich metadata
# This helps Claude Desktop understand the server's purpose and requirements.
mcp = FastMCP(
    "NWA Hydro Intelligence",
    dependencies=[
        "fastmcp",
        "pydantic",
        "google-generativeai",
        "httpx",
        "pandas",
        "python-dotenv"
    ],
    description="Hydrological intelligence system for Nicaraguan agriculture. Provides real-time weather, ETo calculations, and AI-driven agronomic advice."
)
_START_TIME = time.monotonic()


def _validate_inputs(lat: float, lon: float, date_str: str) -> None:
    if not (-90.0 <= lat <= 90.0):
        raise ValueError("Latitude must be between -90 and 90 degrees")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError("Longitude must be between -180 and 180 degrees")
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Date must be in YYYY-MM-DD format") from exc


def _error_payload(message: str, detail: str | None = None) -> str:
    """Return a user-safe JSON error string."""
    payload = {"error": message}
    if detail:
        payload["detail"] = detail
    return json.dumps(payload)


# --- PURE FUNCTIONS (Testable) ---

async def get_climate_data(lat: float, lon: float, date: str) -> str:
    """
    Fetch climate data for a given location and date.
    Use this tool first to get the raw environmental data.
    Returns a JSON string of the ClimateData.
    """
    _validate_inputs(lat, lon, date)
    data = await fetch_climate_data(lat, lon, date)
    logger.info("Fetched climate data from %s for %s", data.source, date)
    return data.model_dump_json()


def calculate_eto(climate_data_json: str) -> str:
    """
    Calculate ETo from ClimateData JSON.
    Requires meteorological data as input.
    Returns a JSON string of the EToResult.
    """
    data = ClimateData.model_validate_json(climate_data_json)
    result = calculate_hargreaves_eto(data)
    logger.info("Calculated ETo via %s for %s", result.method, data.date)
    return result.model_dump_json()


async def get_agronomist_advice(eto_result_json: str) -> str:
    """
    Generate agronomist advice from EToResult JSON.
    Use this tool to get the final actionable advice for the farmer.
    Returns a JSON string of the AgronomistInsight or a user-friendly error JSON.
    """
    try:
        eto_result = EToResult.model_validate_json(eto_result_json)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Invalid ETo payload: %s", exc)
        return _error_payload("Invalid ETo payload", str(exc))

    try:
        insight: AgronomistInsight = await generate_agronomist_insight(eto_result)
        logger.info("Generated agronomist insight for %s", eto_result.date)
        return insight.model_dump_json()
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to generate agronomist insight: %s", exc)
        return _error_payload("Failed to generate agronomist insight", str(exc))


async def get_server_health() -> dict[str, object]:
    """Return basic health information for readiness probes."""
    uptime_seconds = max(time.monotonic() - _START_TIME, 0.0)
    return {
        "status": "ok",
        "tools_ready": True,
        "uptime_seconds": uptime_seconds,
    }


# --- MCP REGISTRATION ---
# Manually invoke the decorator to register tools while keeping functions pure
mcp.tool()(get_climate_data)
mcp.tool()(calculate_eto)
mcp.tool()(get_agronomist_advice)
mcp.tool()(get_server_health)

# Run the FastMCP Server
if __name__ == "__main__":
    mcp.run()
