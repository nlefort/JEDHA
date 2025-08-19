import os
import requests
import time
import pandas as pd
from dotenv import load_dotenv

# Charge les variables définies dans .env et récupère la clé API
load_dotenv()
api_key = os.getenv("API_KEY")

def meteo_villes(lat, lon):
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric", 
        "exclude": "minutely,hourly,alerts"
    }
    r = requests.get(url, params=params, headers={"User-Agent":"WeatherBot"})
    if r.status_code == 200:
        return r.json().get("daily", [])
    return []

if __name__ == "__main__":
    cities = pd.read_csv("data/geocode_villes.csv")
    results = []
    for _, row in cities.iterrows():
        if pd.isna(row.latitude): 
            continue
        daily = meteo_villes(row.latitude, row.longitude)
        time.sleep(1)
        if daily:
            moy_temp = sum(jour['temp']['day'] for jour in daily[:7]) / 7
            ressenti = sum(jour['feels_like']['day'] for jour in daily[:7]) / 7
            humidite = sum(jour['humidity'] for jour in daily[:7]) / 7
            prob_pluie = sum(jour.get('pop', 0) for jour in daily[:7])  # parfois pas de clé 'rain'
            indice_uv = sum(jour['uvi'] for jour in daily[:7]) / 7  

            results.append({
                "id_ville": row.id_ville,
                "nom_ville": row.ville,
                "temp_moy": round(moy_temp,1),
                "ressenti": round(ressenti,1),
                "humidity_moy": round(humidite,1),
                "prob_pluie_moy": round(prob_pluie*100,1),
                "uv_moy": round(indice_uv,1),
            })
            
    df = pd.DataFrame(results)
    df.to_csv("data/villes_meteo.csv", index=False)
    print("Fichier villes_meteo.csv généré")