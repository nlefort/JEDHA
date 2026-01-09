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
import sqlite3
import requests
import joblib
import os

# ==========================================
# CONFIGURATION
# ==========================================
# Chemin du projet (adapter selon votre environnement)
# Configuration simplifiée
DB_PATH = "/app/data/fraud_predictions.db"
MODEL_PATH = "/opt/airflow/dags/models/model_auto.pkl" # Placé dans les dags pour accès facile

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
        r = requests.get("http://api:8000/payments?limit=20")
        return r.json()["data"]

    @task
    def predict_fraud(payments):
        df = pd.DataFrame(payments)
        
        # Chargement des données
        model = joblib.load(MODEL_PATH)
        
        # On ne garde que les colonnes nécessaires
        features = ['amt', 'zip', 'city_pop', 'distance_km'] 
        X = df[features].fillna(0)
        
        df['is_fraud'] = model.predict(X)
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
        df = pd.read_sql("SELECT COUNT(*) as total, SUM(is_fraud) as frauds FROM transactions", conn)
        print(f"RESUMÉ : {df.total[0]} total, {df.frauds[0]} fraudes.")
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