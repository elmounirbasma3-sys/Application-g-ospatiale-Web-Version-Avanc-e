from pydantic import BaseModel
from typing import Optional, List, Any, Dict


class RegionItem(BaseModel):
    nom: str


class ProvinceItem(BaseModel):
    nom: str
    region: str


class CommuneItem(BaseModel):
    nom: str
    province: str
    region: str


class RegionListResponse(BaseModel):
    count: int
    regions: List[str]


class ProvinceListResponse(BaseModel):
    count: int
    region: str
    provinces: List[str]


class CommuneListResponse(BaseModel):
    count: int
    province: str
    region: str
    communes: List[str]


class CentreResponse(BaseModel):
    latitude: float
    longitude: float
    niveau: str          # "region" | "province" | "commune"
    nom: str
    bounds: List[float]  # [minx, miny, maxx, maxy]


class GeoJSONResponse(BaseModel):
    type: str
    features: List[Dict[str, Any]]


class StatsGeoResponse(BaseModel):
    niveau: str
    nom: str
    superficie_km2: Optional[float]
    nb_communes: Optional[int]
    centroid_lat: float
    centroid_lon: float
    bounds: List[float]