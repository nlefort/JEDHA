# Dockerfile - image qui lance FastAPI avec Uvicorn + Streamlit 
FROM python:3.10

# Eviter buffeing Python
ENV PYTHONUNBUFFERED=1

# Définir le répertoire de travail
WORKDIR /app

# Copier requirements et installer d'abord
COPY requirements.txt .

RUN apt-get update --yes \
    && apt-get install --yes --no-install-recommends build-essential gcc curl \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove --yes build-essential gcc \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/apt/lists/*

# Copier le code de l'application
#COPY api ./api
#COPY streamlit ./streamlit
#COPY model ./model
#COPY data ./data

COPY . .

# Copier le script de démarrage
COPY start.sh /start.sh
RUN chmod +x /start.sh


# Exposer les ports (FAST API et Streamlit)
# Port Hugging Face Space
# EXPOSE 7860 
# Port FastAPI par défaut
EXPOSE 8000 
# Port Streamlit par défaut
EXPOSE 8501


# Commande qui lance le launcher (démarre uvicorn et streamlit)
CMD ["/start.sh"]