# Guide de Présentation - Architecture de données Stripe

## Conexte et méthode

Le problème : Stripe traite des millions de transactions par jour. Comment gérer ces données pour :

- Traiter les paiements en temps réel (< 1 seconde)
- Analyser les revenus et détecter la fraude
- Respecter les réglementations (RGPD, PCI-DSS)

La solution : Une architecture en 3 systèmes complémentaires

1. **OLTP** : Base transactionnelle pour les opérations en temps réel
2. **OLAP** : Entrepôt analytique pour les analyses
3. **NoSQL** : Base flexible pour logs et machine learning

## Le Système OLTP

OLTP = Online Transaction Processing
C'est la base de données qui gère les opérations quotidiennes :

- Un client paie → INSERT dans transaction
- Un marchand consulte ses ventes → SELECT
- Un remboursement → UPDATE du statut

### Pourquoi PostgreSQL ?

| Critère | PostgreSQL | Justification |
| ------- | ---------- | -------------- |
| **ACID** | Oui | Garantit la cohérence (pas de paiement perdu) |
| **Performance** | 10,000+ transactions/sec | Gère la charge de Stripe |
| **Réplication** | Standby automatique | Haute disponibilité si panne |
| **Maturité** | 25+ ans | Technologie éprouvée |

### Les 4 tables essentielles

- COMMERCANTS (Les vendeurs) : Qui vend ?
- CLIENTS (Les acheteurs) : Qui achète ?
- METHODE_PAIEMENT : Comment c'est payé ?
- TRANSACTION (Le cœur du système) : Qui paie qui, combien, quand ?

### Normalisation OLTP (3NF)

Pourquoi normaliser ?

- Redondance : Pas de duplication des données
- Intégrité : Modifier un email = 1 seul UPDATE
- Cohérence : Les données sont toujours justes

Exemple conception dénormalisée :

```sql
-- MAUVAIS : Duplication
CREATE TABLE mauvaise_table_transaction (
    transaction_id INT,
    client_email TEXT,  -- Répété pour chaque transaction
    client_telephone TEXT   -- Répété pour chaque transaction
);
```

Conception normalisée:

```sql
-- BON : Normalisé
CREATE TABLE transaction (
    transaction_id INT,
    client_id INT  -- Référence FK, pas duplication
);

CREATE TABLE client (
    client_id INT,
    email TEXT,  -- Une seule fois
    telephone TEXT   -- Modifiable en 1 UPDATE
);
```

## Le Système OLAP

OLAP = Online Analytical Processing

C'est l'entrepôt de données pour les analyses :

- Quel est le chiffre d'affaires par pays ce mois ?
- Quels clients sont à risque de fraude ?
- Quelle est la tendance des abonnements ?

### Différence OLTP vs OLAP

| Aspect | OLTP | OLAP |
| ------ | ---- | ---- |
| Usage | Opérations quotidiennes | Analyses et rapports |
| Requêtes | Simples, rapides (< 10ms) | Complexes, longues (secondes) |
| Volume | Millions de lignes | Milliards de lignes |
| Mise à jour | En temps réel | Batch (quotidien) |
| Structure | Normalisée (3NF) | Dénormalisée (star schema) |

### Le schéma en étoile

Concept : Au centre les MESURES, autour le CONTEXTE

```ascii
                            DIM_DATE (Quand ?)
                                  |
DIM_COMMERCANT (Qui vend ?) -FAIT (Mesures) - DIM_CLIENT (Qui achète ?)
                                  |
                            DIM_GEOGRAPHIE (Où ?)
```

Table de FAITS = Les chiffres à analyser

- Combien ? → transaction_amount
- Quel revenu net ? → net_revenue
- Combien de transactions ? → transaction_count

Tables de DIMENSIONS = Le contexte pour filtrer

- Quand ? → DIM_DATE (année, mois, jour, trimestre)
- Qui ? → DIM_COMMERCANT, DIM_CUSTOMER
- Où ? → DIM_GEOGRAPHIE (pays, région)

### Pourquoi dénormaliser en OLAP ?

**OLTP** : Normaliser pour éviter duplication
**OLAP** : Dénormaliser pour la **vitesse**

```sql
-- OLTP : 3 jointures nécessaires
SELECT c.business_name, c.country, c.secteur_activite
FROM transaction t
JOIN commercant c ON t.commercant_id = c.commercant_id
JOIN country c ON c.country_id = c.country_id;

--  OLAP : Tout dans la dimension, 1 seule jointure
SELECT dc.nom_etps, dc.pays, dc.secteur_activite
FROM fact_transaction f
JOIN dim_commercant dc ON f.commercant_key = dc.commercant_key;
-- Plus rapide car pays est DUPLIQUÉ dans dim_commercant
```

## Le Système NoSQL

**NoSQL = Not Only SQL**

C'est une base flexible pour les données **non structurées** :

- Logs d'API (JSON variable)
- Sessions utilisateur (événements multiples)
- Features pour machine learning

### Pourquoi MongoDB pour Stripe ?

| Critère | Justification |
| ------- | ------------- |
| **Flexibilité** | Structure JSON adaptable sans migration |
| **Performance** | Latence < 10ms pour les lectures |
| **Scalabilité** | Sharding horizontal (ajout serveurs) |
| **Simplicité** | Pas de jointures complexes |
| **Cas d'usage** | Logs, sessions, features ML |

### Les 3 principes clés à retenir

1. **Embedding vs Referencing** : Dupliquer si toujours lu ensemble, référencer sinon
2. **Index intelligents** : Un index par champ de filtrage fréquent
3. **Intégration fluide** : Kafka (temps réel) + Spark (batch) pour connexion avec OLTP/OLAP

### Cas d'usage : Détection de fraude

Pipeline :

1. Transaction créée dans OLTP
2. MongoDB récupère l'historique utilisateur
3. Calcul des features (nombre transactions par heure, anomalies)
4. Modèle ML prédit le score de fraude
5. Décision : approuver ou bloquer

## Intégration des 3 Systèmes

### Le pipeline de données

2 types de flux :

1. BATCH (Nuit, 2h du matin)

OLTP > Extraction (quotidien) > Transformation (Spark, jointures, agrégats) → OLAP (Snowflake, analyses)

2. STREAMING (Temps réel, 24/7)

OLTP > CDC (Changements) > Kafka (bus) → NoSQL (MongoDB, logs, ML)

### Technologies choisies

| Composant | Technologie | Rôle | Justification |
| --------- | ---------- | ---- | ------------- |
| **OLTP** | PostgreSQL | Base transactionnelle | ACID, mature, performant |
| **OLAP** | Snowflake | Entrepôt analytique | Scalable, séparation compute/storage |
| **NoSQL** | MongoDB | Données non structurées | Flexible, performant sur JSON |
| **Streaming** | Kafka | Bus de messages | Haute disponibilité |
| **Transformation** | Spark | Traitement distribué | Parallélisme, gère gros volumes |
| **Orchestration** | Airflow | Scheduling ETL | logique de nouvelle tentative si échec |

### Exemple de job quotidien (Airflow)

```python
# Chaque nuit à 2h du matin
daily_etl = DAG('daily_olap_refresh', schedule='0 2 * * *')

# Étape 1 : Extraire les transactions du jour
extract = SparkOperator(
    task_id='extract_oltp',
    sql='SELECT * FROM transaction WHERE date = YESTERDAY'
)

# Étape 2 : Enrichir avec dimensions
transform = SparkOperator(
    task_id='transform',
    # Jointures avec commercant, client, geographie
)

# Étape 3 : Charger dans Snowflake
load = SnowflakeOperator(
    task_id='load_olap',
    sql='INSERT INTO fact_transaction ...'
)

extract >> transform >> load  # Ordre d'exécution
```

## Sécurité et conformité

1. **Chiffrement partout** : TLS (transit) + AES-256 (repos) + KMS (clés)
2. **Contrôle d'accès strict** : RBAC (rôles) + Least Privilege (minimum nécessaire)
3. **Tokenization obligatoire** : JAMAIS stocker les cartes en clair (PCI-DSS)
4. **RGPD respecté** : Droit à l'oubli + Portabilité + Consentement
5. **Monitoring temps réel** : détection des intrusions
6. **Catalogue des données** : Données sont suivies et déocumentées

## Intégration ML

1. **Features intelligentes** : 50 caractéristiques (vélocité, appareil, comportement, réseau)
2. **Temps réel** : Décision en < 100ms (imperceptible pour l'utilisateur)
3. **Apprentissage continu** : Réentraînement automatique (adaptation nouveaux patterns)
4. **A/B Testing** : Validation avant déploiement (pas de régression)

## Requêtes Exemples

### Requête OLTP (Simple, rapide)

**"Récupérer les 10 dernières transactions d'un client"**

```sql
SELECT transaction_id, amount, status, timestamp
FROM transaction
WHERE customer_id = 100
ORDER BY timestamp DESC
LIMIT 10;

-- Temps d'exécution : < 10ms (index sur customer_id)
```

### Requête OLAP (Complexe, analytique)

**"Top 10 des marchands par revenus en 2024"**

```sql
SELECT 
    dm.business_name,
    dm.industry,
    SUM(f.net_revenue) as total_revenue,
    COUNT(*) as nb_transactions
FROM fact_transaction f
JOIN dim_merchant dm ON f.merchant_key = dm.merchant_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.year = 2024
GROUP BY dm.business_name, dm.industry
ORDER BY total_revenue DESC
LIMIT 10;

-- Temps d'exécution : ~2 secondes (scan millions de lignes)
```

### Requête NoSQL (Flexible, agrégation)

**"Calculer le score de vélocité d'un utilisateur"**

```javascript
db.user_sessions.aggregate([
  // Filtrer les sessions de la dernière heure
  { $match: { 
      user_id: "usr_456",
      timestamp: { $gte: new Date(Date.now() - 3600000) }
  }},
  
  // Compter les transactions
  { $group: {
      _id: "$user_id",
      tx_count: { $sum: 1 },
      total_amount: { $sum: "$amount" }
  }}
]);

// Résultat : { tx_count: 12, total_amount: 5000 }
// Si > 10 tx/heure → ALERTE FRAUDE
```
