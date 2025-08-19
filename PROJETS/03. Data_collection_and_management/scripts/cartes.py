import pandas as pd
import mysql.connector
import plotly.express as px
import webbrowser
from dotenv import load_dotenv
import os

load_dotenv()
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# --- Connexion à MariaDB ---
connection = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)
print("Connecté à MariaDB")

# ---  Récupération des données météo par ville ---
query_meteo = """
SELECT ville, latitude, longitude, temp_moy, ressenti, humidity_moy, uv_moy
FROM hotels_final
"""
df_meteo = pd.read_sql(query_meteo, connection)

# --- Récupération des données hôtels ---
query_hotels = """
SELECT nom, ville, latitude, longitude, note
FROM hotels_final
"""
df_hotels = pd.read_sql(query_hotels, connection)

# --- Nettoyage de la colonne note ---
df_hotels['note'] = df_hotels['note'].astype(str)
df_hotels['note_num'] = df_hotels['note'].str.extract(r'(\d+[\.,]?\d*)')[0]
df_hotels['note_num'] = df_hotels['note_num'].str.replace(',', '.').astype(float)

connection.close()
print("Connexion MariaDB fermée")

# --- Nettoyage et conversion ---
# Météo
for col in ["temp_moy", "ressenti", "humidity_moy", "uv_moy", "latitude", "longitude"]:
    df_meteo[col] = pd.to_numeric(df_meteo[col], errors='coerce')
df_meteo = df_meteo.dropna(subset=["latitude", "longitude", "temp_moy"])

# Hôtels
df_hotels["note"] = pd.to_numeric(df_hotels["note"], errors='coerce')
df_hotels["latitude"] = pd.to_numeric(df_hotels["latitude"], errors='coerce')
df_hotels["longitude"] = pd.to_numeric(df_hotels["longitude"], errors='coerce')
df_hotels = df_hotels.dropna(subset=["latitude", "longitude", "note"])

# ---  Carte météo ---
fig_meteo = px.scatter_mapbox(
    df_meteo,
    lat="latitude",
    lon="longitude",
    size=[10]*len(df_meteo),  # taille uniforme
    color="temp_moy",
    color_continuous_scale="RdBu_r",
    hover_name="ville",
    hover_data={"temp_moy": True, "ressenti": True, "humidity_moy": True, "uv_moy": True,
                "latitude": False, "longitude": False},
    zoom=5,
    height=600
)
fig_meteo.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":30,"l":0,"b":0})
fig_meteo.write_html("data/carte_meteo.html")
webbrowser.open("carte_meteo.html")  # ouvre directement dans le navigateur

# --- Carte top 20 hôtels ---
df_hotels_top = df_hotels.sort_values("note", ascending=False).head(20)
fig_hotels = px.scatter_mapbox(
    df_hotels_top,
    lat="latitude",
    lon="longitude",
    size="note",
    size_max=25,
    color="note",
    color_continuous_scale="Greens",
    hover_name="nom",
    hover_data={"ville": True, "note": True, "latitude": False, "longitude": False},
    zoom=5,
    height=600
)
fig_hotels.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":30,"l":0,"b":0})
fig_hotels.write_html("data/top20_hotels.html")
webbrowser.open("top20_hotels.html")  # ouvre directement dans le navigateur
