from geocodage_villes import id_villes,geocode_ville
from meteo import meteo_villes
from scrape_hotels import scrape_booking
from fusion_chargement_s3 import upload_to_s3
from rds_sql import base_sql
from cartes import carte_meteo, carte_hotel, charger_donnees

if __name__ == "__main__":
    # 1. Géocodage des villes
    geocode_ville()  # remplit lat/lon des villes

    # 2. Récupération météo
    meteo_villes()  

    # 3. Scraping hôtels
    scrape_booking()  

    # 4. Fusion / export S3
    upload_to_s3() 

    # 5. Charger SQL / RDS
    base_sql()

    # 6. Générer cartes
    df_meteo, df_hotels = charger_donnees()
    carte_meteo(df_meteo)
    carte_hotel(df_hotels)