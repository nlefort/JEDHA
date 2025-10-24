# streamlit/app.py
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Getaround Dashboard", layout="wide")

st.title(" Getaround Pricing Dashboard")

menu = st.sidebar.radio("Navigation", ["Exploration des données", "Prédiction de prix"])

if menu == "Exploration des données":
    st.header(" Analyse données de location de voitures")
    df = pd.read_csv("../data/get_around_pricing_project.csv")
    st.write(df.head())
    st.bar_chart(df['car_type'].value_counts())

elif menu == "Prédiction de prix":
    st.header(" Estimation du prix de location")

    model_key = st.selectbox("Modèle", ["citroen_c3", "peugeot_208", "renault_clio"])
    fuel = st.selectbox("Carburant", ["diesel", "essence", "hybride", "electrique"])
    paint_color = st.selectbox("Couleur", ["noir", "blanc", "gris", "bleu", "rouge"])
    car_type = st.selectbox("Type", ["citadine", "compact", "suv", "berline"])
    mileage = st.number_input("Kilométrage", 0, 300000, 50000)
    engine_power = st.number_input("Puissance moteur", 50, 300, 110)
    gps = st.checkbox("GPS")
    air = st.checkbox("Climatisation")
    auto = st.checkbox("Automatique")

    if st.button("Prédire le prix"):
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

        url = "http://127.0.0.1:8000/predict"
        response = requests.post(url, json=data)

        if response.status_code == 200:
            res = response.json()
            st.success(f" Prix estimé : {res['prediction']:.2f} € / jour")
            st.info(f"Fourchette : {res['interval'][0]:.2f} € - {res['interval'][1]:.2f} €")
        else:
            st.error("Erreur de communication avec l'API")
