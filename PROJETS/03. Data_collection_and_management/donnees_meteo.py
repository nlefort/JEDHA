#collecte des données météo
from dotenv import load_dotenv
import os
import requests
import pandas as pd
import time

villes = ["Mont Saint Michel", "Saint Malo"]  # liste des villes à géocoder


villes_meteo = [] #liste pour stocker les données météo des villes


# Charge les variables définies dans .env
load_dotenv()

# Récupère la clé API
api_key = os.getenv("API_KEY")

df=pd.DataFrame(villes_meteo)
#créer les colonnes météo que je veux ajouter à mon fichier CSV
df['temp_moy'] = None #daily.temp
df['ressenti'] = None #laily.feels_like
df['humidite'] = None #daily.humidity
df['prob_pluie'] = None #daily.pop
df['indice_uv'] = None #daily.uvi

print(df.columns)

for i, row in df.iterrows():
    lat = row['latitude']
    lon = row['longitude']

    #paramètres pour la requête API OpenWeatherMap
    params = {
        'lat': lat,
        'lon': lon,
        'exclude': 'minutely,hourly,alerts', # Exclure les données non nécessaires
        'units': 'metric', # Unités métriques
        'appid': api_key # Clé API OpenWeatherMap
    }

    response = requests.get("https://api.openweathermap.org/data/3.0/Onecall", params=params, headers={'User-Agent': 'Mozilla/5.0'})

    if response.status_code == 200:
        data = response.json()

        # Données sur 4 jours
        daily = data.get('daily', [])

        if daily:
            # Moyenne température sur 7 jours
            moy_temp = sum(jour['temp']['day'] for jour in daily[:7]) / 7
            ressenti = sum(jour['feels_like']['day'] for jour in daily[:7]) / 7
            humidite = sum(jour['humidity'] for jour in daily[:7]) / 7
            prob_pluie = sum(jour.get('pop', 0) for jour in daily[:7])  # parfois pas de clé 'rain'
            indice_uv = sum(jour['uvi'] for jour in daily[:7]) / 7


            df.at[i, 'temp_moyenne'] = round(moy_temp, 1)
            df.at[i, 'ressenti'] = round(ressenti, 1)
            df.at[i, 'humidite'] = round(humidite, 1)
            df.at[i, 'prob_pluie'] = round(prob_pluie * 100, 1)  # Convertir en pourcentage
            df.at[i, 'indice_uv'] = round(indice_uv, 1)


            print(f"Météo ajoutée pour {row['ville']}")
        else:
            print(f"Pas de données météo pour {row['ville']}")
    else:
        print(f"Erreur API pour {row['ville']}: {response.status_code}")

    time.sleep(1)  # Pause pour respecter les quotas de l’API

meteo_villes(villes)  # Appel de la fonction pour récupérer les données météo

print("Nombre de villes traitées :", len(villes_meteo))
# Enregistrement du fichier enrichi

chemin_fichier= "D:/Profils/NLefort/Desktop/JEDHA/PROJETS/03. Data_collection_and_management"
df.to_csv(chemin_fichier + "/villes_meteo.csv", index=False)
print(" Fichier 'villes_meteo.csv' exporté avec météo.")
