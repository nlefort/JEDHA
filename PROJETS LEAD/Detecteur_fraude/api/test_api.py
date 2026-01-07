"""
Script pour tester l'API détection de fraude
À lancer après avoir démarré l'API
"""

import requests
import json
from time import sleep

# Configuration
API_URL = "http://localhost:8000"

def test_health():
    """Test du endpoint /health"""
    print("\n" + "="*60)
    print(" TEST 1: Etat de fonctionnement")
    print("="*60)
    
    response = requests.get(f"{API_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print("API en ligne!")
        print(f"Transactions totales: {data['total_transactions']}")
        print(f"Index actuel: {data['current_index']}")
    else:
        print(f"Erreur: {response.status_code}")
    
    return response.status_code == 200

def test_get_payments(limit=5):
    """Test du endpoint /payments"""
    print("\n" + "="*60)
    print(f"TEST 2: Récupération de {limit} paiements")
    print("="*60)
    
    response = requests.get(f"{API_URL}/payments", params={"limit": limit})
    
    if response.status_code == 200:
        data = response.json()
        print(f"{data['count']} paiements récupérés")
        print(f"imestamp: {data['timestamp']}")
        
        # Afficher le premier paiement
        if data['payments']:
            print("\nPremier paiement:")
            first_payment = data['payments'][0]
            for key, value in first_payment.items():
                if value is not None:
                    print(f"  - {key}: {value}")
        
        return data['payments']
    else:
        print(f"Erreur: {response.status_code}")
        return []

def test_multiple_calls():
    """Simule plusieurs appels comme le ferait Airflow"""
    print("\n" + "="*60)
    print("TEST 3: Simulation de 3 appels successifs (Airflow)")
    print("="*60)
    
    for i in range(1, 4):
        print(f"\nAppel {i}/3...")
        response = requests.get(f"{API_URL}/payments", params={"limit": 10})
        
        if response.status_code == 200:
            data = response.json()
            print(f"{data['count']} paiements reçus")
        else:
            print(f"Erreur")
        
        # Attendre 2 secondes entre les appels
        if i < 3:
            sleep(2)

def test_stats():
    """Test du endpoint /stats"""
    print("\n" + "="*60)
    print("TEST 4: Statistiques de l'API")
    print("="*60)
    
    response = requests.get(f"{API_URL}/stats")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Statistiques récupérées:")
        for key, value in data.items():
            print(f"  - {key}: {value}")
    else:
        print(f"Erreur: {response.status_code}")

def test_fraud_detection_simulation():
    """Simule la détection de fraude"""
    print("\n" + "="*60)
    print("TEST 5: Simulation Détection de Fraude")
    print("="*60)
    
    # Récupérer des paiements avec le label (mode dev)
    response = requests.get(
        f"{API_URL}/payments",
        params={"limit": 20, "include_fraud_label": True}
    )
    
    if response.status_code == 200:
        data = response.json()
        payments = data['payments']
        
        # Compter les fraudes
        fraud_count = sum(1 for p in payments if p.get('is_fraud') == 1)
        
        print(f"Analyse de {len(payments)} transactions:")
        print(f"  - Transactions légitimes: {len(payments) - fraud_count}")
        print(f"  - Fraudes détectées: {fraud_count}")
        
        if fraud_count > 0:
            print("\nFraudes trouvées:")
            for p in payments:
                if p.get('is_fraud') == 1:
                    print(f"{p['transaction_id']}: {p['amount']}€ - {p['merchant']}")
    else:
        print(f"Erreur: {response.status_code}")

def main():
    """Lance tous les tests"""
    print("DÉMARRAGE DES TESTS API")
    print("Assurez-vous que l'API est lancée (python main.py)")
    
    try:
        # Test 1: Health
        if not test_health():
            print("\nL'API n'est pas accessible. Lancez-la d'abord!")
            return
        
        # Test 2: Get payments
        test_get_payments(limit=5)
        
        # Test 3: Multiple calls
        test_multiple_calls()
        
        # Test 4: Stats
        test_stats()
        
        # Test 5: Fraud detection
        test_fraud_detection_simulation()
        
        print("\n" + "="*60)
        print("TOUS LES TESTS TERMINÉS")
        print("="*60)
        print("\nProchaine étape: Intégrer cette API dans Airflow!")
        
    except requests.exceptions.ConnectionError:
        print("\nERREUR: Impossible de se connecter à l'API")
        print("Vérifiez que l'API est lancée avec: python main.py")
    except Exception as e:
        print(f"\nERREUR: {e}")

if __name__ == "__main__":
    main()