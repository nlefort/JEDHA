import requests

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

response = requests.post("http://127.0.0.1:8000/predict", json=example)
print(response.json())
