# Plan Your Trip with Kayak

## Contexte du projet

##  Objectif du projet

Le marketing team souhaite créer une application recommandant les meilleures destinations et hôtels basée sur des données réelles :
- Météo des destinations
- Informations sur les hôtels

Problématique : 70% des utilisateurs veulent plus d’informations sur leur destination et font confiance aux marques connues pour leurs contenus.

## Goals

- Scraper les données des destinations. 
- Obtenir les données météo de chaque ville.
- Récupérer les informations sur les hôtels pour chaque destination.
- Stocker toutes les données dans un Data Lake (S3).
- Nettoyer et transformer les données, puis les charger dans un Data Warehouse (SQL RDS).
- Recommander les meilleures destinations et hôtels à partir des données collectées.

## Scope du projet

Le projet se concentre sur les 35 meilleures villes à visiter en France : ["Mont Saint Michel", "St Malo", "Bayeux", "Le Havre", "Rouen", "Paris", "Amiens", "Lille", "Strasbourg", "Chateau du Haut Koenigsbourg", "Colmar", "Eguisheim", "Besancon", "Dijon", "Annecy", "Grenoble", "Lyon", "Gorges du Verdon", "Bormes les Mimosas", "Cassis", "Marseille", "Aix en Provence", "Avignon", "Uzes", "Nimes", "Aigues Mortes", "Saintes Maries de la mer",  "Collioure", "Carcassonne", "Ariege", "Toulouse", "Montauban", "Biarritz", "Bayonne", "La Rochelle"]

## Deliverables

- CSV dans un S3 bucket avec les informations enrichies sur météo et hôtels.
- Base de données SQL contenant les mêmes données nettoyées.
- Cartes interactives : Top-5 destinations, Top-20 hôtels

## Technologies & outils

Python – Pandas, NumPy, Requests, BeautifulSoup, scrapy

AWS – S3, RDS

SQL – PostgreSQL ou MySQL

Visualisation – Plotly, Folium

APIs – OpenWeatherMap, Nominatim
