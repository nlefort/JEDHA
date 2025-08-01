# importer les bibliothèques nécessaires
import requests # pour faire des requêtes HTTP
import time # pour ajouter un délai entre les requêtes
import uuid # pour générer des identifiants uniques
import pandas as pd # pour manipuler les données
import csv # pour lire et écrire des fichiers CSV
from dotenv import load_dotenv
import os # pour interagir avec le système d'exploitation
import asyncio
import urllib.parse
import pandas as pd
import aiohttp
from playwright.async_api import async_playwright

# liste des villes à traiter
villes = ["Mont Saint Michel", "Saint Malo"]  # liste des villes à géocoder

# Charge les variables définies dans .env et récupère la clé API
load_dotenv()
api_key = os.getenv("API_KEY")

if api_key:
    print(" Clé API chargée avec succès :", api_key)
else:
    print(" Clé API non trouvée. Vérifie ton fichier .env")

# liste pour stocker les résultats contenant les coordonnées des villes + météo
villes_meteo = []

def coordonnees_villes(nom_ville):
# itérer sur chaque ville pour obtenir les coordonnées
    url= "https://nominatim.openstreetmap.org/search" # URL de l'API Nominatim
    params = {
        'q': nom_ville , # q=paramètre de recherche
        'format': 'json', #format=json pour obtenir la réponse en JSON
        'limit': 1 #pour obtenir une seule réponse par ville (car plusieurs réponses possibles)
    } 

    #sans headers, la requête peut être bloquée par le serveur = code 403
    response = requests.get(url, params=params, headers={'User-Agent': 'GeocoderBot'})
    if response.status_code == 200: #si requête réussie
        data= response.json() #convertir la réponse en JSON

        if data: #si des données sont trouvées
            # créer un dictionnaire avec les coordonnées et la ville
            coord = { 
                'id_ville': str(uuid.uuid4()),  # Générer un identifiant unique
                'ville': nom_ville, #nom de la ville
                'latitude': float(data[0]['lat']), #latitude de la ville
                'longitude': float(data[0]['lon']) #longitude de la ville
            }

            return coord #retourner les coordonnées de la ville


        else:
            print(f"Aucune donnée trouvée pour {nom_ville}") # si aucune donnée n'est trouvée
            return None
    else:
        print(f"Erreur lors de la requête pour {nom_ville} :", response.status_code) #code d'erreur de la requête
        return coord #retourner les coordonnées de la ville

def meteo_villes(nom_villes):
    for ville in nom_villes: #itérer sur chaque ville
        coord=coordonnees_villes(ville) #appeler la fonction pour obtenir les coordonnées de la ville
        time.sleep(1) # Pause pour respecter les quotas de l’API

        params = {
            'lat': coord['latitude'], #latitude de la ville
            'lon': coord['longitude'], #longitude de la ville
            'exclude': 'minutely,hourly,alerts', # Exclure les données non nécessaires
            'units': 'metric', # Unités métriques
            'appid': api_key # Clé API OpenWeatherMap
        }

        response = requests.get("https://api.openweathermap.org/data/3.0/onecall", params=params, headers={'User-Agent': 'WeatherBot'})

        if response.status_code == 200:
            data = response.json()  #convertir la réponse en JSON
            daily = data.get('daily', [])  # Données sur 4 jours

            if daily:
                try:  # si des données sont trouvées
                    # Moyenne température sur 7 jours
                    moy_temp = sum(jour['temp']['day'] for jour in daily[:7]) / 7
                    ressenti = sum(jour['feels_like']['day'] for jour in daily[:7]) / 7
                    humidite = sum(jour['humidity'] for jour in daily[:7]) / 7
                    prob_pluie = sum(jour.get('pop', 0) for jour in daily[:7])  # parfois pas de clé 'rain'
                    indice_uv = sum(jour['uvi'] for jour in daily[:7]) / 7

                    villes_meteo.append({
                        'id_ville': coord['id_ville'],  # Utiliser l'ID de la ville
                        'ville': coord['ville'],
                        'latitude': coord['latitude'],
                        'longitude': coord['longitude'],
                        'temp_moyenne': round(moy_temp, 1),
                        'ressenti': round(ressenti, 1),
                        'humidite': round(humidite, 1),
                        'prob_pluie': round(prob_pluie * 100, 1),  # Convertir en pourcentage
                        'indice_uv': round(indice_uv, 1)
                    })
                    print(f"Météo ajoutée pour {coord['ville']}")
                except KeyError as e:
                    print(f"Erreur de clé pour {coord['ville']}: {e}")
            else:
                print(f"Aucune donnée météo trouvée pour {coord['ville']}") 

            time.sleep(1)  # Pause pour respecter les quotas de l’API

meteo_villes(villes)  # Appel de la fonction pour récupérer les données météo
print("Nombre de villes traitées :", len(villes_meteo))


# Enregistrement des données dans un fichier CSV
chemin_fichier = "D:/Profils/NLefort/Desktop/JEDHA/PROJETS/03. Data_collection_and_management"
df = pd.DataFrame(villes_meteo)  # Convertir la liste en DataFrame
df.to_csv(chemin_fichier + "/villes_meteo.csv", index=False)  # Enregistrer le DataFrame dans un fichier CSV
print("Fichier 'villes_meteo.csv' exporté avec les coordonnées et la météo.")


# Scraping principal avec Playwright
async def scrape_booking():
    all_hotels = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        ))
        page = await context.new_page()

        for ville in villes:
            print(f"\n🔍 Scraping hôtels à {ville}...")

            coord= coordonnees_villes(ville)

            ville_encoded = urllib.parse.quote_plus(ville)
            url = f"https://www.booking.com/searchresults.fr.html?ss={ville_encoded}"
            await page.goto(url)
            await page.wait_for_timeout(5000)

            hotels = await page.locator('[data-testid="property-card"]').all()
            for hotel in hotels[:1]:  # Limite à 3 hôtels par ville
                print(hotel)
                try:
                    name = await hotel.locator('[data-testid="title"]').inner_text()
                except:
                    name = "N/A"
                try:
                    url = await hotel.locator("a").first.get_attribute("href")
                    if not url.startswith("http"):
                        url = "https://www.booking.com" + url
                except:
                    url = "N/A"
                try:
                    rating = await hotel.locator('[data-testid="review-score"]').inner_text()
                except:
                    rating = "N/A"

                # Page de l’hôtel
                description = "N/A"
                address = "N/A"
                if url != "N/A":
                    hotel_page = await context.new_page()
                    await hotel_page.goto(url)
                    await hotel_page.wait_for_timeout(3000)

                    try:
                        description = await hotel_page.locator('[data-testid="property-description"]').inner_text()
                    except:
                        description = "N/A"

                    

                    await hotel_page.close()

                all_hotels.append({
                    "id": str(uuid.uuid4()),  # Générer un identifiant unique
                    "id_ville": coord['id_ville'],  # Utiliser l'ID de la ville
                    "ville": ville,
                    "nom": name,
                    "url": url,
                    "note": rating,
                    "description": description,
                    'latitude': coord['latitude'],
                    'longitude': coord['longitude'],
                })

        await browser.close()

    # Géocodage des adresses (asynchrone)
    print("\n Géocodage des adresses...")

    # Sauvegarde
    df = pd.DataFrame(all_hotels)
# Enregistrement des données dans un fichier CSV
    chemin_fichier = "D:/Profils/NLefort/Desktop/JEDHA/PROJETS/03. Data_collection_and_management"
    df.to_csv(chemin_fichier + "/all_hotels.csv", index=False)  # Enregistrer le DataFrame dans un fichier CSV
    print("Fichier 'all_hotels.csv' exporté avec les hôtels.")


# Lancement
if __name__ == "__main__":
    asyncio.run(scrape_booking())



