import pytest

from nwa_hydro.schemas import AgronomistInsight, ClimateData
from nwa_hydro.server import (
    calculate_eto,
    get_agronomist_advice,
    get_climate_data,
    get_server_health,
)


@pytest.mark.asyncio
async def test_get_server_health():
    """Smoke test for the health check tool."""
    result = await get_server_health()

    assert result["status"] == "ok"
    assert result["tools_ready"] is True
    assert result["uptime_seconds"] >= 0


@pytest.mark.asyncio
async def test_tool_roundtrip_with_mocks(monkeypatch):
    """End-to-end tool pipeline should work when dependencies are satisfied."""
    dummy_climate = ClimateData(
        date="2023-01-01",
        tmin=18.5,
        tmax=28.2,
        tmean=23.4,
        lat=12.0,
        source="CSV",
    )

    async def mock_fetch(lat: float, lon: float, date: str) -> ClimateData:
        return dummy_climate

    async def mock_generate(result):
        return AgronomistInsight(
            summary="All good",
            advice="Irrigate lightly.",
            risk_level="Low",
            eto_value=result.eto,
        )

    monkeypatch.setattr("nwa_hydro.server.fetch_climate_data", mock_fetch)
    monkeypatch.setattr("nwa_hydro.server.generate_agronomist_insight", mock_generate)

    climate_json = await get_climate_data(12.0, -85.0, "2023-01-01")
    eto_json = calculate_eto(climate_json)
    advice_json = await get_agronomist_advice(eto_json)

    advice = AgronomistInsight.model_validate_json(advice_json)
    assert advice.summary == "All good"
    assert advice.risk_level == "Low"
