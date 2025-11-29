from pathlib import Path

import httpx
import pandas as pd

from ..schemas import ClimateData

LOCAL_DATA_PATH = Path("data/samples/local_station.csv")


async def fetch_climate_data(lat: float, lon: float, target_date: str) -> ClimateData:
    """Fetch climate data from Open-Meteo, fallback to local CSV if needed."""
    try:
        # 1. Try API
        async with httpx.AsyncClient() as client:
            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": target_date,
                "end_date": target_date,
                "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean"],
                "timezone": "auto"
            }
            response = await client.get(url, params=params, timeout=5.0)
            response.raise_for_status()
            data = response.json()

            daily = data.get("daily", {})
            return ClimateData(
                date=target_date,
                tmin=daily["temperature_2m_min"][0],
                tmax=daily["temperature_2m_max"][0],
                tmean=daily["temperature_2m_mean"][0],
                lat=lat,
                source="API",
            )

    except Exception as error:
        # 2. Fallback to CSV
        print(f"API failed ({error}), switching to local fallback.")
        return _load_from_csv(lat, target_date)


def _load_from_csv(lat: float, target_date: str) -> ClimateData:
    """Load climate data from the local CSV fallback."""
    if not LOCAL_DATA_PATH.exists():
        raise FileNotFoundError(f"Local fallback file not found at {LOCAL_DATA_PATH}")

    df = pd.read_csv(LOCAL_DATA_PATH)
    df["date"] = df["date"].astype(str)
    record = df[df["date"] == target_date]

    if record.empty:
        raise ValueError(f"No data found for {target_date} in local CSV.")

    row = record.iloc[0]
    return ClimateData(
        date=target_date,
        tmin=row["tmin"],
        tmax=row["tmax"],
        tmean=row["tmean"],
        lat=lat,
        source="CSV",
    )
