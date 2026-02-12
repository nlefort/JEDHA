#!/bin/bash
set -e

echo "--- Initialisation d'Airflow ---"

# 1. On attend que Postgres réponde
echo "Vérification de la DB..."
airflow db check

# 2. On crée/met à jour les tables
echo "Mise à jour de la DB..."
airflow db upgrade

# 3. On crée l'admin (idempotent grâce au || true)
echo "Création de l'utilisateur admin..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin || true

echo "--- Initialisation terminée ---"