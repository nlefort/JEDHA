"""
DAG Airflow - Détection de Fraude (Version Certification)
==========================================================
Pipeline ETL simple pour la certification :
1. Récupère les paiements de l'API
2. Prédit les fraudes
3. Stocke dans SQLite
4. Génère un rapport quotidien (optionnel)
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import pandas as pd
import sqlite3
import joblib
import os
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
# Chemin du projet (adapter selon votre environnement)
PROJECT_ROOT = Path(__file__).parent.parent.parent
API_URL = "http://localhost:8000/payments"
DB_PATH = PROJECT_ROOT / "database" / "fraud_data.db"
MODEL_DIR = PROJECT_ROOT / "model"

# ==========================================
# FONCTION 1 : Récupérer les paiements
# ==========================================
def fetch_payments(**context):
    """
    Récupère les paiements depuis l'API FastAPI
    """
    try:
        print("Récupération des paiements depuis l'API...")
        
        response = requests.get(
            API_URL, 
            params={'limit': 20},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        payments = data.get('payments', [])
        
        print(f"{len(payments)} paiements récupérés")
        
        # Stocker dans XCom pour la tâche suivante
        context['ti'].xcom_push(key='payments', value=payments)
        
        return len(payments)
    
    except Exception as e:
        print(f"Erreur : {e}")
        return 0

# ==========================================
# FONCTION 2 : Prédire les fraudes
# ==========================================
def predict_fraud(**context):
    """
    Applique le modèle ML sur les paiements
    """
    try:
        # Récupérer les paiements depuis XCom
        payments = context['ti'].xcom_pull(
            key='payments', 
            task_ids='fetch_payments'
        )
        
        if not payments or len(payments) == 0:
            print("Aucun paiement à traiter")
            return 0
        
        print(f"Traitement de {len(payments)} paiements...")
        
        # Charger le modèle et les transformers
        model = joblib.load(MODEL_DIR / "model_auto.pkl")
        scaler = joblib.load(MODEL_DIR / "scaler.pkl")
        target_map = joblib.load(MODEL_DIR / "target_encoding.pkl")
        
        # Convertir en DataFrame
        df = pd.DataFrame(payments)
        
        # SIMPLIFICATION : On suppose que l'API renvoie déjà les features
        # Dans un vrai projet, vous feriez le feature engineering ici
        
        # Features attendues par le modèle
        features = ['amt', 'zip', 'city_pop', 'distance_km', 
                   'category_enc', 'gender_m', 'Hour', 'Weekday']
        
        # Vérifier que les colonnes existent
        if not all(col in df.columns for col in features):
            print(" Colonnes manquantes dans les données")
            # Générer des valeurs par défaut pour la démo
            for col in features:
                if col not in df.columns:
                    df[col] = 0
        
        X = df[features].copy()
        
        # Standardisation des features numériques
        num_features = ['amt', 'zip', 'city_pop', 'distance_km', 'Hour', 'Weekday']
        X[num_features] = scaler.transform(X[num_features])
        
        # Prédiction
        df['fraud_probability'] = model.predict_proba(X)[:, 1]
        df['is_fraud_predicted'] = (df['fraud_probability'] >= 0.5).astype(int)
        
        # Compter les fraudes
        nb_frauds = df['is_fraud_predicted'].sum()
        print(f"{nb_frauds} fraudes détectées")
        
        # Stocker pour la tâche suivante
        context['ti'].xcom_push(key='predictions', value=df.to_dict('records'))
        
        return int(nb_frauds)
    
    except Exception as e:
        print(f"Erreur lors de la prédiction : {e}")
        import traceback
        traceback.print_exc()
        return 0

# ==========================================
# FONCTION 3 : Stocker dans la base
# ==========================================
def store_in_database(**context):
    """
    Stocke les résultats dans NeonDB (PostgreSQL)
    """
    try:
        predictions = context['ti'].xcom_pull(
            key='predictions', 
            task_ids='predict_fraud'
        )
        
        if not predictions:
            print("Aucune prédiction à stocker")
            return
        
        print(f"Stockage de {len(predictions)} transactions...")
        
        # Créer le dossier database si nécessaire
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Connexion SQLite
        conn = sqlite3.connect(DB_PATH)
        df = pd.DataFrame(predictions)

        # Ajouter timestamp de traitement
        df['processed_at'] = datetime.now().isoformat()
        
        # Stocker (append si la table existe déjà)
        df.to_sql(
            'transactions', 
            conn, 
            if_exists='append', 
            index=False
        )
        
        print(f"{len(df)} transactions stockées")
        
        # Compter le nombre total de transactions
        total = pd.read_sql("SELECT COUNT(*) as count FROM transactions", conn)
        print(f"Total en base : {total['count'].iloc[0]} transactions")
        
        conn.close()
        
    except Exception as e:
        print(f"Erreur lors du stockage : {e}")
        import traceback
        traceback.print_exc()

# ==========================================
# FONCTION 4 : Générer un rapport (bonus)
# ==========================================
def generate_daily_report(**context):
    """
    Génère un rapport quotidien simple
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Statistiques des dernières 24h
        query = """
        SELECT 
            COUNT(*) as total_transactions,
            SUM(is_fraud_predicted) as nb_fraudes,
            AVG(fraud_probability) as proba_moyenne,
            MAX(processed_at) as derniere_maj
        FROM transactions
        WHERE processed_at >= datetime('now', '-1 day')
        """
        
        stats = pd.read_sql(query, conn)
        
        print("\n" + "="*60)
        print("RAPPORT QUOTIDIEN")
        print("="*60)
        print(f"Transactions traitées : {stats['total_transactions'].iloc[0]}")
        print(f"Fraudes détectées     : {stats['nb_fraudes'].iloc[0]}")
        print(f"Probabilité moyenne   : {stats['proba_moyenne'].iloc[0]:.2%}")
        print(f"Dernière MAJ          : {stats['derniere_maj'].iloc[0]}")
        print("="*60 + "\n")
        
        conn.close()
        
    except Exception as e:
        print(f"Impossible de générer le rapport : {e}")

# ==========================================
# DÉFINITION DU DAG
# ==========================================
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 7),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    'fraud_detection_simple',
    default_args=default_args,
    description='Pipeline ETL de détection de fraude (Certification)',
    schedule_interval='*/5 * * * *',  # Toutes les 5 minutes
    catchup=False,
    tags=['fraud', 'ml', 'certification'],
)

# ==========================================
# DÉFINITION DES TÂCHES
# ==========================================

# Tâche 1 : Récupérer les paiements
task_fetch = PythonOperator(
    task_id='fetch_payments',
    python_callable=fetch_payments,
    dag=dag,
)

# Tâche 2 : Prédire les fraudes
task_predict = PythonOperator(
    task_id='predict_fraud',
    python_callable=predict_fraud,
    dag=dag,
)

# Tâche 3 : Stocker dans la DB
task_store = PythonOperator(
    task_id='store_in_db',
    python_callable=store_in_database,
    dag=dag,
)

# Tâche 4 : Rapport quotidien (optionnel)
task_report = PythonOperator(
    task_id='daily_report',
    python_callable=generate_daily_report,
    dag=dag,
)

# ==========================================
# DÉFINITION DU FLUX
# ==========================================
# Flux linéaire simple pour la certification
task_fetch >> task_predict >> task_store >> task_report

# Signification :
# 1. Fetch payments (API)
# 2. Predict fraud (ML)
# 3. Store in DB (SQLite)
# 4. Generate report (Stats)