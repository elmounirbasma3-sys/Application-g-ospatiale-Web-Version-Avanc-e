# Dashboard Géospatial Météo Maroc (Version Avancée)

## Présentation du Projet
Ce projet est une application géospatiale interactive permettant d'explorer les divisions administratives du Maroc (Régions, Provinces, Communes) tout en visualisant des données topographiques (MNT) et des prévisions météorologiques en temps réel.

### Au-delà du cadre académique
Dans le cadre de ce projet académique, j'ai choisi de ne pas me limiter à une simple application monolithique. J'ai développé une **version avancée** basée sur une **architecture découplée (Client-Serveur)** :

1.  **Backend FastAPI** : Une API robuste qui gère la logique lourde, la lecture des fichiers Shapefile (fichiers SIG) et les calculs géospatiaux (centroïdes, statistiques de superficie).
2.  **Frontend Streamlit** : Une interface utilisateur moderne et réactive qui communique avec le backend via des requêtes HTTP (JSON).

Cette approche simule une application de production réelle, permettant une meilleure scalabilité et la réutilisation des données par d'autres plateformes (mobile, web ou outils SIG comme QGIS).

---

## Stack Technique
- **Langage** : Python 3.11+
- **Backend** : FastAPI, Uvicorn (Serveur ASGI)
- **Frontend** : Streamlit
- **SIG / Cartographie** : GeoPandas, Folium, Streamlit-Folium, Shapely
- **Visualisation de données** : Plotly Express (Graphiques interactifs)
- **Données Météo** : API Open-Meteo (Prévisions à 15 jours)
- **Topographie** : WMS Terrestris (Modèle Numérique de Terrain)

---

## Architecture du Projet
L'application est structurée de manière modulaire pour séparer les responsabilités :

```
📁 app_vAvancee/
├── 📄 app.py              # Interface utilisateur (Streamlit)
├── 📁 backend/
│   ├── 📄 main.py         # Point d'entrée de l'API
│   ├── 📁 routers/        # Routes Geo et Météo
│   ├── 📁 services/       # Logique métier et calculs SIG
│   └── 📁 schemas/        # Modèles de données Pydantic
├── 📁 data/               # Fichiers sources Shapefiles (.shp, .dbf, etc.)
└── 📄 requirements.txt    # Dépendances du projet
```

---

## Fonctionnalités Clés
- **Navigation Hiérarchique** : Filtrage dynamique des Provinces et Communes en fonction de la Région sélectionnée.
- **Visualisation Cartographique** : 
    - Affichage des contours administratifs.
    - Couche MNT (Modèle Numérique de Terrain) via flux WMS.
    -Recentrage automatique de la carte sur l'entité sélectionnée.
- **Analyse de Données** : Calcul en temps réel de la superficie de l'entité (via projection Lambert) et statistiques climatiques.
- **Prévisions Météo** : Graphiques interactifs (Température/Précipitations) mis à jour instantanément selon la localisation GPS du centre de l'entité choisie.

---

## Installation et Lancement

1. **Cloner le projet** :
   ```bash
   git clone https://github.com/elmounirbasma3-sys/Application-g-ospatiale-Web-Version-Avanc-e
   cd app_vAvancee
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer le Backend (Terminal 1)** :
   ```bash
   python -m uvicorn backend.main:app --reload --port 8000
   ```

4. **Lancer le Frontend (Terminal 2)** :
   ```bash
   python -m streamlit run app.py
   ```

---

## Perspectives d'évolution
- Ajout d'une base de données spatiale **PostGIS** pour remplacer les fichiers Shapefile.
- Authentification des utilisateurs pour la sauvegarde de zones favorites.
- Ajout de couches de risques (inondations, sécheresse) basées sur des données historiques.

---
**Auteur :** [EL MOUNIR Basma]
**Cadre :** Projet Académique - SIG & Programmation Python 2025