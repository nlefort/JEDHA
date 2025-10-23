# ===============================================
#  Getaround - Pricing Model Training Script


import pandas as pd
import numpy as np
import joblib
from catboost import CatBoostRegressor, Pool
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, root_mean_squared_error

# ----------------------------
# 1. Lecture du dataset
# ----------------------------
print(" Chargement du dataset...")
dataset_price = pd.read_csv("D:/Profils/NLefort/Desktop/JEDHA/PROJETS/08.Déploiement/data/get_around_pricing_project.csv", index_col=0)
print(" Dataset chargé :", dataset_price.shape)

# ----------------------------
# 2. Préparation des données
# ----------------------------
bool_features = ['private_parking_available', 
             'has_gps', 'has_air_conditioning', 
             'automatic_car', 
             'has_getaround_connect', 
             'has_speed_regulator', 
             'winter_tires']


# Convertir bool -> int
for col in bool_features:
    dataset_price[col] = dataset_price[col].astype(int)


# Suppression des lignes avec valeurs manquantes sur les variables clés
dataset_price = dataset_price.dropna(subset=['rental_price_per_day', 'mileage', 'engine_power'])

# Colonnes catégorielles
cat_features = ['model_key', 'fuel', 'paint_color', 'car_type']

# Variables numériques
num_features = ['mileage', 'engine_power']

# Cible
target = 'rental_price_per_day'

# Séparation features / target
X = dataset_price[cat_features + bool_features + num_features]
y = dataset_price[target]

print(dataset_price.dtypes)

# ----------------------------
# 3. Création du Pool CatBoost
# ----------------------------
train_pool = Pool(X, y, cat_features=cat_features)

# ----------------------------
# 3. Définition du modèle avec les meilleurs hyperparamètres
# ----------------------------
best_params = {
    'random_strength': 0.5,
    'learning_rate': 0.1,
    'l2_leaf_reg': 1,
    'iterations': 200,
    'depth': 6,
    'border_count': 64,
    'bagging_temperature': 1,
    'loss_function': 'RMSE',
    'verbose': False,
    'random_state': 42
}

model = CatBoostRegressor(
    **best_params,
    cat_features=cat_features,
)

# ----------------------------
# 4. Entraînement
# ----------------------------
print("Entraînement du modèle CatBoost...")
model.fit(X, y)
print("Entraînement terminé.")

# ----------------------------
# 5. Évaluation
# ----------------------------
y_pred = model.predict(X)
rmse = root_mean_squared_error(y, y_pred)
r2 = r2_score(y, y_pred)

print(f"RMSE: {rmse:.2f} €")
print(f"R2: {r2:.2f}")

# ----------------------------
# 6. Feature importance
# ----------------------------
fi = model.get_feature_importance(train_pool)
features = X.columns
importance_df = pd.DataFrame({'Feature': features, 'Importance': fi}).sort_values(by='Importance', ascending=False)
print("\nFeature Importance :")
print(importance_df)

# ----------------------------
# 7. Sauvegarde du modèle
# ----------------------------
joblib.dump(model, "D:/Profils/NLefort/Desktop/JEDHA/PROJETS/08.Déploiement/app/model_auto.pkl")
print("Modèle sauvegardé dans model_auto.pkl")

# ----------------------------
# 8. Fonction prédiction avec fourchette
# ----------------------------
def predict_price(model, example_dict, interval=0.1):
    df = pd.DataFrame([example_dict])
    pred = model.predict(df)[0]
    low = pred * (1 - interval)
    high = pred * (1 + interval)
    return pred, low, high

# Exemple d'utilisation
example = {
    'model_key': 'citroen_c3',
    'fuel': 'diesel',
    'paint_color': 'noir',
    'car_type': 'compact',
    'private_parking_available': 1,
    'has_gps': 1,
    'has_air_conditioning': 0,
    'automatic_car': 0,
    'has_getaround_connect': 1,
    'has_speed_regulator': 0,
    'winter_tires': 0,
    'mileage': 50000,
    'engine_power': 110
}

pred, low, high = predict_price(model, example, interval=0.1)
print(f"\nPrix prédit : {pred:.2f} € / jour")
print(f"Fourchette ±10% : {low:.2f} € - {high:.2f} €")