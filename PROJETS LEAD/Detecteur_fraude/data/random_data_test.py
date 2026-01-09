import os
import pandas as pd
#import numpy as np
import random
from datetime import datetime, timedelta

def generate_random_fraud_data(n=10000):
    # Listes pour rendre les données réalistes
    categories = ['entertainment', 'food_dining', 'gas_transport', 'grocery_net',
                  'grocery_pos', 'health_fitness', 'home', 'kids_pets', 'misc_net',
                  'misc_pos', 'personal_care', 'shopping_net', 'shopping_pos', 'travel']
    merchants = ['Amazon', 'Walmart', 'Shell', 'Starbucks', 'Netflix', 'Target', 'CVS']
    jobs = ['Software Engineer', 'Teacher', 'Doctor', 'Artist', 'Manager', 'Chef']
    genders = ['M', 'F']

    data = []
    base_date = datetime(2025, 1, 1)

    for i in range(n):
        # 1. Dates et Heures aléatoires sur un an
        trans_time = base_date + timedelta(seconds=random.randint(0, 31536000))
        dob = datetime(1950, 1, 1) + timedelta(days=random.randint(0, 20000))
        
        # 2. Localisation utilisateur (autour de NY par exemple)
        user_lat = 40.7128 + random.uniform(-0.5, 0.5)
        user_long = -74.0060 + random.uniform(-0.5, 0.5)
        
        # 3. Création du scénario (Fraude vs Normal)
        is_fraud = random.choices([0, 1], weights=[97, 3])[0] # 3% de fraude
        
        if is_fraud:
            # Profil fraude : Gros montant + distance élevée
            amt = random.uniform(500, 5000)
            dist_offset = random.uniform(0.5, 3.0) 
        else:
            # Profil normal : Petit montant + proche du domicile
            amt = random.uniform(5, 500)
            dist_offset = random.uniform(0.01, 0.2)

        merch_lat = user_lat + random.uniform(-dist_offset, dist_offset)
        merch_long = user_long + random.uniform(-dist_offset, dist_offset)

        row = {
            "trans_date_trans_time": trans_time.strftime("%Y-%m-%d %H:%M:%S"),
            "cc_number": "".join([str(random.randint(0, 9)) for _ in range(16)]),
            "merchant": random.choice(merchants),
            "category": random.choice(categories),
            "amt": round(amt, 2),
            "first": "User",
            "last": str(i),
            "gender": random.choice(genders),
            "street": f"{random.randint(1, 999)} Rue de la Paix",
            "city": "Paris",
            "state": "FR",
            "zip": "75000",
            "lat": user_lat,
            "long": user_long,
            "city_pop": random.randint(1000, 2000000),
            "job": random.choice(jobs),
            "dob": dob.strftime("%Y-%m-%d"),
            "trans_num": "".join(random.choices("abcdef0123456789", k=32)),
            "unix_time": int(trans_time.timestamp()),
            "merch_lat": merch_lat,
            "merch_long": merch_long,
            "is_fraud": is_fraud
        }
        data.append(row)

    return pd.DataFrame(data)

# Génération de 50000 lignes pour tester script train_model.py
file_name = 'fraudTest_random.csv'
current_folder = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_folder, file_name)
df_test = generate_random_fraud_data(10000)
df_test.to_csv(file_path, index=False)

print(f"Fichier créé avec succès dans : {file_path}")