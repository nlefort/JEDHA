# streamlit/app.py
import os
import streamlit as st
import pandas as pd
import requests
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Getaround Dashboard", layout="wide")

st.title("Analyse des retards et estimation de prix des locations")

# Message de debug
st.sidebar.success("Application Streamlit lancée avec succès")

# Vérifier que les fichiers existent
data_path_csv = "data/get_around_pricing_project.csv"
data_path_xlsx = "data/get_around_delay_analysis.xlsx"

st.sidebar.header("Vérification des données")

if os.path.exists(data_path_csv):
    st.sidebar.write(f"{data_path_csv} trouvé")
else:
    st.sidebar.error(f"{data_path_csv} manquant")

if os.path.exists(data_path_xlsx):
    st.sidebar.write(f"{data_path_xlsx} trouvé")
else:
    st.sidebar.error(f"{data_path_xlsx} manquant")


# Menu principal
menu = st.sidebar.radio(
    "Navigation",
    ["Accueil", "Analyse des données GetAround", "Estimation du prix de location"]
)

# --- PAGE ACCUEIL ---
if menu == "Accueil":
    st.markdown("""
    ## Bienvenue sur l'application Getaround 
    Cette application regroupe :
    - une analyse des données GetAround
                - Analyse descriptive des location
                - Simulation du délai tampon entre deux locations
                - Analyse économique du délai tampon
                - Synthèse et recommandation
    - une estimation du prix de location
                - à partir d'un modèle de prédictionaccès à votre modèle CatBoost via une API FastAPI
    """)

# --- PAGE TABLEAU DE BORD ---
elif menu == "Tableau de bord des locations":
    st.header("Analyse des données Getaround")


    # Charger les données
    dataset_path = "/app/data/get_around_delay_analysis.xlsx"
    dataset = pd.read_excel(dataset_path, index_col=0)

    dataset_price_path = "/app/data/get_around_pricing_project.csv"
    dataset_price = pd.read_csv(dataset_price_path, index_col=0)


    # -----------------------------
    #  ANALYSE DESCRIPTIVE
    # -----------------------------
    st.header("Analyse descriptive des locations")
    dataset['delay_at_checkout_in_minutes'] = pd.to_numeric(dataset['delay_at_checkout_in_minutes'], errors='coerce')    
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre de locations", dataset.shape[0])
    col2.metric("Nombre de véhicules", dataset['car_id'].nunique())
    col3.metric("Nombre de retards", int((dataset['delay_at_checkout_in_minutes'] > 0).sum()))


    st.subheader("Répartition des types de check-in")
    fig1 = px.pie(dataset, names='checkin_type', title="Types de check-in")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Distribution des états de location")
    fig2 = px.histogram(dataset, x='state', color='state', title="État des locations")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Distribution du retard au checkout")
    dataset = dataset.dropna(subset=['delay_at_checkout_in_minutes']).copy()
    # ========================
    # Statistiques par type de contrat
    # ========================
    stats_by_type = (
        dataset[dataset['delay_at_checkout_in_minutes'] > 0]
        .groupby('checkin_type')['delay_at_checkout_in_minutes']
        .agg([
            ('Retard moyen (min)', 'mean'),
            ('Retard médian (min)', 'median'),
            ('90e percentile (min)', lambda x: x.quantile(0.9))
        ])
        .reset_index()
    )

    # Ajout du taux de retard par type
    taux_retard_by_type = (
        dataset.groupby('checkin_type')['delay_at_checkout_in_minutes']
        .apply(lambda x: (x > 0).mean())
        .reset_index(name='Taux de retard')
    )

    # Fusion des deux tableaux
    summary = pd.merge(taux_retard_by_type, stats_by_type, on='checkin_type')

    # ========================
    # Calcul global
    # ========================
    global_row = pd.DataFrame({
        'checkin_type': ['Global'],
        'Taux de retard': [(dataset['delay_at_checkout_in_minutes'] > 0).mean()],
        'Retard moyen (min)': [dataset.loc[dataset['delay_at_checkout_in_minutes'] > 0, 'delay_at_checkout_in_minutes'].mean()],
        'Retard médian (min)': [dataset.loc[dataset['delay_at_checkout_in_minutes'] > 0, 'delay_at_checkout_in_minutes'].median()],
        '90e percentile (min)': [dataset.loc[dataset['delay_at_checkout_in_minutes'] > 0, 'delay_at_checkout_in_minutes'].quantile(0.9)],
        'Retard min (min)': [dataset.loc[dataset['delay_at_checkout_in_minutes'] > 0, 'delay_at_checkout_in_minutes'].min()],
        'Retard max (min)': [dataset.loc[dataset['delay_at_checkout_in_minutes'] > 0, 'delay_at_checkout_in_minutes'].max()]
    })

    # ========================
    # Tableau final
    # ========================
    final_summary = pd.concat([global_row, summary], ignore_index=True)
    final_summary['Taux de retard'] = (final_summary['Taux de retard'] * 100).round(1).astype(str) + ' %'
    final_summary = final_summary.round(1)

    st.table(final_summary.round(1))

    st.header(" Simulation du délai tampon entre deux locations")

    dataset['delay_at_checkout_in_minutes'] = pd.to_numeric(dataset['delay_at_checkout_in_minutes'], errors='coerce')
    dataset['time_delta_with_previous_rental_in_minutes'] = pd.to_numeric(dataset['time_delta_with_previous_rental_in_minutes'], errors='coerce')

    # copier le dataset existant
    dataset_seuil=dataset.copy()

    # ========================
    # Simulation delta "temps" entre deux location
    # ========================

    # Simuler les time_delta manquants pour que la simulation ait du sens
    nan_mask = dataset_seuil['time_delta_with_previous_rental_in_minutes'].isna()
    dataset_seuil.loc[nan_mask, 'simulated_time_delta'] = np.random.randint(30, 600, size=nan_mask.sum())
    dataset_seuil.loc[~nan_mask, 'simulated_time_delta'] = dataset_seuil.loc[~nan_mask, 'time_delta_with_previous_rental_in_minutes']


    def calculate_retards_conflicts(dataset_seuil, threshold, alpha=1.0):
        """
        dataset_seuil : DataFrame avec colonnes 'simulated_time_delta' et 'delay_at_checkout_in_minutes'
        threshold : seuil tampon entre deux locations (en minutes)
        """
        dataset_seuil = dataset_seuil.copy()
        # Conflits = locations bloquées par le seuil
        dataset_seuil['conflict'] = dataset_seuil['simulated_time_delta'] < threshold
        
        # Retards évités = retards qui auraient été bloqués
        dataset_seuil['retard_evite'] = dataset_seuil['conflict'] & (dataset_seuil['delay_at_checkout_in_minutes'] > 0)
        
        pct_conflict = dataset_seuil['conflict'].mean() * 100
        pct_retard_evite = dataset_seuil['retard_evite'].mean() * 100
        
        # Score trade-off = retards évités - alpha * conflits
        score = pct_retard_evite - alpha * pct_conflict
        
        return pct_conflict, pct_retard_evite, score


    seuil = st.slider("Choisir un seuil tampon (minutes)", 0, 240, 60, step=30)
    st.info(f'Seuil actuel : **{seuil} minutes**')

    # Appel correct de la fonction avec dataset_seuil
    conflict, retard, score = calculate_retards_conflicts(dataset_seuil, seuil)

    st.metric("Conflits (%)", round(conflict, 2))
    st.metric("Retards évités (%)", round(retard, 2))


    thresholds = list(range(0, 241, 15))
    results = []

    for t in thresholds:
        conflict, retard, s = calculate_retards_conflicts(dataset_seuil, t)
        results.append({'threshold': t, 'pct_conflict': conflict, 'pct_retard_evite': retard})

    results_df = pd.DataFrame(results)

    # Calculs de base
    results_df['delta'] = results_df['pct_retard_evite'] - results_df['pct_conflict']

    # Affichage du tableau récapitulatif
    cols_to_display = ['threshold', 'pct_conflict', 'pct_retard_evite', 'delta']


    st.markdown("""
    ##### Approche perte pour le client

    - Calcul d'une fonction de coût afin d'identifier la perte pour le client
    - Etape 1 - calcul du revenu moyen par location
        - Revenu_moyen = revenu journalier mpyen x durée moyenne location en jours
    - Etape 2 - calcul d'un coût de retard évite. Ce coût correspond à du temps perdu qu'on pourrait louer. Un retard d'une heure sur une location de 4 h coûte environ 1/4 du revenu moyen
        - Coût_retard = revenu moyen x (retard moyen/durée moyenne)
    - Etape 3 - Score monétaire basé sur les taux (%) 
        - Score/location = Coût_retard x % retard évité - Revenu_moyen x % conflit 
    """)

    # -----------------------------
    # ANALYSE ÉCONOMIQUE
    # -----------------------------
    st.title(" Analyse économique du délai tampon")

    revenu_journalier_moyen = dataset_price['rental_price_per_day'].mean()
    duree_moyenne_min = dataset_seuil['simulated_time_delta'].mean()
    duree_moyenne_jours = duree_moyenne_min / 60 / 24
    retard_moyen_min = dataset_seuil['delay_at_checkout_in_minutes'].mean()

    R_avg = revenu_journalier_moyen * duree_moyenne_jours
    C_delay = R_avg * (retard_moyen_min / duree_moyenne_min)

    results_df["score_monetary"] = (
        C_delay * (results_df["pct_retard_evite"] / 100)
        - R_avg * (results_df["pct_conflict"] / 100)
    )
    results_df["total_score_euros"] = results_df["score_monetary"] * dataset.shape[0]

    cols_to_order=[
        'threshold',
        'pct_conflict',
        'pct_retard_evite',
        'score_monetary',
        'total_score_euros'
    ]

    st.dataframe(results_df[cols_to_order].round(0))

   
    # -----------------------------
    # SYNTHÈSE
    # -----------------------------

    st.title("Synthèse et recommandations")
    st.markdown("""
        - Un délai de 60 min réduit de **4 % les retards**, mais bloque **6,8 % des locations**.
        - Cela équivaut à une **perte moyenne de 1,6 € par location**.
        - Aucun seuil testé n’est économiquement avantageux, mais un tampon modéré reste utile pour réduire le stress opérationnel.
        """)



elif menu == "Estimation du prix":
    st.header(" Estimation du prix de location")

    model_key = st.selectbox("Modèle", ["Citroën", "Renault", "BMW", "KIA", "Fiat", "Mazda", "Audi", "Nissan"])
    fuel = st.selectbox("Carburant", ["diesel", "petrol", "hybride", "electrique"])
    paint_color = st.selectbox("Couleur", ["black", "grey", "blue", "white", "red"])
    car_type = st.selectbox("Type", ["estate", "suv", "van", "convertible"])
    mileage = st.number_input("Kilométrage", 0, 500000)
    engine_power = st.number_input("Puissance moteur", 50, 350)
    gps = st.checkbox("GPS")
    air = st.checkbox("Climatisation")
    auto = st.checkbox("Automatique")

    if st.button("Estimer le prix de la location"):
        data = {
            "model_key": model_key,
            "fuel": fuel,
            "paint_color": paint_color,
            "car_type": car_type,
            "private_parking_available": 1,
            "has_gps": int(gps),
            "has_air_conditioning": int(air),
            "automatic_car": int(auto),
            "has_getaround_connect": 1,
            "has_speed_regulator": 0,
            "winter_tires": 0,
            "mileage": mileage,
            "engine_power": engine_power
        }

        url = "http://localhost:8000/predict"
        response = requests.post(url, json=data)

        if response.status_code == 200:
            res = response.json()
            st.success(f" Prix estimé : {res['prediction']:.2f} € / jour")
            st.info(f"Fourchette : {res['interval'][0]:.2f} € - {res['interval'][1]:.2f} €")
        else:
            st.error("Erreur de communication avec l'API")
