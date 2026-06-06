from pydantic import BaseModel
from typing import List, Optional


class MeteoRequest(BaseModel):
    latitude: float
    longitude: float
    forecast_days: Optional[int] = 15


class JourMeteo(BaseModel):
    date: str
    t_max: Optional[float]
    t_min: Optional[float]
    precipitation: Optional[float]
    vent_max: Optional[float]
    code_meteo: Optional[int]
    description: Optional[str]


class MeteoResponse(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    forecast_days: int
    resume: "ResumeMeteo"
    previsions: List[JourMeteo]


class ResumeMeteo(BaseModel):
    t_moy_max: float
    t_max_absolue: float
    t_min_absolue: float
    pluie_totale: float
    vent_moy: float
    jour_plus_chaud: str
    jour_plus_pluvieux: str


# Résolution forward reference
MeteoResponse.model_rebuild()