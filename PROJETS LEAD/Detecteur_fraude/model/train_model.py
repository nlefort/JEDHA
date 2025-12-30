# ===============================================
#  Automatic Fraud Detection - Model Training Script (FIXED)
# ===============================================

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import f1_score, confusion_matrix, recall_score, precision_score, classification_report
from imblearn.over_sampling import SMOTE
import mlflow
import mlflow.xgboost

# ----------------------------
# 1. Lecture du dataset
# ----------------------------
print("Chargement du dataset...")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataset_path = os.path.join(ROOT_DIR, 'data', 'fraudTest.csv')
dataset_path = os.path.abspath(dataset_path)

print(f"Chemin du dataset : {dataset_path}")

dataset = pd.read_csv(dataset_path, index_col=0)
print(f"Dataset chargé : {dataset.shape}")
print(f"Fraudes : {dataset['is_fraud'].sum()} ({dataset['is_fraud'].mean()*100:.2f}%)")

# ----------------------------
# 2. Préparation des données
# ----------------------------
print("\nFeature Engineering...")

dataset = dataset.copy()

# Convertir la colonne en format datetime
dataset["trans_date_trans_time"] = pd.to_datetime(dataset["trans_date_trans_time"])

# Convertir Date en année / semaine / jour de semaine
dataset["Year"] = dataset["trans_date_trans_time"].dt.year
dataset["Month"] = dataset["trans_date_trans_time"].dt.month
dataset["Day"] = dataset["trans_date_trans_time"].dt.day
dataset["Weekday"] = dataset["trans_date_trans_time"].dt.weekday
dataset['Hour'] = dataset['trans_date_trans_time'].dt.hour

# CREATION DES VARIABLES (distance et âge)
def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi, delta_lambda = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(delta_phi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(delta_lambda/2)**2
    return 2 * r * np.arcsin(np.sqrt(a))

dataset['distance_km'] = haversine_distance(
    dataset['lat'], dataset['long'], 
    dataset['merch_lat'], dataset['merch_long']
)
dataset['age'] = dataset['Year'] - pd.to_datetime(dataset['dob']).dt.year

# Encodage gender
dataset['gender_m'] = dataset['gender'].map({'M': 1, 'F': 0})

# ----------------------------
# 3. Split AVANT tout preprocessing
# ----------------------------
print("\n Split Train/Test...")

features_list = [
    "amt",
    "zip",
    "city_pop",
    "distance_km",
    "category",  # On garde la catégorie originale pour l'instant
    "gender_m",
    "Hour",
    "Weekday",
]

X = dataset[features_list].copy()
y = dataset["is_fraud"]

# SPLIT STRATIFIÉ (important pour classes déséquilibrées)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train : {X_train.shape[0]} samples ({y_train.sum()} fraudes)")
print(f"Test  : {X_test.shape[0]} samples ({y_test.sum()} fraudes)")

# ----------------------------
# 4. Target Encoding (SUR TRAIN UNIQUEMENT)
# ----------------------------
print("\nTarget Encoding...")

# Calculer l'encoding UNIQUEMENT sur le train
target_map = X_train.join(y_train).groupby('category')['is_fraud'].mean()
print(f"Categories encodées : {len(target_map)}")

# Appliquer sur train et test
X_train['category_enc'] = X_train['category'].map(target_map)
X_test['category_enc'] = X_test['category'].map(target_map)

# Gérer les catégories inconnues (valeur moyenne globale)
mean_fraud_rate = y_train.mean()
X_train['category_enc'].fillna(mean_fraud_rate, inplace=True)
X_test['category_enc'].fillna(mean_fraud_rate, inplace=True)

# Supprimer la colonne category originale
X_train = X_train.drop('category', axis=1)
X_test = X_test.drop('category', axis=1)

# ----------------------------
# 5. Standardisation (SUR TRAIN UNIQUEMENT)
# ----------------------------
print("\nStandardisation...")

num_features = [
    "amt",
    "zip",
    "city_pop",
    "distance_km",
    "Hour",
    "Weekday",
]

scaler = StandardScaler()

# FIT sur train, TRANSFORM sur train et test
X_train[num_features] = scaler.fit_transform(X_train[num_features])
X_test[num_features] = scaler.transform(X_test[num_features])

print("Standardisation terminée")

# ----------------------------
# 6. Application de SMOTE (SUR TRAIN UNIQUEMENT)
# ----------------------------
print("\nApplication de SMOTE...")
print(f"Avant SMOTE : Fraudes={y_train.sum()}, Non-fraudes={len(y_train)-y_train.sum()}")

smote = SMOTE(random_state=42, sampling_strategy=0.5)  # 50% de fraudes après SMOTE
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

print(f"Après SMOTE : Fraudes={y_train_resampled.sum()}, Non-fraudes={len(y_train_resampled)-y_train_resampled.sum()}")

# ----------------------------
# 7. Définition du modèle
# ----------------------------
print("\nConfiguration du modèle XGBoost...")

best_params = {
    'learning_rate': 0.1,
    'n_estimators': 200,
    'max_depth': 8,
    'subsample': 1.0,
    'scale_pos_weight': 1,  # Ajusté car SMOTE a déjà équilibré
    'random_state': 42,
    'eval_metric': 'logloss'
}

model = XGBClassifier(**best_params)

# ----------------------------
# 8. Entraînement avec MLflow
# ----------------------------
print("\nEntraînement du modèle...")

mlflow.xgboost.autolog()
mlflow.set_experiment("Automatic_Fraud_Detection_XGBoost")

with mlflow.start_run(run_name="xgboost_fraud_detection_fixed"):
    
    # ENTRAÎNEMENT SUR LES DONNÉES RESAMPLED
    model.fit(X_train_resampled, y_train_resampled)
    print("Entraînement terminé")
    
    # ----------------------------
    # 9. Évaluation sur TEST SET (données JAMAIS vues)
    # ----------------------------
    print("\nÉvaluation sur le Test Set...")
    
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Métriques
    f1 = f1_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    
    print(f"\n{'='*50}")
    print(f"RÉSULTATS SUR TEST SET")
    print(f"{'='*50}")
    print(f"F1 Score   : {f1:.4f}")
    print(f"Recall     : {recall:.4f} (% de fraudes détectées)")
    print(f"Precision  : {precision:.4f} (% de prédictions correctes)")
    print(f"{'='*50}\n")
    
    # Matrice de confusion
    cm = confusion_matrix(y_test, y_pred)
    print("Matrice de Confusion :")
    print(f"  TN={cm[0,0]:6d} | FP={cm[0,1]:6d}")
    print(f"  FN={cm[1,0]:6d} | TP={cm[1,1]:6d}")
    print()
    
    # Classification report
    print("Classification Report :")
    print(classification_report(y_test, y_pred, target_names=['Légal', 'Fraude']))
    
    # Log dans MLflow
    mlflow.log_params(best_params)
    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("precision", precision)
    
    # Log du modèle
    mlflow.xgboost.log_model(model, "xgboost_model")
    print("Modèle loggé dans MLflow")
    
    # ----------------------------
    # 10. Feature Importance
    # ----------------------------
    print("\nFeature Importance :")
    fi = model.feature_importances_
    features = X_train.columns
    importance_df = pd.DataFrame({
        'Feature': features, 
        'Importance': fi
    }).sort_values(by='Importance', ascending=False)
    print(importance_df.to_string(index=False))
    
    # ----------------------------
    # 11. Sauvegarde du modèle ET du scaler
    # ----------------------------
    print("\nSauvegarde des artefacts...")
    
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Sauvegarder le modèle
    model_path = os.path.join(CURRENT_DIR, 'model_auto.pkl')
    joblib.dump(model, model_path)
    print(f"Modèle sauvegardé : {model_path}")
    
    # Sauvegarder le scaler
    scaler_path = os.path.join(CURRENT_DIR, 'scaler.pkl')
    joblib.dump(scaler, scaler_path)
    print(f"Scalers sauvegardé : {scaler_path}")
    
    # Sauvegarder le target encoding map
    encoding_path = os.path.join(CURRENT_DIR, 'target_encoding.pkl')
    joblib.dump(target_map, encoding_path)
    print(f"Target encoding sauvegardé : {encoding_path}")

print("\n" + "="*50)
print("ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS")
print("="*50)

# ----------------------------
# 12. Fonction de prédiction réutilisable
# ----------------------------
def predict_transaction(amt, age, distance_km, hour, weekday, 
                       category, gender_m, city_pop, zip_code):
    """
    Prédit si une transaction est frauduleuse
    
    IMPORTANT : Utilise les artefacts sauvegardés (scaler, encoding)
    """
    # Charger les artefacts
    model = joblib.load(os.path.join(CURRENT_DIR, 'model_auto.pkl'))
    scaler = joblib.load(os.path.join(CURRENT_DIR, 'scaler.pkl'))
    target_map = joblib.load(os.path.join(CURRENT_DIR, 'target_encoding.pkl'))
    
    # Encoder la catégorie
    category_enc = target_map.get(category, mean_fraud_rate)
    
    # Créer le DataFrame
    data = pd.DataFrame([[
        amt, zip_code, city_pop, distance_km, 
        category_enc, gender_m, hour, weekday
    ]], columns=X_train.columns)
    
    # Standardiser les features numériques
    data[num_features] = scaler.transform(data[num_features])
    
    # Prédire
    prob = model.predict_proba(data)[0][1]
    prediction = "FRAUDE PROBABLE" if prob >= 0.86 else "TRANSACTION VALIDÉE"
    
    print(f"\n{'='*50}")
    print(f"Probabilité de fraude : {prob:.2%}")
    print(f"Verdict : {prediction}")
    print(f"{'='*50}")
    
    return prob

# Test de la fonction
print("\nTest de prédiction...")
predict_transaction(
    amt=950, 
    age=30, 
    distance_km=450, 
    hour=2,
    weekday=5, 
    category='gas_transport',  # Utiliser une vraie catégorie
    gender_m=0, 
    city_pop=15000,
    zip_code=12345
)