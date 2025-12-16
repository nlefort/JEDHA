# :airplane: Plan Your Trip

## :rocket: Objectif du projet

Ce projet vise à créer une application de recommandation de destinations en France en se basant sur des données réelles de localisation, météo et hôtels.
Les principaux objectifs sont :

- Collecter les coordonnées géographiques des villes (latitude/longitude).

- Récupérer les données météorologiques pour chaque ville.

- Extraire certaines informations sur les hôtels via Booking.com.

- Fusionner toutes ces données pour générer un dataset enrichi et créer des visualisations.

## :brain: Pipeline de traitement

La collecte et le traitement des données suivent la progression suivante :

```text
Collecte des données de localisation (géocodage Nominatim)
    ↓
Collecte des données météo (OpenWeather API)
    ↓
Collecte des données hôtels (Booking.com)
    ↓
Fusion des données et chargement dans un S3 (datalake)
    ↓
Conversion des données en table SQL (RDS)
    ↓
Création de cartes interactives
```

### Collecte et exploitation des données

```bash
                         ┌─────────────────────────┐
                         │  Source 1 : Nominatim   │
                         │  (géocodage des villes) │
                         └─────────────┬───────────┘
                                       │
                              Requête GET
                                       │
                                       ▼
                         ┌─────────────────────────┐
                         │   geocode_villes.csv    │
                         │ ──────────────────────  │
                         │ id_ville                │
                         │ nom_ville               │
                         │ latitude  (lat)         │
                         │ longitude (lon)         │
                         └─────────────┬───────────┘
                                       │
                   Utilisation directe des coordonnées lat / lon
                                       │
              ┌────────────────────────┴────────────────────────┐
              │                                                 │
              ▼                                                 ▼

┌──────────────────────┐                      ┌──────────────────────┐
│ Source 2 :           │                      │ Source 3 :           │
│ OpenWeatherMap API   │                      │ Booking              │
└──────────┬───────────┘                      └──────────┬───────────┘
           │                                               │
    Requête GET                                      Requête GET
   (lat, lon)                                      (lat, lon)
           │                                               │
           ▼                                               ▼
┌──────────────────────┐                      ┌──────────────────────┐
│ Données météo        │                      │ Données hôtels       │
│ ───────────────────  │                      │ ───────────────────  │
│ temp_moy             │                      │ note                 │
│ ressenti_moy         │                      │ latitude             │
│ humidite_moy         │                      │ longitude            │
│ pluie_moy            │                      │ paramètres hôtels    │
│ uv_moy               │                      └──────────┬───────────┘
│ + score météo        │                                 │
└──────────┬───────────┘                                 │
           │                                             │
           ▼                                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           Fichiers intermédiaires                        │
│ ──────────────────────────────────────────────────────────────────────── │
│ villes_meteo.csv        hotels.csv                                       │
│ id_ville | nom_ville    id_ville | nom_ville | paramètres hôtels         │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      Dataset final consolidé                             │
│ ──────────────────────────────────────────────────────────────────────── │
│ Dataset_final.csv (géolocalisation + météo + hôtels)                     │
│ Bucket S3                                                                │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                ▼
                    ┌──────────────────────────┐
                    │ Base de données SQL      │
                    │ (Amazon RDS)             │
                    │ CREATE TABLE             │
                    └───────────┬──────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ Exploitation des données                                                 │
│ ──────────────────────────────────────────────────────────────────────── │
│ • Interrogation de la base SQL                                           │
│ • Agrégations (scores, moyennes, classements)                            │
│ • Création de cartes interactives                                        │
│ • Top villes selon météo / attractivité                                  │
│ • Top hôtels par ville / note / score                                    │
└──────────────────────────────────────────────────────────────────────────┘


```

Les coordonnées géographiques obtenues lors de l’étape de géocodage constituent le point central du pipeline.
Elles permettent de cibler les requêtes envoyées aux API météo et hôtelières, garantissant ainsi la cohérence spatiale des données collectées. L’ensemble des informations est ensuite consolidé, stocké et exploité à des fins analytiques et de visualisation.

### Arborescence

Le projet a été découpé en scripts. **A des fins pédagogiques, un notebook est également disponible**.

```text
03. Data
|   .env # Variable d'environnements (API keys, AWS credentials)
|   arborescence.md # Arborescence détaillée du projet
|   Plan_your_trip.ipynb # Notebook du projet
|   README.md # Documentation générale du projet
|   
+---data # Fichiers générés (CSV, HTML)
|       
+---scripts # Code source principale (main.py, script principal)
|   |   cartes.py # script secondaire
|   |   fusion_chargement_s3.py # script secondaire
|   |   geocodage_villes.py # script secondaire
|   |   main.py # script principal
|   |   meteo.py # script secondaire
|   |   rds_sql.py # script secondaire
|   |   scrape_hotels.py # script secondaire
|   |   
|   \---__pycache__

|           
\---__pycache__

```

## :wheel: Technologies & outils

| Domaine    | Outils                   |
| ---------- | ---------|
| Collecte de données web | Requests, time, asyncio |
| Stockage dans un datalake | Amazon S3 |
| Base de données relationnelle | MySQL, Amazon RDS |
| Visualisation | Plotly, pandas |

## :compass: Roadmap

- [x] Collecter les latitudes et longitudes des villes ciblées

- [x] Récupérer les données météo des villes

- [x] Extraire les informations des hôtels sur Booking.com

- [x] Fusionner toutes les données en un dataset final

- [x] Charger ce dataset final sur un bucket s3

- [x] Créer une table SQL avec les données nettoyées

- [x] Générer des cartes interactives pour les meilleures destinations et hôtels

## :arrow_forward: Installation, exécution, utilisation

### 0. Prérequis

- Python 3.9+

- Fichier ``.env`` à la racine contenant :

  - Clé API Nominatim (géocodage) et OpenWeather

  - Identifiants AWS pour S3

  - Identifiants AWS pour RDS

Installer les dépendances

### 1. Lancer le notebook

Ouvrir ``Plan_your_trip.ipynb`` dans votre IDE préféré (VSCode, Jupyter Lab, Colab…).

Exécuter les cellules étape par étape pour récupérer les données et visualiser les résultats.

## :busts_in_silhouette: Auteurs

Projet développé par [Nadège Lefort](https://github.com/nlefort)

*La réalisation de ce projet s'inscrit dans le cadre de la [formation Data Scientist](https://www.jedha.co/formations/formation-data-scientist) développé par [Jedha](https://www.jedha.co/), en vue de l'obtention de la certification professionnelle de niveau 6 (bac+4) enregistrée au RNCP : [Concepteur développeur en science des données](https://www.francecompetences.fr/recherche/rncp/35288/).*
