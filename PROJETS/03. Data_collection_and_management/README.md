# :dart: Plan Your Trip

## :rocket: Objectif du projet

Le projet consiste à collecter des données issues de sources différentes.
Les objectifs sont les suivants :

- Collecter des données de localisation et de météo
- Agglomérer ces données pour proposer un top destinations

## :brain: Pipeline de traitement

La collecte et le traitement des données suivante la progression suivante :

```text
Collecte des données de localisation
    ↓
Collecte des données météos
    ↓
Collecte des données hôtels
    ↓
Fusion des données et chargement dans un S3
    ↓
Conversion des données en table sql et création d'une table enrichie
    ↓
Création de cartes météo et top 20 hotels
```

### Arborescence

Le projet a été découpé en scripts. **A des fins pédagogiques, un notebook est également disponible**.

```text
03. Data
|   .env # Variable d'environnements
|   arborescence.md # Arborescence détaillée du projet
|   Plan_your_trip.ipynb # Notebook du projet
|   README.md # Documentation générale du projet
|   
+---data # Fichiers générés
|       
+---scripts # Code source principale (main.py, script principal)
|   |   cartes.py
|   |   fusion_chargement_s3.py
|   |   geocodage_villes.py # script secondaire
|   |   main.py # script principal
|   |   meteo.py
|   |   rds_sql.py
|   |   scrape_hotels.py
|   |   
|   \---__pycache__

|           
\---__pycache__

```

## :wheel: Technologies & outils

| Domaine    | Outils                   |
| ---------- | ---------|
| Collecter des données sur le web | Requests, time, asyncio |
| Charger des données dans un datalake | boto3 |
| Créer une table sql | MySQL |
| Visualiser | Plotly, pandas |

## :compass: Roadmap

- [x] Collecter les latitudes et longitudes des villes concernées

- [x] Collecter les données météo des villes concernées

- [x] Collecter certaines données hôtels de ces villes sur Booking.com

- [x] Agglomérer ces données en un dataset final

- [x] Charger ce dataset final sur un s3

- [x] Créer une table SQL

- [x] Visualiser sur des cartes les résultats de ces données

## :arrow_forward: Installation, exécution, tutlisation

### 0. Prérequis

Avoir un fichier à la racine .env qui contient :

La clé API Nominatim pour collecter les données météo.

Les identifiants (credentials) d'AWS.

### 1. Lancer le notebook

Depuis votre IDE préféré, lancer le notebook

## :busts_in_silhouette: Auteurs

Projet développé par [Nadège Lefort](https://github.com/nlefort)

*La réalisation de ce projet s'inscrit dans le cadre de la [formation Data Scientist](https://www.jedha.co/formations/formation-data-scientist) développé par [Jedha](https://www.jedha.co/), en vue de l'obtention de la certification professionnelle de niveau 6 (bac+4) enregistrée au RNCP : [Concepteur développeur en science des données](https://www.francecompetences.fr/recherche/rncp/35288/).*
