# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

# ----------------------------
# 1. Initialisation FastAPI
# ----------------------------
app = FastAPI(
    title="GetAround Price Prediction API",
    description="API pour prédire le prix de location d'un véhicule à partir de ses caractéristiques",
    version="1.0.0"
)

# ----------------------------
# 2. Chargement du modèle
# ----------------------------
model = joblib.load("D:/Profils/NLefort/Desktop/JEDHA/PROJETS/08.Déploiement/api/model_auto.pkl")

# ----------------------------
# 3. Schéma d'entrée
# ----------------------------
class VehicleData(BaseModel):
    model_key: str
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: int
    has_gps: int
    has_air_conditioning: int
    automatic_car: int
    has_getaround_connect: int
    has_speed_regulator: int
    winter_tires: int
    mileage: int
    engine_power: int

# ----------------------------
# 4. Endpoint d'accueil
# ----------------------------
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de prédiction GetAround!"}

# ----------------------------
# 5. Endpoint de prédiction
# ----------------------------
@app.post("/predict")
def predict(vehicle: VehicleData):
    try:
        # Conversion du Pydantic model en DataFrame
        input_df = pd.DataFrame([vehicle.dict()])
        # Prédiction
        pred = model.predict(input_df)[0]
        # Optionnel : retourner une fourchette ±10%
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