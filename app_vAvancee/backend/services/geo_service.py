import geopandas as gpd
from pathlib import Path
from functools import lru_cache
from typing import Optional
import json

# ─────────────────────────────────────────────────────────────────────────────
# Colonnes de référence
# ─────────────────────────────────────────────────────────────────────────────
REGION_COL        = "libelle_fr"
REGION_IN_COMMUNE = "FIRST_regi"
PROVINCE_COL      = "FIRST_prov"
COMMUNE_COL       = "FIRST_com_"

DATA_DIR = Path(__file__).parent.parent.parent / "data"


# ─────────────────────────────────────────────────────────────────────────────
# Chargement unique des données (mis en cache)
# ─────────────────────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def get_geodata():
    """
    Charge les 3 shapefiles une seule fois en mémoire.
    lru_cache garantit qu'on ne relit pas les fichiers à chaque requête.
    """
    regions   = gpd.read_file(DATA_DIR / "Regions_WGS84.shp")
    provinces = gpd.read_file(DATA_DIR / "Provinces_WGS84.shp")
    communes  = gpd.read_file(DATA_DIR / "communes_WGS84.shp")
    return regions, provinces, communes


# ─────────────────────────────────────────────────────────────────────────────
# Services
# ─────────────────────────────────────────────────────────────────────────────
def service_get_regions() -> list[str]:
    regions, _, _ = get_geodata()
    return sorted(regions[REGION_COL].dropna().unique().tolist())


def service_get_provinces(region: str) -> list[str]:
    _, _, communes = get_geodata()
    filtered = communes[communes[REGION_IN_COMMUNE] == region]
    if filtered.empty:
        return []
    return sorted(filtered[PROVINCE_COL].dropna().unique().tolist())


def service_get_communes(region: str, province: str) -> list[str]:
    _, _, communes = get_geodata()
    filtered = communes[
        (communes[REGION_IN_COMMUNE] == region) &
        (communes[PROVINCE_COL]      == province)
    ]
    if filtered.empty:
        return []
    return sorted(filtered[COMMUNE_COL].dropna().unique().tolist())


def service_get_centre(
    region: str,
    province: Optional[str] = None,
    commune: Optional[str]  = None
) -> dict:
    regions_gdf, _, communes_gdf = get_geodata()

    if commune and province:
        gdf = communes_gdf[
            (communes_gdf[REGION_IN_COMMUNE] == region) &
            (communes_gdf[PROVINCE_COL]      == province) &
            (communes_gdf[COMMUNE_COL]       == commune)
        ]
        niveau = "commune"
        nom    = commune

    elif province:
        gdf = communes_gdf[
            (communes_gdf[REGION_IN_COMMUNE] == region) &
            (communes_gdf[PROVINCE_COL]      == province)
        ].dissolve()
        niveau = "province"
        nom    = province

    else:
        gdf    = regions_gdf[regions_gdf[REGION_COL] == region]
        niveau = "region"
        nom    = region

    if gdf.empty:
        raise ValueError(f"Entité introuvable : {nom}")

    gdf    = gdf[gdf.geometry.notnull()]
    centre = gdf.geometry.union_all().centroid
    bounds = gdf.total_bounds.tolist()

    return {
        "latitude" : centre.y,
        "longitude": centre.x,
        "niveau"   : niveau,
        "nom"      : nom,
        "bounds"   : bounds
    }


def service_get_geojson(
    region: str,
    province: Optional[str] = None,
    commune: Optional[str]  = None
) -> dict:
    regions_gdf, _, communes_gdf = get_geodata()

    if commune and province:
        gdf = communes_gdf[
            (communes_gdf[REGION_IN_COMMUNE] == region) &
            (communes_gdf[PROVINCE_COL]      == province) &
            (communes_gdf[COMMUNE_COL]       == commune)
        ]
    elif province:
        gdf = communes_gdf[
            (communes_gdf[REGION_IN_COMMUNE] == region) &
            (communes_gdf[PROVINCE_COL]      == province)
        ].dissolve()
    else:
        gdf = regions_gdf[regions_gdf[REGION_COL] == region]

    if gdf.empty:
        raise ValueError("Entité introuvable")

    gdf = gdf[gdf.geometry.notnull()].to_crs(epsg=4326)
    return json.loads(gdf.to_json())


def service_get_stats(
    region: str,
    province: Optional[str] = None,
    commune: Optional[str]  = None
) -> dict:
    regions_gdf, _, communes_gdf = get_geodata()

    if commune and province:
        gdf    = communes_gdf[
            (communes_gdf[REGION_IN_COMMUNE] == region) &
            (communes_gdf[PROVINCE_COL]      == province) &
            (communes_gdf[COMMUNE_COL]       == commune)
        ]
        niveau = "commune"
        nom    = commune

    elif province:
        gdf    = communes_gdf[
            (communes_gdf[REGION_IN_COMMUNE] == region) &
            (communes_gdf[PROVINCE_COL]      == province)
        ]
        niveau = "province"
        nom    = province

    else:
        gdf    = regions_gdf[regions_gdf[REGION_COL] == region]
        niveau = "region"
        nom    = region

    if gdf.empty:
        raise ValueError("Entité introuvable")

    gdf     = gdf[gdf.geometry.notnull()]
    centre  = gdf.geometry.union_all().centroid
    bounds  = gdf.total_bounds.tolist()

    # Superficie en km²
    gdf_proj    = gdf.to_crs(epsg=26191)   # projection Maroc
    superficie  = gdf_proj.geometry.area.sum() / 1e6

    # Nombre de communes (uniquement si région ou province)
    nb_communes = None
    if niveau in ("region", "province"):
        nb_communes = int(communes_gdf[
            communes_gdf[REGION_IN_COMMUNE] == region
        ].shape[0]) if niveau == "region" else int(gdf.shape[0])

    return {
        "niveau"       : niveau,
        "nom"          : nom,
        "superficie_km2": round(superficie, 2),
        "nb_communes"  : nb_communes,
        "centroid_lat" : round(centre.y, 6),
        "centroid_lon" : round(centre.x, 6),
        "bounds"       : [round(b, 6) for b in bounds]
    }