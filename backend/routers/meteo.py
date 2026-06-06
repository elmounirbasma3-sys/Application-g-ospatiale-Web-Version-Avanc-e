from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.services.meteo_service import service_get_meteo

router = APIRouter(prefix="/meteo", tags=["Météo"])


# ── GET /meteo/previsions ─────────────────────────────────────────────────────
@router.get("/previsions", summary="Prévisions météo 15 jours")
def get_previsions(
    latitude      : float         = Query(..., description="Latitude  (ex: 31.7917)"),
    longitude     : float         = Query(..., description="Longitude (ex: -7.0926)"),
    forecast_days : Optional[int] = Query(15,  ge=1, le=16)
):
    """
    Retourne les prévisions météo quotidiennes sur 15 jours
    pour les coordonnées données via Open-Meteo API.

    Inclut : température max/min, précipitations,
    vitesse du vent, code météo WMO + description.
    """
    try:
        data = service_get_meteo(latitude, longitude, forecast_days)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur API météo : {e}")


# ── GET /meteo/resume ─────────────────────────────────────────────────────────
@router.get("/resume", summary="Résumé météo uniquement")
def get_resume(
    latitude  : float = Query(...),
    longitude : float = Query(...),
):
    """
    Retourne uniquement le résumé statistique météo
    (températures extrêmes, pluie totale, vent moyen).
    """
    try:
        data = service_get_meteo(latitude, longitude, forecast_days=15)
        return {
            "latitude" : latitude,
            "longitude": longitude,
            **data["resume"]
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur API météo : {e}")