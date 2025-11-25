import pandas as pd
import mysql.connector
import plotly.express as px
import webbrowser
from dotenv import load_dotenv
import os


# -----------------------------
# Connexion et chargement des données
# -----------------------------
def charger_donnees():
    load_dotenv()
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    print("Connecté à MariaDB")

    # ---  Récupération des données météo ---
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

    connection.close()
    print("Connexion MariaDB fermée")

    # --- Nettoyage ---
    # Météo
    cols_meteo = ["temp_moy", "ressenti", "humidity_moy", "uv_moy", "latitude", "longitude"]
    for col in cols_meteo:
        df_meteo[col] = pd.to_numeric(df_meteo[col], errors='coerce')
    df_meteo = df_meteo.dropna(subset=["latitude", "longitude", "temp_moy"])

    # Hôtels
    df_hotels["note"] = pd.to_numeric(df_hotels["note"], errors='coerce')
    df_hotels["latitude"] = pd.to_numeric(df_hotels["latitude"], errors='coerce')
    df_hotels["longitude"] = pd.to_numeric(df_hotels["longitude"], errors='coerce')
    df_hotels = df_hotels.dropna(subset=["latitude", "longitude", "note"])

    return df_meteo, df_hotels


# -----------------------------
# Fonction CARTE METEO
# -----------------------------
def carte_meteo(df_meteo):
    fig = px.scatter_mapbox(
        df_meteo,
        lat="latitude",
        lon="longitude",
        size=[10] * len(df_meteo),  # taille uniforme
        color="temp_moy",
        color_continuous_scale="RdBu_r",
        hover_name="ville",
        hover_data={"temp_moy": True, "ressenti": True, "humidity_moy": True, "uv_moy": True,
                    "latitude": False, "longitude": False},
        zoom=5,
        height=600
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":30,"l":0,"b":0})

    output = "data/carte_meteo.html"
    fig.write_html(output)
    webbrowser.open(output)
    print("Carte météo générée :", output)


# -----------------------------
# Fonction CARTE TOP 20 HÔTELS
# -----------------------------
def carte_hotel(df_hotels):
    df_top20 = df_hotels.sort_values("note", ascending=False).head(20)

    fig = px.scatter_mapbox(
        df_top20,
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
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":30,"l":0,"b":0})

    output = "data/top20_hotels.html"
    fig.write_html(output)
    webbrowser.open(output)
    print("Carte hôtels générée :", output)


# -----------------------------
# Lancement du script
# -----------------------------
if __name__ == "__main__":
    df_meteo, df_hotels = charger_donnees()

    # Appels des fonctions
    carte_meteo(df_meteo)
    carte_hotel(df_hotels)
