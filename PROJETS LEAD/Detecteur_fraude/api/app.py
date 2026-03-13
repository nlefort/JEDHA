from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import pandas as pd
import random
import uvicorn
import pickle
import os
import numpy as np
import joblib
import requests
import sqlite3

# ----------------------------
# 1. Initialisation FastAPI
# ----------------------------
app = FastAPI(
    title="API détection de fraude",
    description="API de simulation de paiements en temps réel pour détection de fraude",
    version="1.0.0"
)

# ----------------------------
# 2. Chargement du modèle
# ----------------------------
RESULTS_DB = "/app/database/fraud_predictions.db"
MODEL_DIR = os.getenv("MODEL_DIR", "/app/data/model")

# 1. Initialisation sécurisée (on évite le None)
model = None
scaler = None
target_map = {} # On met un dictionnaire vide par défaut

try:
    # 2. Chargement du modèle
    model_path = os.path.join(MODEL_DIR, 'model_auto.pkl')
    model = joblib.load(model_path)
    
    # FIX XGBOOST : On supprime l'attribut qui fâche si l'objet le possède
    if model is not None and hasattr(model, 'use_label_encoder'):
        try:
            delattr(model, 'use_label_encoder')
        except:
            pass

    # 3. Chargement du scaler
    scaler_path = os.path.join(MODEL_DIR, 'scaler.pkl')
    scaler = joblib.load(scaler_path)

    # 4. Chargement du target_map
    encoding_path = os.path.join(MODEL_DIR, 'target_encoding.pkl')
    target_map = joblib.load(encoding_path)
    
    print("Tous les artefacts ont été chargés et nettoyés.")

except Exception as e:
    # Si ça rate, l'API ne crash pas ici, elle affichera l'erreur dans les logs
    print(f"Erreur critique lors du chargement : {e}")

# Vérification finale dans les logs Docker
if target_map == {}:
    print("Attention : target_map est vide, vérifiez le chemin des fichiers !")

# ----------------------------
# 3. Schéma d'entrée
# ----------------------------
class Payment(BaseModel):
    """Modèle d'un paiement"""
    amt: float
    zip: int
    city_pop: int
    distance_km : float
    category: str
    gender_m: int
    hour: int
    weekday: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "amt": 123.45,
                "zip": "12345",
                "city_pop": 50000,
                "distance_km": 12.34,
                "category": "grocery_pos",
                "gender_m": 1,
                "hour": 14,
                "weekday": 2
            }
        }

class PaymentResponse(BaseModel):
    """Réponse de l'API"""
    status: str
    count: int
    timestamp: str
    payments: List[Payment]

class HealthResponse(BaseModel):
    """Réponse du health check"""
    status: str
    total_transactions: int
    current_index: int
    api_version: str

# =========================
# 4. Fonction de simulation de données entrantes
# =========================

class APIState:
    """Gestion de l'état de l'API"""
    def __init__(self):
        self.df = None
        self.current_index = 0
        self.total_calls = 0
        
    def load_dataset(self, filepath: str):
        """Charge le dataset de fraudes"""
        if not os.path.exists(filepath):
            print(f"ERREUR : Le fichier est introuvable au chemin : {filepath}")
            return
        try:
            self.df = pd.read_csv(filepath)
            print(f"Dataset chargé avec succès : {len(self.df)} transactions")
        except Exception as e:
            print(f"Erreur lors de la lecture du CSV : {e}")
 
# Initialisation
state = APIState()

# =========================
# 4.1 Lancement de l'API
# =========================

@app.on_event("startup")   
async def startup_event():
    print("Démarrage de l'API en mode DYNAMIQUE (Utilisation de FakerAPI)...")

    print("API prête à recevoir des requêtes sur /payments")


# ----------------------------
# 5. Endpoints
# ----------------------------
@app.get("/", response_model=dict)
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Payment Stream API",
        "version": "1.0.0",
        "endpoints": {
            "payments": "/payments - Récupère un batch de paiements",
            "health": "/health - Status de l'API",
            "docs": "/docs - Documentation interactive",
            "prediction fraude": "/predict - Prédire si une transaction est frauduleuse ou non"
        }
    }

@app.get("/payments")
async def get_payments(limit: int = 10):
    """
    Récupère des données de FakerAPI et les adapte.
    Si FakerAPI est HS, on génère des données aléatoires propres.
    """
    try:
        # 1. Tentative d'appel à FakerAPI pour les données de base (Nom, Carte, etc.)
        faker_url = f"https://fakerapi.it/api/v1/credit_cards?_quantity={limit}"
        response = requests.get(faker_url, timeout=5)
        
        # Si FakerAPI répond bien
        if response.status_code == 200:
            raw_data = response.json().get('data', [])
        else:
            raw_data = range(limit) # Fallback si l'API externe répond mal

        # 2. On construit les features attendues par ton modèle ML
        processed_data = []
        for _ in raw_data:
            processed_data.append({
                "amt": round(random.uniform(5.0, 1200.0), 2),
                "zip": random.randint(10000, 99999),
                "city_pop": random.randint(500, 1000000),
                "distance_km": round(random.uniform(0.1, 150.0), 2),
                "category": random.choice(["grocery_pos", "entertainment", "shopping_net", "gas_transport"]),
                "gender_m": random.choice([0, 1]),
                "hour": datetime.now().hour,
                "weekday": datetime.now().weekday()
            })
            
        return {"status": "success", "data": processed_data}

    except Exception as e:
        # En cas de gros bug, on renvoie une erreur JSON propre au lieu d'un 502
        raise HTTPException(status_code=502, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "api_version": "1.0.0"
    }


@app.post("/predict")
def predict_fraude(data: Payment):
    """Prédit si une transaction est frauduleuse ou non"""
    try:
        # 1. Target Encoding (cohérent avec ton entraînement)
        # On utilise .get() pour éviter le KeyError si la catégorie est nouvelle
        category_enc = target_map.get(data.category, 0.002) 
        
        # 2. Création du DataFrame avec les noms de colonnes EXACTS du train_model
        # Attention : 'Hour' et 'Weekday' doivent avoir une majuscule !
        input_data = {
            "amt": [data.amt],
            "zip": [data.zip],
            "city_pop": [data.city_pop],
            "distance_km": [data.distance_km],
            "gender_m": [data.gender_m],
            "Hour": [data.hour],       # On mappe 'hour' vers 'Hour'
            "Weekday": [data.weekday], # On mappe 'weekday' vers 'Weekday'
            "category_enc": [category_enc]
        }
        input_df = pd.DataFrame(input_data)
        
        # 3. Réorganiser les colonnes dans l'ordre exact du modèle
        features_list = ["amt", "zip", "city_pop", "distance_km", "gender_m", "Hour", "Weekday", "category_enc"]
        input_df = input_df[features_list]

        # 4. Standardisation (uniquement sur les colonnes numériques)
        num_features = ["amt", "zip", "city_pop", "distance_km", "Hour", "Weekday"]
        input_df[num_features] = scaler.transform(input_df[num_features])
        
        # 5. Prédiction
        prob = float(model.predict_proba(input_df)[0][1])
        prediction = 1 if prob >= 0.50 else 0 
        
        return {
            "is_fraud": prediction,
            "probability": f"{prob:.2%}",
            "verdict": "ALERTE FRAUDE" if prediction == 1 else "TRANSACTION OK"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur: {str(e)}")

@app.get("/results")
def get_results():
    try:
        if not os.path.exists(RESULTS_DB):
            return {"status": "error", "message": f"Base de données introuvable à {RESULTS_DB}"}
            
        conn = sqlite3.connect(RESULTS_DB)
        # On récupère les 20 dernières transactions
        df = pd.read_sql("SELECT * FROM transactions ORDER BY processed_at DESC LIMIT 20", conn)
        conn.close()
        
        return {
            "status": "success",
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------------
# 6. Endpoints
# ----------------------------

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMARRAGE DE L'API DE DÉTECTION DE FRAUDE ")
    print("=" * 60)
    print("URL: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("Test: curl http://localhost:8000/payments?limit=5")
    print("=" * 60)
    
    uvicorn.run(
        "api:app", 
        host="127.0.0.1",
        port=8000,
        reload=True  # Auto-reload pendant le développement
    )

# ----------------------------
# /docs est automatiquement disponible
# ----------------------------

# =========================
# Démarrage : uvicorn app:app --reload
# ========================= 