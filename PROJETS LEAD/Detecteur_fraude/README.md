# :dart: Détecteur de fraude 

## :rocket: Objectifs du projet

Ce projet a pour but de détecter les paiements frauduleux en temps réel à l’aide de l’IA et de mettre en production un pipeline automatisé exploitable par plusieurs équipes.

Les objectifs principaux sont :

- Détecter les fraudes sur des transactions bancaires en temps réel
- Envoyer des notifications lorsqu’une fraude est détectée
- Générer des rapports quotidiens sur les transactions frauduleuses

## :brain: Flux global du projet

```ascii
         Appel API (FakerAPI)
            ↓
        Airflow DAG
     (ingestion / ETL)
            ↓
     Transformation des paiements
     et standardisation
            ↓
     Entraînement ML
      (MLflow tracking)
            ↓
      Modèles + métriques
            ↓
     API FastAPI → Prédictions
            ↓
      Stockage des résultats (SQLite)
            ↓      
      Monitoring / logs
```

## :building_construction: Architecture globale

### Composants

| Technologie | Rôle |
| ----------- | ---- |
| API FastAPI | Expose les endpoints pour récupérer les paiements et faire des prédictions |
| Airflow | Orchestration des tâches (récupération des paiements, prédiction, stockage) |
| MLflow | Suivi des expérimentations et gestion des modèles |
| SQLite | Stockage des transactions et résultats |
| Docker Compose | Environnement reproductible |
| GitHub | Stockage du code |

### Interactions entre les modules

```bash
Transactions >> API >> Airflow >> ML Model >> Résultats >> Stockage/Alertes/Reports

```

| Étape          | Module source | Module cible | Description               | Fichier clé                  |
| -------------- | ------------- | ------------ | ------------------------- | ---------------------------- |
| Configuration  | `.env`        | Airflow      | Variables d’environnement | `.env`                       |
| Orchestration  | Airflow DAG   | Airflow      | Définition du pipeline    | `/airflow/dags/*.py`         |
| Entraînement   | Model         | MLflow       | Training & métriques      | `model/train_model.py`       |
| Registry       | MLflow        | MLflow       | Versioning modèle         | MLflow UI                    |
| Serving        | FastAPI       | MLflow       | Chargement modèle prod    | `/api/app.py`                |

### Flux API de prédiction

- ``GET /payments`` : récupère un batch de paiements
- ``POST /predict`` : prédit la fraude sur une transaction
- ``GET /stats`` : affiche les statistiques des transactions traitées
- ``GET /health`` : vérifie l’état de l’API

### MLFlow

- **Interface Web** : ``http://localhost:5000``
- **Tracking URI (depuis les conteneurs)** : `http://mlflow:5000`
- **Tracking URI (depuis l'hôte)** : `http://localhost:5000`

MLFlow permet de :

- comparer les runs,
- analyser les métriques,
- gérer les versions,
- promouvoir un modèle de production

## :atom_symbol: Installation

Prérequis

- Docker
- Docker Compose

```bash
git clone https://github.com/nlefort/JEDHA/tree/main/PROJETS%20LEAD/Detecteur_fraude
cd Detection_fraude
```

Renseigner les variables nécessaires dans `.env`

### Générer les clés Airflow

```bash
# AIRFLOW_FERNET_KEY (chiffrement des secrets)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# AIRFLOW_WEBSERVER_SECRET_KEY (sessions web)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Exécution

1. Construire et démarrer les services Docker :

`docker compose up -d --build`

2. Initialiser Airflow :

```bash
docker compose run --rm airflow airflow db init
docker compose run --rm airflow airflow users create \
    --username admin --password admin \
    --firstname Admin --lastname User \
    --role Admin --email admin@example.com
```

### URLs des services

| Service | URL | Description |
| ------- | --- | ----------- |
| Airflow | http://localhost:8080 | Orchestration des pipelines (admin/admin) |
| MLflow | http://localhost:5000 | Tracking des expériences ML |
| API | http://localhost:8000 | API de prédiction |
| API Docs | http://localhost:8000/docs | Documentation Swagger |

### Utilisation

1. Lancer le DAG dans Airflow (Call API + training + stockage)
2. Vérifier les runs et métriques dans MLflow
3. Appeler l’API `/predict`

### Exemple de prédiction

Requête

```http
POST/predict
```

```json
curl -X POST "http://localhost:8000/predict" \
-H "Content-Type: application/json" \
-d '{
    "amt": 120.5,
    "zip": 75001,
    "city_pop": 21000,
    "distance_km": 12.5,
    "category": "shopping_net",
    "gender_m": 1,
    "hour": 14,
    "weekday": 3
}'

```

Réponse

```json
{
    "is_fraud": 0,
    "probability": "0.23%",
    "verdict": "TRANSACTION OK"
}

```

### Promouvoir un modèle en Production

1. Enregistrer le modèle via MLflow
2. Mettre à jour le modèle dans le dossier model/
3. Redémarrer le service API si nécessaire

## :test_tube: Tests & qualité

- Les DAGs Airflow doivent passer les tests d’intégrité (airflow dags test <dag_id> <date>)
- Les modèles ML sont évalués via des métriques classiques (Recall, Precision, F1-score)
- L’API FastAPI peut être testée avec pytest ou curl
- L'Exploration des données et les tests des modèles sont disponibles dans `notebooks/EDA.ipynb` et `notebooks/ML.ipynb`

## :mag: Dépannage

Airflow

- DAGs non visibles >> vérifier `AIRFLOW_HOME` et que `.env` est chargé
- Tâches bloquées >> logs dans Airflow UI (task instance logs)
- Scheduler pas démarré >> vérifier service `airflow-scheduler`

MLflow

- Runs absents >> vérifier que MLflow tracking URI est bien défini (`mlflow.set_tracking_uri`)
- MLflow innaccessible : vérifier que le port 5000 n'est pas occupé

FastAPI

- Erreur de prédiction >> logs API `docker-compose logs api`
- Routes non disponibles >> vérifier sur `/docs`

Docker

- Rebuild nécessaire >> `docker-compose build` pour forcer la reconstruction sans cache
- Conteneurs qui plantent >> `docker ps` pour surveiller la bonne mise en service des conteneurs

## :compass: Roadmap

- [x] Analyse exploratoire et nettoyage

- [x] Modélisation CatBoost

- [x] Suivi des expérimentations MLflow

- [x] Déploiement API FastAPI

- [x] Déploiement Docker Compose

- [x] Automatisation Airflow

- [ ] Monitoring

- [ ] CI/CD

## :busts_in_silhouette: Auteurs

Projet développé par [Nadège Lefort](https://github.com/nlefort)

*La réalisation de ce projet s'inscrit dans le cadre de la [formation Data Scientist](https://www.jedha.co/formations/formation-data-engineer) développé par [Jedha](https://www.jedha.co/), en vue de l'obtention de la certification professionnelle de niveau 7 (bac+7) enregistrée au RNCP : [Architecte en intelligence artificielle](https://www.francecompetences.fr/recherche/rncp/38777/).*
