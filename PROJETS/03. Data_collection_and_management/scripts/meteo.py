import os
import requests
import time
import pandas as pd
from dotenv import load_dotenv

# Charger la clé API depuis .env
load_dotenv()
api_key = os.getenv("API_KEY")


def api_meteo_villes(lat, lon):
    """Récupère la météo quotidienne d'une ville à partir de lat/lon"""
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "exclude": "minutely,hourly,alerts"
    }
    r = requests.get(url, params=params, headers={"User-Agent": "WeatherBot"})
    if r.status_code == 200:
        return r.json().get("daily", [])
    return []


def calcul_score(row):
    """Calcule un score météo global sur 100 pour une ville"""
    # Température idéale autour de 22,5 °C
    temp_score = max(0, 1 - abs(row['temp_moy'] - 22.5) / 10)

    # Ressenti proche de la température
    ressenti_score = max(0, 1 - abs(row['ressenti'] - row['temp_moy']) / 5)

    # Humidité faible est mieux
    humidite_score = max(0, 1 - row['humidity_moy'] / 100)

    # Probabilité de pluie faible est mieux
    pluie_score = max(0, 1 - row['prob_pluie_moy'] / 100)

    # UV modéré (idéal 3-6)
    uv = row['uv_moy']
    if uv <= 6:
        uv_score = 1 - abs(4.5 - uv) / 4.5
    else:
        uv_score = max(0, 1 - (uv - 6) / 6)

    # Moyenne pondérée
    total_score = (temp_score + ressenti_score + humidite_score + pluie_score + uv_score) / 5
    return round(total_score * 100, 1)  # sur 100


def meteo_villes(save_csv=True, delay=1.0):
    """Récupère la météo pour toutes les villes et retourne un DataFrame avec score"""
    
    # Chemin vers le CSV geocode_villes.csv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    csv_path = os.path.join(root_dir, "data", "geocode_villes.csv")

    villes = pd.read_csv(csv_path)
    results = []

    for _, row in villes.iterrows():
        if pd.isna(row.latitude):
            continue

        daily = api_meteo_villes(row.latitude, row.longitude)
        time.sleep(delay)  # pause pour respecter l'API

        if daily:
            moy_temp = sum(j['temp']['day'] for j in daily[:7]) / 7
            ressenti = sum(j['feels_like']['day'] for j in daily[:7]) / 7
            humidite = sum(j['humidity'] for j in daily[:7]) / 7
            prob_pluie = sum(j.get('pop', 0) for j in daily[:7])
            indice_uv = sum(j['uvi'] for j in daily[:7]) / 7

            results.append({
                "id_ville": row.id_ville,
                "nom_ville": row.ville,
                "temp_moy": round(moy_temp, 1),
                "ressenti": round(ressenti, 1),
                "humidity_moy": round(humidite, 1),
                "prob_pluie_moy": round(prob_pluie * 100, 1),
                "uv_moy": round(indice_uv, 1)
            })

    df = pd.DataFrame(results)

    # Calcul du score météo
    if not df.empty:
        df['meteo_score'] = df.apply(calcul_score, axis=1)
        df = df.sort_values(by='meteo_score', ascending=False)

    # Sauvegarde si demandé
    if save_csv:
        data_dir = os.path.join(root_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        output_path = os.path.join(data_dir, "villes_meteo.csv")
        df.to_csv(output_path, index=False)
        print(f"Fichier CSV généré : {output_path}")

    return df


# Exécution directe si on lance le script
if __name__ == "__main__":
    meteo_villes()
