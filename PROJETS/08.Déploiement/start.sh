# !/usr/bin/env bash
set -e

# Démarrer FastAPI (Uvicorn) en arrière-plan
uvicorn api.app:app --host 0.0.0.0 --port 8000 &

# Attendre que l'API démarre
sleep 2

# Lancer Streamlit au premier plan
streamlit run streamlit/app.py --server.port 8501 --server.address 0.0.0.0 &

# Maintenir le conteneur en exécution
tail -f /dev/null