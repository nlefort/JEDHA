import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
import mysql.connector
from IPython.display import display

# -----------------------------
# Configuration
# -----------------------------
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Dossier de sortie pour les fichiers
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "..", "data")
os.makedirs(output_dir, exist_ok=True)

# -----------------------------
# Charger le dataset depuis RDS
# -----------------------------
def charger_dataset_final():
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    print("Connecté à RDS")

    df = pd.read_sql("SELECT * FROM hotels_final", conn)
    conn.close()
    print("Connexion RDS fermée")

    # Nettoyage des colonnes numériques
    for col in ["latitude", "longitude", "meteo_score", "note"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["latitude", "longitude"])
    return df

# -----------------------------
# Top villes
# -----------------------------
def carte_top_villes(df, top_n=5, save_files=True):
    df_villes = df.drop_duplicates(subset=["nom_ville"])
    
    df_top_villes = df_villes.sort_values(
        "meteo_score", 
        ascending=False
    ).head(top_n)

    # Scatter mapbox
    fig = px.scatter_map(
        df_top_villes,
        lat="latitude",
        lon="longitude",
        size=[15]*len(df_top_villes),
        color="meteo_score",
        hover_name="nom_ville",
        hover_data={"temp_moy": True, "ressenti": True,
                    "humidity_moy": True, "prob_pluie_moy": True, "uv_moy": True},
        zoom=5,
        height=500
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":30,"l":0,"b":0})

    display(fig)

    if save_files :
        png_path = os.path.join(output_dir, "top_villes.png")
        html_path = os.path.join(output_dir, "top_villes.html")
        csv_path = os.path.join(output_dir, "top_villes.csv")

        fig.write_image(png_path)
        fig.write_html(html_path)
        df_top_villes.to_csv(csv_path, index=False)
        print(f"Top villes exportées : {png_path}, {html_path}, {csv_path}")

    return df_top_villes

# -----------------------------
# Top hôtels
# -----------------------------
def carte_top_hotels(df, df_top_villes, top_n=20, save_files=True):
    df_hotels = df[df["nom"].notna()]
    df_hotels_topvilles = df_hotels[df_hotels["ville"].isin(df_top_villes["nom_ville"])]
    df_top20 = df_hotels_topvilles.sort_values("note", ascending=False).head(top_n)

    fig = px.scatter_map(
        df_top20,
        lat="latitude",
        lon="longitude",
        size="note",
        size_max=25,
        color="note",
        hover_name="nom",
        hover_data={"ville": True, "note": True},
        zoom=5,
        height=500
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":30,"l":0,"b":0})

    display(fig)  # Affiche directement dans le notebook

    if save_files:
        png_path = os.path.join(output_dir, "top_hotels.png")
        html_path = os.path.join(output_dir, "top_hotels.html")
        csv_path = os.path.join(output_dir, "top_hotels.csv")

        fig.write_image(png_path)
        fig.write_html(html_path)
        df_top20.to_csv(csv_path, index=False)
        print(f"Top hôtels exportés : {png_path}, {html_path}, {csv_path}")

# -----------------------------
# Pipeline complet
# -----------------------------
def visualiser_cartes_dataset_final(top_villes=5, top_hotels=20, save_files=True):
    df = charger_dataset_final()
    df_top_villes = carte_top_villes(df, top_n=top_villes, save_files=save_files)
    carte_top_hotels(df, df_top_villes, top_n=top_hotels, save_files=save_files)

# -----------------------------
# Exécution
# -----------------------------
if __name__ == "__main__":
    visualiser_cartes_dataset_final()
