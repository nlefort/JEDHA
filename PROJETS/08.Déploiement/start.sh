#!/bin/bash
set -e

echo "--- Démarrage des services Getaround (MLflow, FastAPI, Streamlit) ---"

# Lancement du Serveur MLflow (Port 5000) en arrière-plan
mlflow server \
    --host 0.0.0.0 \
    --port 5000 &

# Lancement de l'API FastAPI (Port 8000) en arrière-plan
uvicorn api.app:app --host 0.0.0.0 --port 8000 &

# Lancement de Streamlit (Port 8501) en arrière-plan
streamlit run streamlit/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 &

# Maintenir le conteneur en vie indéfiniment
echo "Tous les services sont lancés. Conteneur actif."
tail -f /dev/null