import os
import pandas as pd
from dotenv import load_dotenv
import boto3
import mysql.connector

# -----------------------------
# Chemins CSV
# -----------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)       # remonte au projet
data_dir = os.path.join(root_dir, "data")    # point vers data/ à côté de scripts/

hotels_path = os.path.join(data_dir, "hotels.csv")
meteo_path = os.path.join(data_dir, "villes_meteo.csv")
geo_path = os.path.join(data_dir, "geocode_villes.csv")
dataset_path = os.path.join(data_dir, "dataset_final.csv")

# -----------------------------
# Charger les variables d'environnement
# -----------------------------
load_dotenv()

# -----------------------------
# Fonctions réutilisables
# -----------------------------
def generer_dataset_final():
    """Fusionne hôtels, géocodage et météo pour créer le dataset final."""
    df_hotels = pd.read_csv(hotels_path)
    df_meteo = pd.read_csv(meteo_path)
    df_geo = pd.read_csv(geo_path)

    # Merge hôtels avec géocode
    df_hotels_geo = pd.merge(df_hotels, df_geo, on="id_ville", how="left", suffixes=('', '_geo'))
    df_hotels_geo = df_hotels_geo.drop(columns=[col for col in df_hotels_geo.columns if col.endswith('_geo')])

    # Merge avec météo
    df_final = pd.merge(df_hotels_geo, df_meteo, on="id_ville", how="left", suffixes=('', '_meteo'))
    for col in ['ville_meteo', 'latitude_meteo', 'longitude_meteo']:
        if col in df_final.columns:
            df_final.drop(columns=[col], inplace=True)

    # Sauvegarde locale
    df_final.to_csv(dataset_path, index=False)
    print(f"Dataset final généré : {dataset_path}")
    print("Colonnes présentes :", df_final.columns)
    print(df_final.head())
    return df_final

def upload_to_s3(local_file: str, bucket: str, key: str):
    """Upload un fichier local sur S3"""
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )
    try:
        s3.upload_file(local_file, bucket, key)
        print(f"Upload réussi vers s3://{bucket}/{key}")
    except Exception as e:
        print("Erreur upload S3 :", e)

def upload_dataset_final_s3():
    """Upload du dataset final sur S3"""
    bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_key = "data/dataset_final.csv"
    if bucket_name:
        upload_to_s3(dataset_path, bucket_name, s3_key)


# -----------------------------
# Exécution directe
# -----------------------------
if __name__ == "__main__":
    df_final = generer_dataset_final()
    upload_dataset_final_s3()
