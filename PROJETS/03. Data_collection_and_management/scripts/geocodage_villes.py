#bibliothèque
import requests #faire les requêtes http
import hashlib #
import time
import pandas as pd

villes=["Mont Saint Michel",
"Saint Malo",
"Bayeux",
"Le Havre",
"Rouen",
"Paris",
"Amiens",
"Lille",
"Strasbourg",
"Chateau du Haut Koenigsbourg",
"Colmar",
"Eguisheim",
"Besancon",
"Dijon",
"Annecy",
"Grenoble",
"Lyon",
"Gorges du Verdon",
"Bormes les Mimosas",
"Cassis",
"Marseille",
"Aix en Provence",
"Avignon",
"Uzes",
"Nimes",
"Aigues Mortes",
"Saintes Maries de la mer",
"Collioure",
"Carcassonne",
"Ariege",
"Toulouse",
"Montauban",
"Biarritz",
"Bayonne",
"La Rochelle"]


def id_villes(nom_ville: str) -> str:
    return hashlib.md5(nom_ville.strip().lower().encode()).hexdigest()[:12]

def geocode_ville(nom_ville: str) -> dict:
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': nom_ville,
        'format': 'json',
        'limit': 1
    }
    response = requests.get(url, params=params, headers={'User-Agent': 'GeocoderBot'})
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return {
                'id_ville': id_villes(nom_ville),
                'ville': nom_ville,
                'latitude': float(data[0]['lat']),
                'longitude': float(data[0]['lon'])
            }
        else:
            print(f"Aucune donnée trouvée pour {nom_ville}")
            return None
    else:
        print(f"Erreur lors de la requête pour {nom_ville} :", response.status_code)
        return None
    
if __name__ == "__main__":
    rows = []
    for ville in villes:
        result = geocode_ville(ville)
        if result:
            rows.append(result)
    df = pd.DataFrame(rows)
    df.to_csv("D:/Profils/NLefort/Desktop/JEDHA/PROJETS/03. Data_collection_and_management/data/geocode_villes.csv", index=False)