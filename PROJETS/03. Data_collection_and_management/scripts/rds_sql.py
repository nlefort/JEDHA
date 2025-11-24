import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import re

# Charger les variables d’environnement depuis .env
load_dotenv()
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")  # Nom de la base à créer si elle n'existe pas

# Charger le dataset final
df = pd.read_csv("data/dataset_final.csv")
print("Dataset chargé :", df.shape)

# Fonction pour nettoyer la colonne 'note'
def nettoyer_note(note):
    if pd.isna(note):
        return None
    match = re.search(r'[\d,]+', str(note))
    if match:
        return float(match.group(0).replace(',', '.'))
    return None

df['note'] = df['note'].apply(nettoyer_note)

def base_sql():
    connection = None
    cursor = None

    try:
        # Connexion à l'instance sans spécifier de base
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password
        )
        cursor = connection.cursor()
        print("Connecté à l’instance RDS")

        # Créer la base si elle n'existe pas
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Base '{db_name}' vérifiée / créée avec succès")
        cursor.close()
        connection.close()

        # Reconnexion à la base créée
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = connection.cursor()
        print(f"Connecté à la base '{db_name}'")

        # Créer la table si elle n'existe pas
        create_table_query = """
        CREATE TABLE IF NOT EXISTS hotels_final (
            id VARCHAR(50) PRIMARY KEY,
            id_ville VARCHAR(50),
            ville VARCHAR(255),
            nom VARCHAR(255),
            url TEXT,
            note FLOAT,
            latitude FLOAT,
            longitude FLOAT,
            nom_ville VARCHAR(255),
            temp_moy FLOAT,
            ressenti FLOAT,
            humidity_moy FLOAT,
            prob_pluie_moy FLOAT,
            uv_moy FLOAT
        )
        """
        cursor.execute(create_table_query)

        # Préparer et insérer les données
        insert_query = """
        REPLACE INTO hotels_final
        (id, id_ville, ville, nom, url, note, latitude, longitude, nom_ville,
         temp_moy, ressenti, humidity_moy, prob_pluie_moy, uv_moy)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for _, row in df.iterrows():
            cursor.execute(insert_query, tuple([
                row['id'],
                row['id_ville'],
                row['ville'],
                row['nom'],
                row['url'],
                row['note'],
                row['latitude'],
                row['longitude'],
                row['nom_ville'],
                row['temp_moy'],
                row['ressenti'],
                row['humidity_moy'],
                row['prob_pluie_moy'],
                row['uv_moy']
            ]))

        connection.commit()
        print("Données insérées avec succès")

    except Error as e:
        print("Erreur de connexion ou d'insertion :", e)

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("Connexion MariaDB fermée")

if __name__ == "__main__":
    base_sql()
