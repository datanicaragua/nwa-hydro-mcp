import pytest

from nwa_hydro.schemas import ClimateData
from nwa_hydro.tools.fusion import fetch_climate_data
from nwa_hydro.tools.intelligence import generate_agronomist_insight
from nwa_hydro.tools.science import calculate_hargreaves_eto


@pytest.mark.asyncio
async def test_fetch_climate_data_csv_fallback(httpx_mock):
    """When the API fails, fusion should return data from the local CSV fallback."""
    target_date = "2023-01-01"
    httpx_mock.add_response(status_code=500)

    result = await fetch_climate_data(12.0, -85.0, target_date)

    assert result.source == "CSV"
    assert result.date == target_date
    assert result.tmean == pytest.approx(23.4)


def test_calculate_hargreaves_eto_sanity():
    """Science layer should return a reasonable ETo value without crashing."""
    climate = ClimateData(
        date="2023-01-01",
        tmin=18.5,
        tmax=28.2,
        tmean=23.4,
        lat=12.0,
        source="CSV",
    )

    result = calculate_hargreaves_eto(climate)

    assert result.method == "Hargreaves (Native)"
    # FAO-56 Hargreaves with these inputs should be ~8-9 mm/day.
    assert result.eto == pytest.approx(8.9, rel=0.15)


@pytest.mark.asyncio
async def test_generate_agronomist_insight_missing_key(monkeypatch):
    """Gemini tool should respond gracefully when API key is absent."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    climate = ClimateData(
        date="2023-01-01",
        tmin=18.5,
        tmax=28.2,
        tmean=23.4,
        lat=12.0,
        source="CSV",
    )
    eto_result = calculate_hargreaves_eto(climate)

    insight = await generate_agronomist_insight(eto_result)

    assert insight.summary.lower().startswith("api key missing")
    assert insight.risk_level == "Unknown"
    assert insight.eto_value == pytest.approx(eto_result.eto)
