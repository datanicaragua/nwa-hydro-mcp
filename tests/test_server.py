import pytest
from nwa_hydro.server import get_server_health

@pytest.mark.asyncio
async def test_get_server_health():
    """Smoke test for the health check tool."""
    result = await get_server_health()
    
    assert result["status"] == "ok"
    assert result["tools_ready"] is True
    assert result["uptime_seconds"] >= 0
