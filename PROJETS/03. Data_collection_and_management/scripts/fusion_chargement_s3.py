import pandas as pd
from dotenv import load_dotenv
import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError

# 1. Charger les datasets
geocode = pd.read_csv("data/geocode_villes.csv")
meteo = pd.read_csv("data/villes_meteo.csv")
hotels = pd.read_csv("data/hotels.csv")

print(" Fichiers chargés :")
print(" - geocode:", geocode.shape)
print(" - meteo:", meteo.shape)
print(" - hotels:", hotels.shape)

df_geo = pd.read_csv("data/geocode_villes.csv")
df_hotels = pd.read_csv("data/hotels.csv")
df_meteo = pd.read_csv("data/villes_meteo.csv")

# --- Étape 2 : Merge hôtels avec géocode ---
df_hotels_geo = pd.merge(df_hotels, df_geo, on="id_ville", how="left", suffixes=('', '_geo'))

# Supprimer colonnes dupliquées (ville, latitude, longitude)
df_hotels_geo = df_hotels_geo.drop(columns=[col for col in df_hotels_geo.columns if col.endswith('_geo')])

# --- Étape 3 : Merge avec météo ---
df_final = pd.merge(df_hotels_geo, df_meteo, on="id_ville", how="left", suffixes=('', '_meteo'))

# Supprimer colonnes dupliquées issues de météo (ville, latitude, longitude)
for col in ['ville_meteo', 'latitude_meteo', 'longitude_meteo']:
    if col in df_final.columns:
        df_final.drop(columns=[col], inplace=True)

# --- Étape 4 : Réorganisation des colonnes (optionnel) ---
cols_order = [
    'id', 'id_ville', 'ville', 'nom', 'url', 'note', 'description',
    'latitude', 'longitude',
    'temp_moyenne', 'ressenti', 'humidite', 'prob_pluie', 'indice_uv'
]

# 3. Sauvegarder en local
output_path = "data/dataset_final.csv"
df_final.to_csv(output_path, index=False)
print(f"Fichier consolidé exporté : {output_path}")

# 4. Upload sur S3
load_dotenv()
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
bucket_name = os.getenv("S3_BUCKET_NAME")
s3_key = "final/dataset_final.csv"

def upload_to_s3(local_file, bucket, key):
    s3 = boto3.client("s3",
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      region_name=aws_region)
    try:
        s3.upload_file(local_file, bucket, key)
        print(f"Upload réussi vers s3://{bucket}/{key}")
    except FileNotFoundError:
        print("Fichier local non trouvé.")
    except NoCredentialsError:
        print("Identifiants AWS manquants.")
    except ClientError as e:
        print(f"Erreur S3 : {e}")

if bucket_name:
    upload_to_s3(output_path, bucket_name, s3_key)

if __name__ == "__main__":
    upload_to_s3(output_path, bucket_name, s3_key)