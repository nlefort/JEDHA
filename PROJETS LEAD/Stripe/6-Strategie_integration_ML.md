# Stratégie d'intégration Machine Learning

## 1. Pourquoi utiliser le Machine Learning ?

### 1.1 Le problème de la fraude

Stripe traite plusieurs millions de transactions par jour. Cela représente des pertes potentielles importantes si elles ne sont pas détectées.

Les types de fraude :

- Carte volée: Quelqu'un utilise une carte qui ne lui appartient pas
- Teste de cartes (Card Testing): Pirate teste des milliers de numéros pour trouver ceux qui fonctionnent
- Fraude amicale (Friendly Fraud): Client légitime demande un chargeback alors qu'il a reçu le produit
- Fraude synthétique: Création de fausses identités avec vraies/fausses infos mélangées

Règles traditionnelles :

- SI montant > 1000€ ALORS bloquer
- SI pays = Nigéria ALORS bloquer
- SI 3+ transactions en 1h ALORS bloquer

Problèmes :

- Trop de faux positifs : Blocage de vrais clients (frustration)
- Facile à contourner : Fraudeurs adaptent (montant 999€, 2 tx/h)
- Pas adaptatif : Nouveaux patterns de fraude non détectés

**Machine Learning** :

- Analyse 50+ features en temps réel : Vélocité (transactions/heure), réputation appareil, historique utilisateur,...
L'analyse des features permet d'établir un score de fraude. 

**Avantages** :

- **Moins de faux positifs** : Analyse nuancée, pas binaire
- **S'adapte** : Apprend des changements de comportement
- **Rapide** : Décision en < 100ms

## 2. Le Pipeline ML

### 2.1 Vue d'ensemble

```ascii
┌──────────────────────────────────────────────────┐
│ 1. COLLECTE DES DONNÉES                          │
│    PostgreSQL + MongoDB → Historique utilisateur │
└─────────────────┬────────────────────────────────┘
                  │
┌──────────────────────────────────────────────────┐
│ 2. CALCUL DES FEATURES                           │
│    Transaction → 50 features                     │
│    Ex: "Cet user a fait 12 transactions en 24h"  │
└─────────────────┬────────────────────────────────┘
                  │
┌──────────────────────────────────────────────────┐
│ 3. PRÉDICTION                                    │
│    Modèle ML → Score fraude (0-100%)             │
│    Ex: "85% de chance que ce soit une fraude"    │
└─────────────────┬────────────────────────────────┘
                  │
┌──────────────────────────────────────────────────┐
│ 4. DÉCISION                                      │
│    ├─ Score > 80% → BLOQUER                      │
│    ├─ Score 50-80% → REVUE MANUELLE              │
│    └─ Score < 50% → APPROUVER                    │
└─────────────────┬────────────────────────────────┘
                  │
┌──────────────────────────────────────────────────┐
│ 5. APPRENTISSAGE CONTINU                         │
│    Stocker résultat → Réentraîner modèle         │
└──────────────────────────────────────────────────┘
```

## 3. Les Features (Caractéristiques)

**Feature** = Une information qui aide à détecter la fraude

- Heure inhabituelle ? (3h du matin)
- Localisation bizarre ? (Carte à Paris puis Tokyo en 10 min)
- Montant anormal ? (Toujours 10€, puis 1000€)
- Nouvel appareil ? (Jamais vu avant)

### 3.2 Les 3 types de features

#### Type 1 : Features de vélocité

**Question** : "Combien de transactions cet utilisateur fait-il ?"
*Features calculées* : transactions_last_hour, transactions_last_24h, total_amount_24h, unique_merchants_24h
*Pourquoi c'est utile* : utilisateur normal = 1-2 transactions/jour // Suspect = 10 transactions/heure

#### Type 2 : Features d'appareil

**Question** : "Cet appareil est-il fiable ?"
*Features calculées* : device_age_days, is_new_device, device_reputation_score, device_transaction_count
*Pourquoi c'est utile* : Appareil connu depuis 45 jours avec 120 transactions = Fiable // Appareil jamais vu avec 50 transactions en 1h = Suspect

#### Type 3 : Features comportementales

**Question** : "Ce comportement est-il habituel pour cet utilisateur ?"
*Feature calculée* : ecart_montant_moyen, heure_anormale, localisation_anormale, duree_depuis_dernière_transaction
*Pourquoi c'est utile* : Montant habituel à heure/lieu habituels = Normal // Montant 10x supérieur dans pays jamais visité = Suspect

### 3.3 Comment on stocke les features ?

**Dans MongoDB** (collection `fraud_ml_features`) :

```json
{
  "transaction_id": "txn_123",
  "computed_at": "2024-12-22T10:32:00Z",
  
  "velocity": {
    "transactions_last_hour": 3,
    "transactions_last_24h": 12
  },
  
  "device": {
    "is_new_device": false,
    "device_reputation_score": 0.85
  },
  
  "comportement": {
    "ecart_montant_moyen": 2.3,
    "heure_anormale": false
  },
  
  "fraud_prediction": {
    "fraud_probability": 0.08,
    "decision": "approved"
  }
}
```

**Pourquoi MongoDB et pas PostgreSQL** :

- Structure flexible (on ajoute des features sans casser l'existant)
- Rapide pour écrire (millions de features/jour)
- Historique pour réentraîner le modèle plus tard

## 4. Entraînement du Modèle

### 4.1 Processus

- ÉTAPE 1 : Collecter des exemples
  - transactions passées (1 millions)
  - Pour chacune : "Était-ce une fraude ?" (OUI/NON)
  - Calculer les features pour chacune

- ÉTAPE 2 : Entraîner le modèle
  - Algorithme : XGBoost (très performant)
  - Le modèle apprend : "Quelles features indiquent une fraude ?"
  - Exemples :
    - Si (tx_last_hour > 10) + (new_device = true) → Fraude probable
    - Si (amount_zscore > 5) + (vpn = true) → Fraude probable

- ÉTAPE 3 : Tester le modèle
  - 200 000 transactions de test (non vues pendant l'entraînement)
  - Vérifier : "Le modèle prédit-il correctement ?"
  - Métriques :
    - Précision : nombre de vraies fraudes bloquées sur le nombre de fraudes totales
    - Rappel : détection des vraies fraudes
    - F1-score : moyenne précision/rappel

### 4.2 Choisir le seuil de décision

Le modèle donne un score 0-100%, mais où mettre la barre ?

- Seuil de décision à 50% : risque qu'il y ait trop de vrais clients bloqués
- Seuil de décision à 99% : risque que trop de fraudes passent

**Hypothèses** :

- Score > 85% --> **BLOQUER** (haute confiance de fraude)
- Score 50-85% --> **REVUE MANUELLE** (un humain décide)
- Score < 50% --> **APPROUVER** (faible risque)

### 4.3 Versioning avec MLflow

**Le problème** : On entraîne plein de versions du modèle. Comment suivre ?
**La solution** : MLflow = "GitHub pour les modèles ML"
**Le principe** : les différents modèles (ceux archivés et ceux en production) sont stockés dans un MLFlow model registry

- On peut revenir en arrière si nouveau modèle problématique
- On sait quel modèle a fait quelle prédiction (traçabilité)
- On peut comparer les performances facilement

## 5. Déploiement en Production

### 5.1 Architecture de déploiement

```ascii
┌─────────────────────────────────────────┐
│     Transaction créée dans PostgreSQL   │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     Kafka (événement temps réel)        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│   Service ML (API FastAPI)              │
│   ├─ Calcul features (MongoDB)          │
│   ├─ Prédiction modèle (XGBoost)        │
│   └─ Décision                           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│   PostgreSQL (mise à jour statut)       │
│   ├─ Status = APPROUVE                  │
│   ├─ Status = BLOQUE                    │
│   └─ Status = EN ATTENTE VALIDATION     │
└─────────────────────────────────────────┘
```

**Déploiement Kubernetes** :

- 5 répliques (serveurs) pour haute disponibilité
- Load balancer (répartition de charge)
- Auto-scaling si charge augmente

## 5. Monitoring et Maintenance

### 5.1 Métriques à surveiller

**Métriques business** :

| Métrique | Cible | Alerte si |
| -------- | ----- | --------- |
| Taux de fraude détecté | 1-2% | > 3% ou < 0.5% |
| Taux de faux positifs | < 5% | > 10% |
| Taux de faux négatifs | < 15% | > 25% |

### 6.2 Model Drift (Dérive du modèle)

**Le problème** : Les fraudeurs évoluent, le modèle devient obsolète.
**Comment on détecte** : Test statistique (Kolmogorov-Smirnov). Pour chaque feature : Comparer distribution cette semaine vs distribution training set. Si > 5 features ont dérivé = ALERTE + Réentraînement automatique

### 6.3 A/B Testing (Tester un nouveau modèle)

**Le problème** : Nouveau modèle v3.4 développé. Est-il meilleur que v3.3 ?
**La solution** : Tester sur 50% du trafic

50% des transactions → Modèle v3.3 (actuel)
50% des transactions → Modèle v3.4 (nouveau)
Après 1 semaine, Comparer les performances. si v3.4 meilleur que v3.3, alors déploiement du modèle

## 7. Réentraînement Automatique

### 7.1 Quand réentraîner ?

**Déclencheurs automatiques** :
Tous les mois : Schedule Airflow : 1er du mois à 2h
OU
Détection de drift : Performance baisse > 5%

### 7.2 Pipeline de réentraînement (Airflow)

DAG Airflow "fraud_model_retraining"

- ÉTAPE 1 : Extraire données
  - MongoDB : Features des 90 derniers jours
  - PostgreSQL : Labels (fraude confirmée OUI/NON)
  - Export vers S3 (format Parquet)

- ÉTAPE 2 : Entraîner nouveau modèle
  - Spark : Préparation données
  - Python : XGBoost training
  - Sauvegarder dans MLflow

- ÉTAPE 3 : Validation
  - Tester sur transactions récentes
  - Si performance < modèle actuel → ANNULER
  - Sinon, continuer

- ÉTAPE 4 : Déploiement staging
  - Déployer en environnement de test
  - Tests automatisés (latence, format output)
  - Si OK, continuer

- ÉTAPE 5 : A/B test
  - 10% du trafic sur nouveau modèle
  - Monitoring performances
  - Si meilleur, promouvoir à 100%
