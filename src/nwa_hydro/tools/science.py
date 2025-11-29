import math
from datetime import datetime

from ..schemas import ClimateData, EToResult

GSC = 0.0820  # MJ m-2 min-1, FAO-56 solar constant


def _extraterrestrial_radiation(lat_rad: float, day_of_year: int) -> float:
    """
    Compute daily extraterrestrial radiation (Ra) in MJ m-2 day-1.
    Implements FAO-56 equations (Allen et al., 1998).
    """
    dr = 1.0 + 0.033 * math.cos((2 * math.pi / 365) * day_of_year)
    solar_declination = 0.409 * math.sin((2 * math.pi / 365) * day_of_year - 1.39)
    tan_term = -math.tan(lat_rad) * math.tan(solar_declination)
    # Clamp to avoid domain errors at extreme latitudes.
    tan_term = min(1.0, max(-1.0, tan_term))
    sunset_hour_angle = math.acos(tan_term)
    ra = (
        (24 * 60) / math.pi
    ) * GSC * dr * (
        sunset_hour_angle * math.sin(lat_rad) * math.sin(solar_declination)
        + math.cos(lat_rad) * math.cos(solar_declination) * math.sin(sunset_hour_angle)
    )
    return ra


def calculate_hargreaves_eto(climate_data: ClimateData) -> EToResult:
    """
    Calculate reference evapotranspiration (ETo) using FAO-56 Hargreaves (native math).
    ETo = 0.0023 * (Tmean + 17.8) * sqrt(Tmax - Tmin) * Ra
    """
    if climate_data.tmax < climate_data.tmin:
        raise ValueError("tmax must be greater than or equal to tmin")

    dt = datetime.strptime(climate_data.date, "%Y-%m-%d")
    doy = dt.timetuple().tm_yday

    lat_rad = math.radians(climate_data.lat)
    ra = _extraterrestrial_radiation(lat_rad, doy)
    delta_temp = max(climate_data.tmax - climate_data.tmin, 0.0)
    eto = 0.0023 * (climate_data.tmean + 17.8) * math.sqrt(delta_temp) * ra

    return EToResult(
        date=climate_data.date,
        eto=float(eto),
        method="Hargreaves (Native)",
        input_data=climate_data,
    )
