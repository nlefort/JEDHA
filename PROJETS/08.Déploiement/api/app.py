# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import os

# ----------------------------
# 1. Initialisation FastAPI
# ----------------------------
app = FastAPI(
    title="GetAround Price Prediction API",
    description="API pour prédire le prix de location d'un véhicule à partir de ses caractéristiques",
    version="1.0.0",
    author="Nadège Lefort"
)

# ----------------------------
# 2. Chargement du modèle
# ----------------------------
# model = joblib.load("D:/Profils/NLefort/Desktop/JEDHA/PROJETS/08.Déploiement/api/model_auto.pkl") --> ne va pas fonctionner avec Docker

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model_auto.pkl")
model = joblib.load(MODEL_PATH)

# ----------------------------
# 3. Schéma d'entrée
# ----------------------------
class CarInput(BaseModel):
    model_key: str
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: int | str | bool
    has_gps: int | str | bool
    has_air_conditioning: int | str | bool
    automatic_car: int | str | bool
    has_getaround_connect: int | str | bool
    has_speed_regulator: int | str | bool
    winter_tires: int | str | bool
    mileage: int
    engine_power: int

# =========================
# 4. Fonction de nettoyage des entrées
# =========================

def preprocess_input(car: CarInput):
    data = car.model_dump()

    # Conversion Oui/Non ou True/False → 1/0
    def normalize_bool(value):
        if isinstance(value, str):
            value = value.strip().lower()
            if value in ["oui", "yes", "true", "1"]:
                return 1
            elif value in ["non", "no", "false", "0"]:
                return 0
        elif isinstance(value, bool):
            return int(value)
        elif isinstance(value, (int, float)):
            return int(value)
        return 0  # valeur par défaut

    bool_fields = [
        'private_parking_available',
        'has_gps',
        'has_air_conditioning',
        'automatic_car',
        'has_getaround_connect',
        'has_speed_regulator',
        'winter_tires'
    ]

    for field in bool_fields:
        data[field] = normalize_bool(data[field])

    return pd.DataFrame([data])

# ----------------------------
# 5. Endpoints
# ----------------------------
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de prédiction GetAround! - Rendez-vous sur /docs pour la documentation."}

@app.get("/health")
def health_check():
    """
    Vérifie l'état de santé du modèle et de l'API.
    """
    expected_features = [
        'model_key', 'fuel', 'paint_color', 'car_type',
        'private_parking_available', 'has_gps', 'has_air_conditioning',
        'automatic_car', 'has_getaround_connect', 'has_speed_regulator',
        'winter_tires', 'mileage', 'engine_power'
    ]

    status = {
        "api_status": "OK",
        "model_loaded": model,
        "expected_features": expected_features
    }

    return status


# ----------------------------
# 5.1 Endpoint de prédiction
# ----------------------------
@app.post("/predict")
def predict_price(car: CarInput):
    """ Reçoit les craractéristiques d'une voiture et retourne la prédiction de prix avec intervalle +/-10%. """
    try:
        # Prétraitement des entrées
        input_df = preprocess_input(car)
        # Prédiction
        pred = model.predict(input_df)[0]
        # Calcul intervalle +/- 10%
        interval = 0.1
        low = pred * (1 - interval)
        high = pred * (1 + interval)
        return {
            "prediction": round(pred, 2),
            "interval": [round(low, 2), round(high, 2)]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ----------------------------
# /docs est automatiquement disponible
# ----------------------------

# =========================
# Démarrage : uvicorn app:app --reload
# =========================