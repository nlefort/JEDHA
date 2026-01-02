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
# Définir le chemin absolu du modèle

# Chemins vers les artefacts
MODEL_DIR = os.getenv("MODEL_DIR", "/app/model")

try:
    model = joblib.load(os.path.join(MODEL_DIR, 'model_auto.pkl'))
    scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
    target_map = joblib.load(os.path.join(MODEL_DIR, 'target_encoding.pkl'))
    print(" Modèle, Scaler et Target Map chargés avec succès.")
except Exception as e:
    print(f" Erreur lors du chargement des artefacts : {e}")

# Vérification
print("Modèle chargé avec succès :", MODEL_DIR)

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
    print("Démarrage de l'API ...")
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(BASE_DIR, 'data', 'fraudTest_random.csv')
    
    print(f"Tentative de chargement : {dataset_path}")

    if os.path.exists(dataset_path):
        state.load_dataset(dataset_path)
    else:
        print("Aucun CSV de simulation trouvé — API lancée sans dataset")

    print("API prête à recevoir des requêtes")


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

@app.get("/payments", response_model=PaymentResponse)
async def get_payments(
    limit: int = 10,
    include_fraud_label: bool = False
):
    if state.df is None:
        raise HTTPException(status_code=500, detail="Dataset non chargé")
    
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit doit être entre 1 et 100")
    
    # Variation de la taille du batch (simule le flux réel)
    actual_limit = random.randint(max(1, limit // 2), min(100, limit * 3 // 2))
    
    # Récupération du batch dans le dataframe
    end_index = min(state.current_index + actual_limit, len(state.df))
    batch = state.df.iloc[state.current_index:end_index].copy()
    
    # Boucle de l'index
    if end_index >= len(state.df):
        state.current_index = 0
    else:
        state.current_index = end_index
    
    payments = []
    for _, row in batch.iterrows():
        # On convertit la ligne du DF en dictionnaire
        row_dict = row.to_dict()
        
        # Gestion du label de fraude (masqué par défaut pour le client de l'API)
        if not include_fraud_label:
            row_dict['is_fraud'] = 0 
            
        # Création de l'objet Payment en utilisant le dictionnaire de la ligne
        # **row_dict passe automatiquement toutes les colonnes (amt, lat, long, category...)
        try:
            payment = Payment(**row_dict)
            payments.append(payment)
        except Exception as e:
            print(f"Erreur de mapping sur une ligne : {e}")
            continue
    
    state.total_calls += 1
    
    return PaymentResponse(
        status="success",
        count=len(payments),
        timestamp=datetime.now().isoformat(),
        payments=payments
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérifie le status de l'API"""
    if state.df is None:
        raise HTTPException(status_code=503, detail="Dataset non chargé")
    
    return HealthResponse(
        status="healthy",
        total_transactions=len(state.df),
        current_index=state.current_index,
        api_version="1.0.0"
    )

@app.get("/stats", response_model=dict)
async def get_stats():
    """Statistiques de l'API"""
    if state.df is None:
        raise HTTPException(status_code=500, detail="Dataset non chargé")
    
    fraud_count = state.df['is_fraud'].sum() if 'is_fraud' in state.df.columns else 0
    
    return {
        "total_transactions": len(state.df),
        "fraud_transactions": int(fraud_count),
        "fraud_rate": f"{(fraud_count / len(state.df) * 100):.2f}%",
        "current_index": state.current_index,
        "total_api_calls": state.total_calls,
        "progress": f"{(state.current_index / len(state.df) * 100):.1f}%"
    }

@app.post("/predict", response_model=dict)
def predict_fraude(data: Payment):
    """Prédit si une transaction est frauduleuse ou non"""
    try:
        # 1. Préparation de la catégorie (Target Encoding)
        # On utilise la moyenne de fraude de l'entraînement comme fallback
        mean_fraud_rate = 0.002  # À ajuster selon tes logs d'entraînement
        category_enc = target_map.get(data.category, mean_fraud_rate)
        
        # 2. Création du DataFrame avec l'ordre EXACT des colonnes de l'entraînement
        # L'ordre doit être : amt, zip, city_pop, distance_km, gender_m, hour, weekday, category_enc
        input_df = pd.DataFrame([[
            data.amt, 
            data.zip, 
            data.city_pop, 
            data.distance_km, 
            data.gender_m, 
            data.hour, 
            data.weekday,
            category_enc
        ]], columns=["amt", "zip", "city_pop", "distance_km", "gender_m", "Hour", "Weekday", "category_enc"])
        
        # 3. Standardisation
        num_features = ["amt", "zip", "city_pop", "distance_km", "Hour", "Weekday"]
        input_df[num_features] = scaler.transform(input_df[num_features])
        
        # 4. Prédiction
        prob = float(model.predict_proba(input_df)[0][1])
        prediction = 1 if prob >= 0.50 else 0 # Seuil utilisé dans ton test
        
        return {
            "is_fraud": prediction,
            "probability": f"{prob:.2%}",
            "verdict": "ALERTE FRAUDE" if prediction == 1 else "TRANSACTION OK"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur: {str(e)}")

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