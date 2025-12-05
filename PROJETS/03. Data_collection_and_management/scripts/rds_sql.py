from dotenv import load_dotenv
import os
import re
import pandas as pd
import mysql.connector

def base_sql():
    """Charge le dataset final CSV et l'insère dans la base RDS MySQL."""
    
    # Charger les variables d'environnement
    load_dotenv()
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    # Chemin vers le CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    dataset_path = os.path.join(data_dir, "dataset_final.csv")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Le fichier CSV n'existe pas : {dataset_path}")

    # Lire le CSV
    df = pd.read_csv(dataset_path)

    # Nettoyer la colonne 'note'
    def nettoyer_note(note):
        if pd.isna(note):
            return None
        match = re.search(r'[\d,]+', str(note))
        if match:
            return float(match.group(0).replace(',', '.'))
        return None

    if 'note' in df.columns:
        df['note'] = df['note'].apply(nettoyer_note)

    # Colonnes exactes pour MySQL
    table_cols = [
        'id', 'id_ville', 'ville', 'nom', 'url', 'note',
        'latitude', 'longitude', 'nom_ville',
        'temp_moy', 'ressenti', 'humidity_moy', 'prob_pluie_moy', 'uv_moy',
        'meteo_score'
    ]

    # Sélectionner uniquement les colonnes existantes dans le CSV
    df_insert = df[[col for col in table_cols if col in df.columns]]

    # Remplacer les NaN par None
    df_insert = df_insert.where(pd.notnull(df_insert), None)

    # Connexion à MySQL sans base (pour créer si nécessaire)
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    cursor.close()
    conn.close()

    # Reconnexion à la base
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = conn.cursor()

    # Supprimer la table si elle existe
    cursor.execute("DROP TABLE IF EXISTS hotels_final")

    # Créer la table
    create_table = """
    CREATE TABLE hotels_final (
        id VARCHAR(50) PRIMARY KEY,
        id_ville VARCHAR(50),
        ville VARCHAR(50),
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
        uv_moy FLOAT,
        meteo_score FLOAT
    )
    """
    cursor.execute(create_table)

    # Préparer la requête REPLACE INTO
    insert_query = f"""
    REPLACE INTO hotels_final ({', '.join(df_insert.columns)})
    VALUES ({', '.join(['%s'] * len(df_insert.columns))})
    """

    # Boucle d’insertion avec conversion NaN → None
    for _, row in df_insert.iterrows():
        values = tuple(None if pd.isna(x) else x for x in row)
        cursor.execute(insert_query, values)

    conn.commit()
    cursor.close()
    conn.close()
    print("Données insérées avec succès dans RDS.")


if __name__ == "__main__":
    base_sql()
