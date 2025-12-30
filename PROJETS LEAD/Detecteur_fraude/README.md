# :dart: Détecteur de fraude

## :rocket: Objectifs du projet

Le projet consiste à utiliser l'IA pour détecter les paiements frauduleux. L'algorithme d'apprentissage doit être en capacité de prédire les paiements frauduleux en temps réel et doit être mis en production dans un environnement standardisé afin d'être utilisé par plusieurs équipes  :

- Détecter les fraudes en temps réel sur des transactions bancaires
- Envoi des notifications quand une fraude est détectée
- Génère un rapport quotidien quand une fraude est détectée

## Architecture 

## :deciduous_tree: Arborescence du projet

```text
08.Déploiement
|   .Dockerignore # Fichiers ignorés par le conteneur Docker
|   README.md
|   requirements.txt # Dépendances globales
|   train_model.py # Script d'entraînement avec MLflow
+---api # API FastAPI déployée sur Hugging Face
+---data # Données sources
+---mlruns
+---model # Modèle final sauvegardé
+---notebooks # EDA et ML
\---streamlit # Dashborad web interactif
 ```

## :brain: Pipeline de traitement

La collecte et le traitement des données suivent la progression suivante :

```text
Importation des données
↓
Analyse exploratoire (EDA)
↓
Prétraitement (nettoyage, dates, outliers)
↓
Entraînement d’un modèle CatBoost
↓
Évaluation et interprétation
↓
Enregistrement du modèle avec MLflow
↓
Déploiement du modèle de prédiction (FastApi)
↓
Mise à disposition des analyses et du modèle de prédiction (Streamlit)
↓
Déploiement du modèle, API de prédiction, dashboard, MLflow (Docker)
↓
Automatisation des tâcjes (Airflow)
```

| Étape                    | Description                                             |
| ------------------------ | ------------------------------------------------------- |
| **Données sources**      | Fichiers `.csv` fournis  |
| **EDA / Prétraitement**  | Analyse exploratoire, nettoyage, encodage des features  |
| **Modèle ML (CatBoost)** | Régression du prix de location journalier               |
| **MLflow Tracking**      | Suivi complet : hyperparamètres, RMSE, R², modèle loggé |
| **Export modèle**        | Sauvegarde en `.pkl` pour intégration API               |
| **API FastAPI**          | Endpoint `/predict` pour servir le modèle               |
| **Dashboard Streamlit**  | ... |
| **Décision finale**      | ... |

### Interaction utilisateur

```pqsql
                Utilisateur
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
┌───────────┐ ┌──────────────┐ ┌─────────────┐
│ Navigateur│ │ Navigateur   │ │ Navigateur  │
│ :8000     │ │ :8501        │ │ :5000       │
└─────┬─────┘ └──────┬───────┘ └─────┬───────┘
      │              │               │
      ▼              ▼               ▼
 FastAPI         Streamlit        MLflow UI
 API REST        Dashboard        Expériences
 (prédiction)    Visualisation    Modèles

```

## Focus : Standardisation de l'environnement

```pgsql
┌───────────────────────────────┐
│        Démarrage Docker       │
│   (docker run )               │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Image Python 3.10             │
│ Environnement d’exécution     │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Installation des dépendances  │
│ - FastAPI                     │
│ - Streamlit                   │
│ - MLflow                      │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Copie du code applicatif      │
│ (API, UI, modèles, données)   │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Exécution du script start.sh  │
│ (orchestration des services)  │
└───────────────┬───────────────┘
                │
                ▼
      ┌─────────────────────────────┐
      │ Lancement des services      │
      │ en parallèle                │
      └─────────────┬───────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌─────────────┐ ┌──────────────┐ ┌─────────────┐
│ FastAPI     │ │ Streamlit    │ │ MLflow      │
│ API REST    │ │ Interface UI │ │ Tracking    │
│ Port 8000   │ │ Port 8501    │ │ Port 5000   │
└─────┬───────┘ └──────┬───────┘ └─────┬───────┘
      │                │               │
      ▼                ▼               ▼
  Consommation API  Visualisation   Suivi des
  (prédictions,     des résultats   expériences
   inference)       & modèles       & modèles

```

L’architecture repose sur un conteneur Docker intégrant trois services :

- une API FastAPI exposée via Uvicorn pour la logique métier et l’inférence des modèles
- une interface Streamlit destinée à la visualisation et à l’interaction utilisateur
- un serveur MLflow permettant le suivi des expériences, des métriques et des modèles entraînés.
Le lancement simultané de ces services est assuré par un script d’orchestration (start.sh).
Chaque composant est accessible via un port distinct.

### Commandes principales

| Étape            | Commande                         | Description                                  |
| ---------------- | -------------------------------- | -------------------------------------------- |
| **Entraînement** | `python train_model.py`          | Entraîne et enregistre le modèle dans MLflow |
| **MLflow UI**    | `mlflow ui`                      | Démarre l’interface de suivi                 |
| **API (local)**  | `uvicorn api.app:app --reload`   | Lance le serveur FastAPI local               |
| **Dashboard**    | `streamlit run streamlit/app.py` | Lance le tableau de bord Streamlit           |
| **Déploiement**  | Docker + Hugging Face            | Met l’ensemble en production                 |

### Technologies & outils

| Domaine                     | Outils                                      |
| --------------------------- | ------------------------------------------- |
| **Analyse & Visualisation** | Pandas, NumPy, Seaborn, Matplotlib, Plotly  |
| **Machine Learning**        | CatBoost, Scikit-learn, GridSearchCV        |
| **Déploiement**             | FastAPI, Streamlit, Uvicorn, Docker, MLflow |
| **Testing & Requêtes**      | Curl, Requests                              |

### Méthodes de l'API

| Endpoint   | Méthode | Description                               |
| ---------- | ------- | ----------------------------------------- |
| `/`        | GET     | Message d’accueil                         |
| `/health`  | GET     | Vérifie si l’API fonctionne               |
| `/predict` | POST    | Renvoie une prédiction à partir d’un JSON |
| `/docs`    | GET     | Interface Swagger interactive             |

## :running: Instruction d'exécution (local & Docker)

### Visualiser l'analyse descriptive complète

Ouvrir `notebooks/EDA.ipynb`

### Visualiser la constitution du modèle de ML

Ouvrir `notebook/ML.ipynb`

### Entraînement du modèle (local)

Commande à effectuer à la racine du projet

Entraînement du modèle CatBoost et sauvegarde --> `python train_model.py`
Réponse attendue :

``` bash
Dataset chargé : (4843, 14)
[...]
Entraînement du modèle CatBoost...
Entraînement terminé.
RMSE: 14.23 €
R2: 0.82
Modèle loggé dans MLflow.
[...]
Modèle sauvegardé dans d:\Profils\NLefort\Desktop\JEDHA\PROJETS\08.Déploiement\model\model_auto.pkl

Prix prédit : 141.17 € / jour
Fourchette ±10% : 127.06 € - 155.29 €
```

### Visualisation MLFlow (local)

Commande à effectuer à la racine du projet

Lancer l'interface de suivi MLFlow --> `mlflow ui`

Réponse attendue :

```bash
[INFO] Starting MLflow UI at http://127.0.0.1:5000
[...]
INFO:     Application startup complete.
```

Ouvrir dans le navigateur : <http://127.0.0.1:5000>

### Lancer le service API (local)

1.Lancer le serveur à la racine du projet

```bash
uvicorn api.app:app --reload
```

Sortie attendue :

```bash
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

2.Tester dans le navigateur

- <http://127.0.0.1:8000> → message d’accueil
- <http://127.0.0.1:8000/docs>  → interface documentation API

3.Exemple de requête POST (curl)

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
-H "Content-Type: application/json" \
-d "{\"model_key\":\"Renault\",\"fuel\":\"diesel\",\"paint_color\":\"noir\",\"car_type\":\"compact\",\"private_parking_available\":1,\"has_gps\":1,\"has_air_conditioning\":0,\"automatic_car\":0,\"has_getaround_connect\":1,\"has_speed_regulator\":0,\"winter_tires\":0,\"mileage\":50000,\"engine_power\":110}"
```

Réponse attendue :

```bash
{
  "prediction": 141.17,
  "interval": [127.06, 155.29]
}
```

4.Exemple avec Python

utiliser le script api/test.py

``` python
import requests

url = "http://127.0.0.1:8000/predict"
data = {
  "model_key": "Renault",
  "fuel": "diesel",
  "paint_color": "noir",
  "car_type": "compact",
  "private_parking_available": "Oui",
  "has_gps": "Oui",
  "has_air_conditioning": "Non",
  "automatic_car": "Non",
  "has_getaround_connect": "Oui",
  "has_speed_regulator": "Non",
  "winter_tires": "Non",
  "mileage": 50000,
  "engine_power": 110
}

resp = requests.post(url, json=data)
print(resp.status_code)
print(resp.json())
print(f"Prédiction de prix : {resp.json()['prediction']:.2f} €")

```

Commande attendue (ouvrir un nouveau terminal)

```bash
python test.py
```

### Lancer le service Streamlit (local)

1.Lancer le serveur à la racine du projet (>dossier streamlit/)

```bash
python app.py
```
2.Tester dans le navigateur

- <http://127.0.0.1:8501> → Visualisation du dashboard


### :whale: Déploiement Docker (mise en production)

```bash
docker build -t getaround-all .
docker run --rm -v ${PWD}:/app getaround-all python /app/train_model.py
docker run -p 5000:5000 -p 8000:8000 -p 8501:8501 -v ${PWD}:/app getaround-all

```

- le déploiement Docker doit permettre
  - Construire l'image Docker -> docker build -t getaround-all .
  - lancer le script train_model.py -> docker run --rm -v ${PWD}:/app getaround-all python /app/train_model.py
  - visualiser MLFlow -> `http://0.0.0.0:5000`
  - visualiser l'API -> ``INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)``
  - visualiser le tableau de bord Streamlit -> 
  
  ```bash
  You can now view your Streamlit app in your browser.

  URL: http://0.0.0.0:8501`
  ```



## :toolbox: Dépannage rapide

| Erreur                        | Cause probable                   | Solution                                    |
| ----------------------------- | -------------------------------- | ------------------------------------------- |
| 500                           | Mauvais chemin vers le modèle    | Vérifier `joblib.load()`                    |
| 422                           | JSON invalide                    | Corriger les clés/types du payload          |
| CatBoostError                 | Valeurs "Oui/Non" au lieu de 0/1 | Convertir avant envoi                       |
| Could not import module "app" | Mauvais répertoire               | Exécuter dans le dossier contenant `app.py` |

## :compass: Roadmap

- [x] Analyse exploratoire et nettoyage

- [x] Modélisation CatBoost

- [x] Suivi des expérimentations MLflow

- [x] Déploiement API FastAPI

- [x] Interface Streamlit

- [x] Déploiement final sur Hugging Face

- [x] Déploiement Docker

- [ ] Déploiement via Docker Compose

## :busts_in_silhouette: Auteurs

Projet développé par [Nadège Lefort](https://github.com/nlefort)

*La réalisation de ce projet s'inscrit dans le cadre de la [formation Data Scientist](https://www.jedha.co/formations/formation-data-scientist) développé par [Jedha](https://www.jedha.co/), en vue de l'obtention de la certification professionnelle de niveau 6 (bac+4) enregistrée au RNCP : [Concepteur développeur en science des données](https://www.francecompetences.fr/recherche/rncp/35288/).*
