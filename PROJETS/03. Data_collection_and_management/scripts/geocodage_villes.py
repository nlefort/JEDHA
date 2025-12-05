# Bibliothèques
import requests # Faire les requêtes http
import hashlib # Générer des id pour les villes
import pandas as pd
import os
import time

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
    
def generer_geocode_csv(villes: list[str], filename: str = "geocode_villes.csv"):
    """Génère un CSV contenant lat/lon de toutes les villes."""
    rows = []
    for ville in villes:
        result = geocode_ville(ville)
        if result:
            rows.append(result)
        time.sleep(1)  # pour respecter les limites de Nominatim

    if not rows:
        print("Aucun résultat récupéré, CSV non généré.")
        return

    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    print(f"Fichier CSV généré : {filename}")

# -----------------------------
# Exécution
# -----------------------------
if __name__ == "__main__":
    # Gestion du dossier data
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
    except NameError:  # pour notebooks
        base_dir = os.getcwd()

    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "geocode_villes.csv")

    generer_geocode_csv(villes, filename=csv_path)