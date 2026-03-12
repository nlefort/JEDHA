"""
DAG Airflow - Détection de Fraude
==========================================================
Pipeline ETL simple pour la certification :
1. Récupère les paiements de l'API
2. Prédit les fraudes
3. Stocke dans SQLite
4. Génère un rapport quotidien (optionnel)
"""

from airflow.decorators import dag, task
from datetime import datetime
import pandas as pd
import numpy as np
import sqlite3
import requests
import joblib
import os
import json
import xgboost as xgb

# ==========================================
# CONFIGURATION
# ==========================================
# Chemin du projet (adapter selon votre environnement)
# Configuration simplifiée
DB_PATH = "/opt/airflow/data/fraud_predictions.db"
MODEL_DIR = "/opt/airflow/data/model"
os.makedirs(MODEL_DIR, exist_ok=True)

# Planificiation du DAG
@dag(
    schedule_interval='*/5 * * * *',
    start_date=datetime(2026, 1, 7),
    catchup=False,
    tags=['fraud', 'ML', 'prediction']
)

# ==========================================
# FONCTION : Récupérer les paiements > prédire les fraudes > stocker le résulat > faire un rapport
# ==========================================
def fraud_detection_pipeline():

    @task
    def fetch_payments():
        # 'api' : est le nom du service dans docker-compose
        #r = requests.get("http://api:8000/payments?limit=20")
        URL_ECOLE = "https://sdacelo-real-time-fraud-detection.hf.space/current-transactions"

        r = requests.get(URL_ECOLE, timeout=10)
        r.raise_for_status()
        raw_data = r.json()
        
        # L'API renvoie une string JSON, on la décode en dictionnaire
        raw_data = r.json()
        if isinstance(raw_data, str):
            raw_data = json.loads(raw_data)
            
        return raw_data

    @task
    def predict_fraud(raw_json):
        import mlflow

    # 1. Configuration de la connexion
        mlflow.set_tracking_uri("http://172.18.0.1:5000")
        mlflow.set_experiment("Fraud_Detection_XGBoost")

        # 1. Reconstruction du DataFrame depuis le format split de l'API
        df = pd.DataFrame(data=raw_json['data'], columns=raw_json['columns'])
        
        # 2. Feature Engineering (Distance & Temps)
        def haversine(lat1, lon1, lat2, lon2):
            r = 6371
            phi1, phi2 = np.radians(lat1), np.radians(lat2)
            a = np.sin(np.radians(lat2-lat1)/2)**2 + \
                np.cos(phi1)*np.cos(phi2)*np.sin(np.radians(lon2-lon1)/2)**2
            return 2 * r * np.arcsin(np.sqrt(a))

        df['distance_km'] = haversine(df['lat'], df['long'], df['merch_lat'], df['merch_long'])
        
        # Extraction de l'heure et du jour (basé sur le timestamp current_time de l'API)
        # Note: current_time semble être en secondes
        dt_object = pd.to_datetime(df['current_time'], unit='ms')
        df['Hour'] = dt_object.dt.hour
        df['Weekday'] = dt_object.dt.weekday
        
        # 3. Encodages (Gender & Category)
        df['gender_m'] = df['gender'].map({'M': 1, 'F': 0}).fillna(0)
        
        target_map = joblib.load("/opt/airflow/data/model/target_encoding.pkl")
        # On utilise la moyenne de fraude du train (0.0052 approx) si catégorie inconnue
        df['category_enc'] = df['category'].map(target_map).fillna(0.0052)

        # 4. Préparation finale (Ordre strict des colonnes)
        features_list = ["amt", "zip", "city_pop", "distance_km", "gender_m", "Hour", "Weekday", "category_enc"]
        X = df[features_list].copy()

        # 5. Scaling et Prédiction
        scaler = joblib.load("/opt/airflow/data/model/scaler.pkl")
        model = joblib.load("/opt/airflow/data/model/model_auto.pkl")
        
        num_features = ["amt", "zip", "city_pop", "distance_km", "Hour", "Weekday"]
        X[num_features] = scaler.transform(X[num_features])
        
        # Prédiction
        df['is_fraud'] = model.predict(X)

        # 2. Enregistrement du passage dans MLflow
        with mlflow.start_run(run_name=f"Airflow_Run_{datetime.now().strftime('%H:%M')}"):
            
            # Ton code de prédiction existant
            df['is_fraud'] = model.predict(X)

            # On logue les résultats du batch actuel
            mlflow.log_metric("batch_size", len(df))
            # À l'intérieur de ton run MLflow
            nb_frauds = int(df['is_fraud'].sum()) # <--- Force le type int
            mlflow.log_metric("frauds_found", nb_frauds)

            
            # Optionnel : on récupère le run_id pour l'historique
            run_id = mlflow.active_run().info.run_id
            df['mlflow_run_id'] = run_id

        
        return df.to_dict('records')

    @task
    def store_data(predictions):
        df = pd.DataFrame(predictions)
        conn = sqlite3.connect(DB_PATH)
        df.to_sql('transactions', conn, if_exists='append', index=False)
        count = len(df)
        conn.close()
        return f"{count} transactions enregistrées"

    @task
    def daily_report():
        conn = sqlite3.connect(DB_PATH)
        # Petit check pour éviter que le rapport plante si la table n'existe pas encore
        try:
            df = pd.read_sql("SELECT COUNT(*) as total, SUM(is_fraud) as frauds FROM transactions", conn)
            print(f"RESUMÉ : {df.total[0]} total, {df.frauds[0]} fraudes.")
        except:
            print("Pas encore de données pour le rapport.")
        finally:
            conn.close()

    # Flux de données limpide
    data = fetch_payments()
    preds = predict_fraud(data)
    store_data(preds) >> daily_report()

# Instanciation
fraud_detection_pipeline()


# ==========================================
# DÉFINITION DU FLUX
# ==========================================
# Flux linéaire simple
# fetch_payments >> predict_fraud >> store_data >> daily_report

# Signification :
# 1. Fetch payments (API)
# 2. Predict fraud (ML)
# 3. Store in DB (SQLite)
# 4. Generate report (Stats)