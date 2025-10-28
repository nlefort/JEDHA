import requests

url = "http://127.0.0.1:8000/predict"
data = {
  "model_key": "Renault",
  "fuel": "diesel",
  "paint_color": "noir",
  "car_type": "compact",
  "private_parking_available": "Oui",
  "has_gps": "Oui",
  "has_air_conditioning": "Non",
  "automatic_car": "Non",
  "has_getaround_connect": "Oui",
  "has_speed_regulator": "Non",
  "winter_tires": "Non",
  "mileage": 50000,
  "engine_power": 110
}

resp = requests.post(url, json=data)
print(resp.status_code)
print(resp.json())
print(f"Prédiction de prix : {resp.json()['prediction']:.2f} €")