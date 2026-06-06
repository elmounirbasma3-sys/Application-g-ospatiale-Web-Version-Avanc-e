from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.services.geo_service import (
    service_get_regions,
    service_get_provinces,
    service_get_communes,
    service_get_centre,
    service_get_geojson,
    service_get_stats,
)

router = APIRouter(prefix="/geo", tags=["Géospatial"])


# ── GET /geo/regions ──────────────────────────────────────────────────────────
@router.get("/regions", summary="Liste de toutes les régions")
def get_regions():
    """
    Retourne la liste triée de toutes les régions du Maroc.
    """
    try:
        regions = service_get_regions()
        return {"count": len(regions), "regions": regions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /geo/provinces ────────────────────────────────────────────────────────
@router.get("/provinces", summary="Provinces d'une région")
def get_provinces(
    region: str = Query(..., description="Nom de la région")
):
    """
    Retourne la liste des provinces/préfectures
    appartenant à la région spécifiée.
    """
    try:
        provinces = service_get_provinces(region)
        if not provinces:
            raise HTTPException(
                status_code=404,
                detail=f"Région '{region}' introuvable ou sans provinces."
            )
        return {"count": len(provinces), "region": region, "provinces": provinces}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /geo/communes ─────────────────────────────────────────────────────────
@router.get("/communes", summary="Communes d'une province")
def get_communes(
    region  : str = Query(..., description="Nom de la région"),
    province: str = Query(..., description="Nom de la province")
):
    """
    Retourne la liste des communes appartenant
    à la province et à la région spécifiées.
    """
    try:
        communes = service_get_communes(region, province)
        if not communes:
            raise HTTPException(
                status_code=404,
                detail=f"Province '{province}' introuvable dans '{region}'."
            )
        return {
            "count"   : len(communes),
            "region"  : region,
            "province": province,
            "communes": communes
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /geo/centre ───────────────────────────────────────────────────────────
@router.get("/centre", summary="Centroïde et bornes d'une entité")
def get_centre(
    region  : str           = Query(...),
    province: Optional[str] = Query(None),
    commune : Optional[str] = Query(None)
):
    """
    Calcule le centroïde et les bornes géographiques
    de l'entité administrative demandée.
    """
    try:
        return service_get_centre(region, province, commune)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /geo/geojson ──────────────────────────────────────────────────────────
@router.get("/geojson", summary="GeoJSON d'une entité")
def get_geojson(
    region  : str           = Query(...),
    province: Optional[str] = Query(None),
    commune : Optional[str] = Query(None)
):
    """
    Retourne la géométrie complète en format GeoJSON
    de l'entité administrative demandée.
    """
    try:
        return service_get_geojson(region, province, commune)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /geo/stats ────────────────────────────────────────────────────────────
@router.get("/stats", summary="Statistiques d'une entité")
def get_stats(
    region  : str           = Query(...),
    province: Optional[str] = Query(None),
    commune : Optional[str] = Query(None)
):
    """
    Retourne les statistiques géographiques :
    superficie, nombre de communes, centroïde, bornes.
    """
    try:
        return service_get_stats(region, province, commune)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))