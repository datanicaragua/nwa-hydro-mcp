"""FastMCP server bootstrap for the NWA Hydro MCP project."""

from __future__ import annotations

import logging
import time
from typing import Any

from fastmcp import FastMCP
from pydantic import BaseModel, Field

LOGGER = logging.getLogger(__name__)
START_TIME = time.perf_counter()
APP_ID = "nwa-hydro-mcp"

app = FastMCP(
    "nwa-hydro-mcp")

class HealthPayload(BaseModel):
    """Structured response returned by the health tool."""

    status: str = Field(..., description="High-level readiness summary.")
    uptime_seconds: float = Field(..., ge=0, description="Process uptime in seconds.")
    tools_ready: bool = Field(..., description="Indicates whether required tools loaded.")


@app.tool(description="Return current server health diagnostics.")
async def get_server_health() -> dict[str, Any]:
    """Return a JSON health report for orchestrators.

    Returns:
        dict[str, Any]: JSON-serializable payload describing current server health.
    """

    uptime = time.perf_counter() - START_TIME
    payload = HealthPayload(status="ok", uptime_seconds=uptime, tools_ready=True)
    LOGGER.debug("Health probe resolved: %s", payload.model_dump())
    return payload.model_dump()


def main() -> None:
    """CLI entry point that runs the FastMCP application."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    LOGGER.info("Starting %s", APP_ID)
    app.run()


if __name__ == "__main__":
    main()
