import pandas as pd
import time
import asyncio

from geocodage_villes import villes,generer_geocode_csv
from meteo import meteo_villes
from scrape_hotels import scrape_booking
from fusion_chargement_s3 import generer_dataset_final, upload_dataset_final_s3
from rds_sql import base_sql
from cartes import visualiser_cartes_dataset_final

if __name__ == "__main__":
    # 1. Géocodage des villes
    generer_geocode_csv(villes)

    # 2. Récupération météo
    meteo_villes()  

    # 3. Scraping hôtels
    asyncio.run(scrape_booking()) 

    # 4. Fusion / export S3
    df = generer_dataset_final()
    upload_dataset_final_s3()

    # 5. Charger SQL / RDS
    base_sql()

    # 6. Générer cartes
    visualiser_cartes_dataset_final(top_villes=5, top_hotels=20, save_files=True)