# :dart: Déploiement d'une API de prédiction de prix

## :rocket: Objectif du projet

L'objectif de ce projet est de déployer une API  :

## :brain: Pipeline de traitement

La collecte et le traitement des données suivante la progression suivante :

```text
Import des données 
↓
Analyse exploratoire (EDA) et statistiques descriptives
↓
Prétraitement des données (gestion des NaN, conversion des dates, suppression des outliers)
↓
Création d'un modèle de régression linéaire de référence
↓
Évaluation et interprétation des coefficients du modèle
↓

↓

↓

```

| Étape            | Commande                         | Description                    |
| ---------------- | -------------------------------- | ------------------------------ |
| Entraînement | `python train_model.py`          | Enregistre modèle + run MLflow |
| Suivi MLflow | `mlflow ui`                      | Ouvre ton tableau de bord      |
| API          | `uvicorn api.app:app --reload`   | Démarre ton service local      |
| Dashboard    | `streamlit run streamlit/app.py` | Teste ton front Streamlit      |
| Déploiement  | Docker, Hugging Face           | Met tout en ligne          |


## :wheel: Technologies & outils

| Domaine    | Outils                   |
| ---------- | ---------|
| Exploitation et visualisation des données | Pandas, NumPy, Seaborn, Matplotlib, Plotly |
| Apprentissage automatique supervisé | Scikit-learn, LinearRegression, Ridge, Lasso, GridSearchCV, KFold |

## Méthodes de l'API

| Endpoint | Méthode | Description |
| -------- | ------- | ----------- |
| / | GET | Message d’accueil |
| /health | GET | Vérifie si l’API et le modèle fonctionnent |
| /predict | POST | Prend un JSON et renvoie une prédiction |
| /docs | GET| Interface Swagger pour tester visuellement |

## :compass: Roadmap

- [x]

- [x]

- [x]

- [x]

- [x]

- [x]

- [x] uvicorn app:app --reload

## :arrow_forward: Installation, exécution, tutlisation

### 0. Prérequis

Python 3.x

### 1. Lancer le notebook

Depuis votre IDE préféré, lancer le notebook

## :busts_in_silhouette: Auteurs

Projet développé par [Nadège Lefort](https://github.com/nlefort)

*La réalisation de ce projet s'inscrit dans le cadre de la [formation Data Scientist](https://www.jedha.co/formations/formation-data-scientist) développé par [Jedha](https://www.jedha.co/), en vue de l'obtention de la certification professionnelle de niveau 6 (bac+4) enregistrée au RNCP : [Concepteur développeur en science des données](https://www.francecompetences.fr/recherche/rncp/35288/).*

0 ) Préparations rapides (une seule fois)

Ouvrir PowerShell et se placer dans le dossier de ton API :

cd "D:\Profils\NLefort\Desktop\JEDHA\PROJETS\08.Déploiement\api"

Activer l'environnement si besoin (conda)
conda activate base

Vérifier que les dépendances sont installées :
pip install fastapi uvicorn joblib pandas catboost requests
(les paquets déjà installés apparaîtront comme « Requirement already satisfied »)

1) Lancer le serveur (uvicorn)
Dans le dossier contenant app.py, lancer :
uvicorn app:app --reload

Explications :
app:app → module:app_object (ton fichier app.py doit définir app = FastAPI()).
--reload redémarre automatiquement quand tu modifies app.py (utile en dev).

Ce que je dois voir dans le terminal

Messages d’info uvicorn, par ex :

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Application startup complete.

Si une erreur d’import apparaît (Could not import module "app"), vérifier que je suis dans le bon dossier et que le fichier s’appelle bien app.py.

2 ) Vérifier l’API dans le navigateur

Ouvrir le navigateur :
http://127.0.0.1:8000/ → je dois voir le JSON d’accueil ({"message":"Bienvenue ..."}).
http://127.0.0.1:8000/docs → Swagger UI interactif (documentation auto).

je peux tester /predict directement dans l’interface (bouton Try it out).

3 ) Tester /predict depuis le terminal (curl) — exemple

Si je veux tester sans navigateur, en PowerShell (curl ou Invoke-RestMethod) :

Exemple JSON complet attendu (adapté au schéma CarInput déjà défini) :

{
  "model_key": "citroen_c3",
  "fuel": "diesel",
  "paint_color": "noir",
  "car_type": "compact",
  "private_parking_available": 1,
  "has_gps": 1,
  "has_air_conditioning": 0,
  "automatic_car": 0,
  "has_getaround_connect": 1,
  "has_speed_regulator": 0,
  "winter_tires": 0,
  "mileage": 50000,
  "engine_power": 110
}

Commande curl (PowerShell) :

curl -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" -d "{\"model_key\":\"citroen_c3\",\"fuel\":\"diesel\",\"paint_color\":\"noir\",\"car_type\":\"compact\",\"private_parking_available\":1,\"has_gps\":1,\"has_air_conditioning\":0,\"automatic_car\":0,\"has_getaround_connect\":1,\"has_speed_regulator\":0,\"winter_tires\":0,\"mileage\":50000,\"engine_power\":110}"

Réponse attendue (exemple) :

{"prediction":141.17,"interval":[127.06,155.29]}

4 ) Tester /predict depuis Python (script test.py)

Crée un fichier test.py dans le même dossier avec ce contenu :

import requests

url = "http://127.0.0.1:8000/predict"
data = {
  "model_key": "citroen_c3",
  "fuel": "diesel",
  "paint_color": "noir",
  "car_type": "compact",
  "private_parking_available": 1,
  "has_gps": 1,
  "has_air_conditioning": 0,
  "automatic_car": 0,
  "has_getaround_connect": 1,
  "has_speed_regulator": 0,
  "winter_tires": 0,
  "mileage": 50000,
  "engine_power": 110
}

resp = requests.post(url, json=data)
print(resp.status_code)
print(resp.json())

Puis lancer :

python test.py

Je dois voir :

200
{'prediction': 141.17, 'interval': [127.06, 155.29]}

5 ) Erreurs fréquentes et corrections rapides

500 / erreur serveur : regarde les logs dans la console uvicorn — il affichera la trace. Probable cause : modèle introuvable (mauvais chemin) ou données d’entrée mal typées.

Solution : vérifier chemin du joblib.load("...model.pkl").

422 Unprocessable Entity (Pydantic validation) : la requête JSON ne contient pas les champs attendus ou types incorrects.

Solution : envoyer les mêmes clés et types que ton BaseModel (voir JSON d’exemple).

CatBoostError: Cannot convert 'Non' to float : tu as passé "Oui"/"Non" au lieu de 1/0 ou types attendus.

Solution : préparer et envoyer 0/1 pour les booléens ou adapter app.py pour effectuer la conversion avant prédiction.

Could not import module "app" : s'assurer que j'exécute uvicorn depuis le dossier contenant app.py et que app.py contient app = FastAPI().

6 ) Arrêter le serveur

Dans la console où uvicorn tourne, presser CTRL+C. :
INFO:     Shutting down
