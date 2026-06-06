import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import os
# ─────────────────────────────────────────────────────────────────────────────
# CONFIG & CSS
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Dashboard GIS Météo Maroc", page_icon="🌍", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: radial-gradient(circle at top left, #1E293B 0%, #0F172A 45%, #020617 100%); }
.hero { background: linear-gradient(135deg, rgba(59,130,246,0.25), rgba(236,72,153,0.16)); border: 1px solid rgba(255,255,255,0.12); border-radius: 24px; padding: 26px 32px; margin-bottom: 22px; }
.hero-title { font-size: 2.2rem; font-weight: 900; color: white; margin-bottom: 8px; }
.card-title { font-size: 1.1rem; font-weight: 800; color: #F8FAFC; margin-bottom: 12px; }
.info-card { background: rgba(15,23,42,0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 14px 16px; margin-bottom: 12px; }
.info-value { color: white; font-size: 1.05rem; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ── URL du backend ──
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS API
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def api_get_regions():
    return requests.get(f"{BACKEND_URL}/geo/regions").json()["regions"]

@st.cache_data(ttl=3600)
def api_get_provinces(region):
    return requests.get(f"{BACKEND_URL}/geo/provinces", params={"region": region}).json()["provinces"]

@st.cache_data(ttl=3600)
def api_get_communes(region, province):
    return requests.get(f"{BACKEND_URL}/geo/communes", params={"region": region, "province": province}).json()["communes"]

@st.cache_data(ttl=3600)
def api_get_centre(region, province=None, commune=None):
    p = {"region": region, "province": province, "commune": commune}
    return requests.get(f"{BACKEND_URL}/geo/centre", params=p).json()

@st.cache_data(ttl=3600)
def api_get_geojson(region, province=None, commune=None):
    p = {"region": region, "province": province, "commune": commune}
    return requests.get(f"{BACKEND_URL}/geo/geojson", params=p).json()

@st.cache_data(ttl=1800)
def api_get_meteo(lat, lon):
    return requests.get(f"{BACKEND_URL}/meteo/previsions", params={"latitude": lat, "longitude": lon}).json()

# ─────────────────────────────────────────────────────────────────────────────
# INTERFACE GRAPHIQUE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero"><div class="hero-title">🌍 Dashboard GIS Météo Maroc</div><div style="color:#CBD5E1">Navigation administrative et prévisions climatiques (Backend FastAPI)</div></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.9, 2.1, 1.4], gap="large")

# --- COLONNE 1 : NAVIGATION ---
with col1:
    with st.container(border=True):
        st.markdown('<div class="card-title">🧭 Navigation</div>', unsafe_allow_html=True)
        try:
            regions = api_get_regions()
            sel_reg = st.selectbox("Choisir une région", [""] + regions)
            
            sel_prov = ""
            if sel_reg:
                provinces = api_get_provinces(sel_reg)
                sel_prov = st.selectbox("Choisir une province", [""] + provinces)
            
            sel_com = ""
            if sel_prov:
                communes = api_get_communes(sel_reg, sel_prov)
                sel_com = st.selectbox("Choisir une commune", [""] + communes)
        except:
            st.error("Connectez le backend (port 8000)")
            st.stop()

    with st.container(border=True):
        st.markdown('<div class="card-title">🗺️ Affichage</div>', unsafe_allow_html=True)
        mode = st.radio("Mode carte", ["Contour seulement", "Contour + MNT", "MNT seulement"])

# --- COLONNE 2 : CARTE ---
with col2:
    if not sel_reg:
        st.info("👈 Sélectionnez une région pour commencer")
    else:
        # Récupérer données géo via API
        geo_info = api_get_centre(sel_reg, sel_prov if sel_prov else None, sel_com if sel_com else None)
        lat, lon = geo_info["latitude"], geo_info["longitude"]
        bounds = geo_info["bounds"]
        
        st.markdown(f'<div class="info-card"><div class="info-value">📍 {sel_com or sel_prov or sel_reg}</div></div>', unsafe_allow_html=True)
        
        # Créer la carte
        m = folium.Map(location=[lat, lon], zoom_start=7, tiles="OpenStreetMap")
        
        # Ajouter le contour GeoJSON via API
        if "MNT" not in mode:
            geojson_data = api_get_geojson(sel_reg, sel_prov if sel_prov else None, sel_com if sel_com else None)
            folium.GeoJson(geojson_data, style_function=lambda x: {'fillOpacity': 0.1, 'color': '#3B82F6', 'weight': 3}).add_to(m)
        
        if "MNT" in mode:
            folium.raster_layers.WmsTileLayer(url="https://ows.terrestris.de/osm/service?", layers="SRTM30-Colored-Hillshade", name="MNT", fmt="image/png", transparent=True).add_to(m)
            
        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        st_folium(m, width=700, height=500)

# --- COLONNE 3 : METEO ---
with col3:
    if sel_reg:
        st.markdown('<div class="card-title">🌦️ Prévisions</div>', unsafe_allow_html=True)
        meteo_data = api_get_meteo(lat, lon)
        df = pd.DataFrame(meteo_data["previsions"])
        
        resume = meteo_data["resume"]
        m1, m2 = st.columns(2)
        m1.metric("Temp. Moy", f"{resume['t_moy_max']}°C")
        m2.metric("Pluie Tot.", f"{resume['pluie_totale']}mm")
        
        param = st.radio("Graphique", ["Température", "Précipitations"], horizontal=True)
        
        if param == "Température":
            fig = px.line(df, x="date", y="t_max", title="Température Max (°C)")
            fig.update_traces(line_color='#F43F5E')
        else:
            fig = px.bar(df, x="date", y="precipitation", title="Précipitations (mm)")
            fig.update_traces(marker_color='#3B82F6')
            
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig, use_container_width=True)