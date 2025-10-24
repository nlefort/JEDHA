# Utiliser une image Python officielle comme image parente
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /api

# Copier les fichiers de l'application dans le conteneur
COPY . .
#COPY requirements.txt .
#COPY app.py .
#COPY model_auto.pkl .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port de l'application
# Port Hugging Face Space
EXPOSE 7860 
# Port FastAPI par défaut
# EXPOSE 8000 


# Commande pour démarrer l'application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "--reload"]