# importer les bibliothèques nécessaires
import requests # pour faire des requêtes HTTP
import time # pour ajouter un délai entre les requêtes
import uuid # pour générer des identifiants uniques
import pandas as pd # pour manipuler les données
import csv # pour lire et écrire des fichiers CSV

villes = ["Mont Saint Michel", "Saint Malo"]  # liste des villes à géocoder


coordonnées = [] #liste pour stocker les coordonnées des villes

# itérer sur chaque ville pour obtenir les coordonnées
for ville in villes:
    params = {
        'q': ville , # q=paramètre de recherche
        'format': 'json', #format=json pour obtenir la réponse en JSON
        'limit': 1 #pour obtenir une seule réponse par ville (car plusieurs réponses possibles)
    } 



#sans headers, la requête peut être bloquée par le serveur = code 403
    response = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers={'User-Agent': 'Mozilla/5.0'})
        
    if response.status_code == 200: #si requête réussie
        data = response.json() #convertir la réponse en JSON
        if data: #si des données sont trouvées
            # créer un dictionnaire avec les coordonnées et la ville
            coord = { 
                'id': str(uuid.uuid4()),  # Générer un identifiant unique
                'ville': ville, #nom de la ville
                'latitude': data[0]['lat'], #latitude de la ville
                'longitude': data[0]['lon'] #longitude de la ville
                }
            coordonnées.append(coord)
        else:
            print(f"Aucune donnée trouvée pour {ville}") # si aucune donnée n'est trouvée
    else:
        print(f"Erreur lors de la requête pour {ville} :", response.status_code) #code d'erreur de la requête

    time.sleep(1)

#sauvegarder les résultats dans un fichier csv
df=pd.DataFrame(coordonnées)
chemin_fichier="D:/Profils/NLefort/Desktop/JEDHA/PROJETS/03. Data_collection_and_management"
df.to_csv(chemin_fichier + "/coordonnées_villes.csv", index=False, encoding='utf-8') #index=False, ne pas inclure l'index dans le fichier CSV
print("Les coordonnées des villes ont été enregistrées dans 'coordonnées_villes.csv'.")