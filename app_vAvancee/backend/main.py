from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routers import geo, meteo

# ─────────────────────────────────────────────────────────────────────────────
# Initialisation de l'application FastAPI
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "🌍 GIS Météo Maroc — API",
    description = """
API backend minimaliste pour le Dashboard GIS Météo Maroc.

## Modules disponibles

### 🗺️ Géospatial
- Liste des **régions**, **provinces**, **communes**
- **Centroïde** et bornes géographiques
- Export **GeoJSON**
- **Statistiques** (superficie, nombre de communes…)

### 🌦️ Météo
- **Prévisions 15 jours** (température, pluie, vent, code WMO)
- **Résumé statistique** (min/max/moyennes)
    """,
    version     = "1.0.0",
    contact     = {
        "name" : "GIS Programming 2025-2026",
        "email": "contact@gismaroc.ma"
    },
    license_info= {
        "name": "MIT"
    }
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS — autorise Streamlit à appeler l'API
# ─────────────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # En prod : ["https://ton-app.streamlit.app"]
    allow_credentials = True,
    allow_methods     = ["GET"],
    allow_headers     = ["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Inclusion des routers
# ─────────────────────────────────────────────────────────────────────────────
app.include_router(geo.router)
app.include_router(meteo.router)


# ─────────────────────────────────────────────────────────────────────────────
# Route racine — Health check
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="Health check")
def root():
    return JSONResponse({
        "status" : "✅ API opérationnelle",
        "version": "1.0.0",
        "docs"   : "/docs",
        "modules": ["/geo", "/meteo"]
    })


@app.get("/health", tags=["Health"], summary="Statut détaillé")
def health():
    return JSONResponse({
        "status"  : "ok",
        "services": {
            "geodata": "loaded",
            "meteo"  : "open-meteo proxy"
        }
    })