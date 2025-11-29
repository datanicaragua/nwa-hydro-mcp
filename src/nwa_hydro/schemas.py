
from pydantic import BaseModel, Field


class ClimateData(BaseModel):
    """
    Standardized climate data model for hydrological calculations.
    Source can be 'API' (Open-Meteo) or 'CSV' (Local Fallback).
    """
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    tmin: float = Field(..., description="Minimum temperature in Celsius")
    tmax: float = Field(..., description="Maximum temperature in Celsius")
    tmean: float = Field(..., description="Mean temperature in Celsius")
    lat: float = Field(..., description="Latitude of the location")
    source: str = Field(..., description="Source of the data: 'API' or 'CSV'")
    precipitation: float = Field(0.0, description="Daily precipitation sum in mm")
    humidity: float = Field(0.0, description="Daily mean relative humidity (0-100)")

class EToResult(BaseModel):
    """
    Result of the Hargreaves ETo calculation.
    """
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    eto: float = Field(..., description="Reference Evapotranspiration (ETo) in mm/day")
    method: str = Field("Hargreaves", description="Calculation method used")
    input_data: ClimateData = Field(..., description="The climate data used for calculation")

class AgronomistInsight(BaseModel):
    """
    AI-generated insight for the farmer based on ETo data.
    """
    summary: str = Field(..., description="Concise summary of the water situation")
    advice: str = Field(..., description="Actionable advice for the farmer")
    risk_level: str = Field(..., description="Risk level: 'Low', 'Medium', 'High'")
    eto_value: float = Field(..., description="The ETo value analyzed")
