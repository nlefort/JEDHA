import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Charger les variables d’environnement
load_dotenv()
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Charger le dataset final
df = pd.read_csv("data/dataset_final.csv")

print("Dataset chargé :", df.shape)

def base_sql():
    # Connexion à MariaDB
    try:
        connection = mysql.connector.connect(
            host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

        if connection.is_connected():
            cursor = connection.cursor()
            print(" Connecté à MariaDB")

        #supprimer la table si elle existe
            cursor.execute("DROP TABLE IF EXISTS hotels_final;")


        # Création de la table si elle n'existe pas
            create_table_query = """
            CREATE TABLE IF NOT EXISTS hotels_final (
                id VARCHAR(50) PRIMARY KEY,
                id_ville VARCHAR(50),
                ville VARCHAR(255),
                nom VARCHAR(255),
                url TEXT,
                note VARCHAR(255),
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

        # Insérer les données
            insert_query = """
            REPLACE INTO hotels_final
            (id, id_ville, ville, nom, url, note, latitude, longitude, nom_ville, temp_moy, ressenti, humidity_moy, prob_pluie_moy, uv_moy)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            for _, row in df.iterrows():
                cursor.execute(insert_query, tuple(row))

            connection.commit()
            print("Données insérées avec succès")

    except Error as e:
        print(" Erreur de connexion ou d'insertion :", e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print(" Connexion MariaDB fermée")

if __name__ == "__main__":
    base_sql()