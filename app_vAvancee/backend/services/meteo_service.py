import requests
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Codes météo WMO → descriptions
# ─────────────────────────────────────────────────────────────────────────────
WMO_CODES = {
    0 : "Ciel dégagé ☀️",
    1 : "Principalement dégagé 🌤️",
    2 : "Partiellement nuageux ⛅",
    3 : "Couvert 🌥️",
    45: "Brouillard 🌫️",
    48: "Brouillard givrant 🌫️",
    51: "Bruine légère 🌦️",
    53: "Bruine modérée 🌦️",
    55: "Bruine dense 🌧️",
    61: "Pluie légère 🌧️",
    63: "Pluie modérée 🌧️",
    65: "Pluie forte 🌧️",
    71: "Neige légère ❄️",
    73: "Neige modérée ❄️",
    75: "Neige forte ❄️",
    80: "Averses légères 🌦️",
    81: "Averses modérées 🌦️",
    82: "Averses fortes ⛈️",
    95: "Orage ⛈️",
    96: "Orage avec grêle ⛈️",
    99: "Orage violent avec grêle ⛈️",
}


# ─────────────────────────────────────────────────────────────────────────────
# Service principal
# ─────────────────────────────────────────────────────────────────────────────
def service_get_meteo(
    latitude: float,
    longitude: float,
    forecast_days: int = 15
) -> dict:

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude"     : latitude,
        "longitude"    : longitude,
        "daily"        : [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max",
            "weathercode"
        ],
        "timezone"     : "auto",
        "forecast_days": forecast_days
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    raw = response.json()

    daily     = raw["daily"]
    dates     = daily["time"]
    t_max     = daily["temperature_2m_max"]
    t_min     = daily["temperature_2m_min"]
    precip    = daily["precipitation_sum"]
    vent      = daily["windspeed_10m_max"]
    codes     = daily["weathercode"]

    # ── Construction des prévisions journalières ──────────────────────────────
    previsions = []
    for i, date in enumerate(dates):
        previsions.append({
            "date"         : date,
            "t_max"        : t_max[i],
            "t_min"        : t_min[i],
            "precipitation": precip[i],
            "vent_max"     : vent[i],
            "code_meteo"   : codes[i],
            "description"  : WMO_CODES.get(codes[i], "Inconnu")
        })

    # ── Résumé statistique ────────────────────────────────────────────────────
    valid_tmax  = [v for v in t_max  if v is not None]
    valid_tmin  = [v for v in t_min  if v is not None]
    valid_prec  = [v for v in precip if v is not None]
    valid_vent  = [v for v in vent   if v is not None]

    idx_chaud   = t_max.index(max(valid_tmax))
    idx_pluie   = precip.index(max(valid_prec))

    resume = {
        "t_moy_max"        : round(sum(valid_tmax) / len(valid_tmax), 1),
        "t_max_absolue"    : max(valid_tmax),
        "t_min_absolue"    : min(valid_tmin),
        "pluie_totale"     : round(sum(valid_prec), 1),
        "vent_moy"         : round(sum(valid_vent) / len(valid_vent), 1),
        "jour_plus_chaud"  : dates[idx_chaud],
        "jour_plus_pluvieux": dates[idx_pluie],
    }

    return {
        "latitude"    : latitude,
        "longitude"   : longitude,
        "timezone"    : raw.get("timezone", "auto"),
        "forecast_days": forecast_days,
        "resume"      : resume,
        "previsions"  : previsions
    }