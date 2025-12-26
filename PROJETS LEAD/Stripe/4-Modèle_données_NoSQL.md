# Modèle de Données NoSQL - MongoDB

## 1. Pourquoi utiliser NoSQL ?

### 1.1 Le problème avec SQL (relationnel)

Si je veux stocker les actions d'un utilisateur sur le site Stripe :

- Il visite une page
- Il clique sur un bouton
- Il remplit un formulaire
- Il effectue un paiement

**Avec PostgreSQL (SQL)**, nous devrions créer :

```sql
TABLE session (session_id, user_id, start_time)
TABLE events (event_id, session_id, event_type, timestamp, page, button, field...)
```

**Le problème** :

- Chaque utilisateur a un **nombre différent d'événements** (3, 10, 100...)
- Chaque événement a des **champs différents** (page_view a "page", click a "button")
- Pour ajouter un nouveau type d'événement, il faut **modifier la structure** de la base

### 1.2 La solution NoSQL (MongoDB)

Avec MongoDB, on stocke tout dans **un seul document JSON flexible** :

```json
{
  "session_id": "sess_123",
  "user_id": "usr_456",
  "start_time": "2024-12-22T10:30:00Z",
  "events": [
    {"type": "page_view", "page": "/checkout"},
    {"type": "click", "button": "subscribe"},
    {"type": "payment", "amount": 15.99, "success": true}
  ]
}
```

Les avantages :

- Structure flexible : Chaque événement peut avoir ses propres champs
- Tout regroupé : Une seule lecture pour avoir toute la session
- Évolutif : Ajouter un nouveau type d'événement ? Juste ajouter un objet JSON
- Performance : Pas de jointures complexes

## 2. Les 4 Collections MongoDB de Stripe

| Collection | Information stockée | Pourquoi NoSQL | Usage |
| ---------- | ------------------- | -------------- | ----- |
| `user_sessions` | Comportement utilisateur sur site/app Stripe | Chaque session a un nombre variable d'évènements. Chaque evènement à des champs différents | Analyser le parcours client, détecter comportements suspects, personnaliser expérience utilisateur |
| `api_logs` | Logs de toutes les requêtes API (qui appelle quoi, quand, résultat) | Logs ont une structure variable selon le type d'API appelée. Logs générés en millions | Analyse des usages, monitoring performances (API qui devient lente) |
| `fraud_ml_features` | "Features" calculées pour détecter la fraude avec le machine learning | Evolution constante des features | Entraîner les modèles ML, détection fraude temps réel, analyse blocage transaction |
| `customer_feedback` | Tickets de support, avis clients, enquêtes de satisfaction | Donnée non structurée avec contenu et longueur variable | Gérer le support client, analyser la satisfaction, identifier les problèmes récurrents |

*Exemple user_session :*

```json
{
  "session_id": "sess_abc123",
  "user_id": "usr_456",
  "start_time": "2024-12-22T10:30:00Z",
  "end_time": "2024-12-22T10:45:00Z",
  
  "device": {
    "type": "mobile",
    "os": "iOS"
  },
  
  "location": {
    "country": "FR",
    "city": "Paris"
  },
  
  "events": [
    {"type": "page_view", "page": "/checkout", "time": "10:30:15"},
    {"type": "click", "element": "card_number", "time": "10:31:00"},
    {"type": "payment", "amount": 15.99, "success": true, "time": "10:32:00"}
  ]
}
```

*Exemple api_logs :*

```json
{
  "timestamp": "2024-12-22T10:32:15Z",
  "endpoint": "/v1/charges",
  "method": "POST",
  "merchant_id": "mch_xyz789",
  
  "request": {
    "amount": 5000,
    "currency": "eur",
    "customer": "cus_abc123"
  },
  
  "response": {
    "status_code": 200,
    "response_time_ms": 145,
    "success": true
  }
}
```

*Exemple fraud_ml_features :*

```json
{
  "transaction_id": "txn_123",
  "computed_at": "2024-12-22T10:32:00Z",
  
  "velocity": {
    "transactions_last_hour": 3,
    "transactions_last_24h": 12,
    "total_amount_24h": 15000
  },
  
  "device": {
    "is_new_device": false,
    "device_reputation_score": 0.85
  },
  
  "behavior": {
    "unusual_time": false,
    "unusual_location": false,
    "amount_unusual": true
  },
  
  "fraud_prediction": {
    "fraud_probability": 0.08,
    "decision": "approved"
  }
}
```

*Exemple customer_feedback* :

```json
{
  "feedback_id": "fbk_789",
  "customer_id": "usr_abc123",
  "type": "support_ticket",
  "created_at": "2024-12-22T11:00:00Z",
  
  "content": {
    "subject": "Demande de remboursement",
    "message": "Je souhaite un remboursement pour la transaction txn_123..."
  },
  
  "sentiment": "negative",
  "status": "open",
  
  "conversation": [
    {
      "time": "2024-12-22T11:05:00Z",
      "from": "support_agent",
      "message": "Nous étudions votre demande..."
    }
  ]
}
```

## 3. Stratégies de Conception

### 3.1 Embedding (imbrication) vs Referencing (référencement)

| Type Conception | Définition | Avantages | Cas d'utilisation |
| --------------- | ---------- | --------- | ----------------- |
| Embedding | Tout dans un seul document | Pas de jointures, une seule lecture pour tout récupérer | Pour des données petites,  toujours lues ensemble (évènements/session) et pas réutilisées ailleurs |
| Referencing | Pointer vers un autre document | Pas de duplication de données | Pour des données existantes, grandes, réutilisées dans plusieurs documents |

**EMBEDDING**

```json
{
  "session_id": "sess_123",
  "events": [
    {"type": "page_view", "page": "/checkout"},
    {"type": "click", "button": "subscribe"}
  ]
}
```

**REFERENCING**

```json
{
  "fraud_features_id": "feat_123",
  "transaction_id": "txn_456",  // <- Référence vers PostgreSQL
  "fraud_probability": 0.08
}
```

**Recommandations pour Stripe** :

| Collection | Choix | Justification |
| --------- | ----- | ------------- |
| `user_sessions` | EMBEDDING pour events | Events spécifiques à cette session |
| `fraud_ml_features` | REFERENCING pour transaction_id | Transaction existe dans PostgreSQL |
| `customer_feedback` | EMBEDDING pour conversation | Conversation spécifique au ticket |
| `api_logs` | REFERENCING pour merchant_id | Marchand existe dans PostgreSQL |

### 3.2 Index : Accélérer les recherches

**Problème** : Sans index, MongoDB doit scanner tous les documents pour trouver ce que vous cherchez.
**Principe** : On crée un index sur chaque champ qu'on utilise pour filtrer ou trier.
**Exemple** : Trouver toutes les sessions d'un utilisateur

- Sans index : Scanner 10 millions de documents (lent)
- Avec index : Accès direct aux documents de cet utilisateur (rapide)

**Création des index :**

```javascript
// Index sur user_id pour recherches fréquentes
db.user_sessions.createIndex({ "user_id": 1 });

// Index composite pour recherches temporelles
db.user_sessions.createIndex({ 
  "user_id": 1, 
  "start_time": -1  // -1 = ordre décroissant (plus récent d'abord)
});

// Index TTL (durée de vie de l'index): suppression automatique après 30 jours
db.api_logs.createIndex(
  { "created_at": 1 }, 
  { expireAfterSeconds: 2592000 }  // 30 jours en secondes
);
```

### 3.3 Sharding : Distribuer les données

**Problème** : Si on a 1 milliard de documents, une seule machine ne suffit pas.
**Solution** : Sharding = découper les données sur plusieurs serveurs.

```ascii
Cluster MongoDB (3 shards)

Shard 1                Shard 2                Shard 3
├─ merchant_id         ├─ merchant_id         ├─ merchant_id
│  hash(mch_001)       │  hash(mch_250)       │  hash(mch_500)
├─ Sessions            ├─ Sessions            ├─ Sessions
│  (33% données)       │  (33% données)       │  (33% données)
```

**Fonctionnement** :

1. Choisir une clé de partitionnement (ex: commercant_id)
2. MongoDB calcule une séparation du commercant_id
3. Les données sont automatiquement réparties sur les 3 serveurs

**Avantage** : On peut gérer 10x, 100x, 1000x plus de données en ajoutant des serveurs.

## 4. Intégration avec OLTP et OLAP

### 4.1 Comment les données arrivent dans MongoDB ?

**Flux temps réel** (Streaming) =
PostgreSQL (OLTP) > Kafka (bus) → MongoDB (NoSQL)

Exemple :

1. Transaction créée dans PostgreSQL
2. Kafka reçoit l'événement en < 1 seconde
3. MongoDB consomme et stocke les features ML

**Flux batch** (Quotidien) =
MongoDB (NoSQL) > Spark (Transform) > Snowflake (OLAP)

Exemple :

1. Chaque nuit, Spark lit les sessions MongoDB
2. Agrège les statistiques (nb sessions, durée moyenne)
3. Charge dans Snowflake pour analyses


### 4.2 Pourquoi cette séparation ?

| Système | Rôle | Exemple de données |
| ------- | ---- | ----------------- |
| **PostgreSQL (OLTP)** | Opérations | "Transaction txn_123 créée" |
| **MongoDB (NoSQL)** | Enrichissement | "User a fait 12 transactions en 1h" (feature ML) |
| **Snowflake (OLAP)** | Analyses | "Revenus par pays ce mois" |


## 5. Performance et Scalabilité

### 5.1 Métriques de performance

- Latence lecture | < 10ms | 8ms (P95) |
- Latence écriture | < 50ms | 35ms (P95) |
- Disponibilité | 99.99% | 99.97% |

### 5.2 Comment on garantit la performance ?

**1. Réplication (3 copies)** :

```ascii
Primary (écriture) ──┬──> Secondary 1 (lecture)
                     └──> Secondary 2 (lecture)
```

- Si le Primary tombe, un Secondary devient Primary automatiquement
- Les lectures peuvent se faire sur les Secondary (pas d'impact sur les écritures)

**2. Index optimisés** :

- Chaque requête fréquente a son index
- Index composites pour requêtes complexes

**3. Sharding** :

- Distribution sur 3 serveurs minimum
- Ajout de serveurs si besoin (scaling horizontal)

## 6. Exemples de Requêtes

### 6.1 Requête simple : Toutes les sessions d'un utilisateur

```javascript
// Trouver toutes les sessions de usr_456 des 7 derniers jours
db.user_sessions.find({
  "user_id": "usr_456",
  "start_time": { 
    $gte: new Date("2025-12-15")  // Depuis le 15 décembre
  }
});
```

**Ce qu'on obtient** : Liste de toutes ses sessions avec leurs événements.

### 6.2 Requête d'agrégation : Compter les transactions par heure

```javascript
// Combien de transactions chaque heure aujourd'hui ?
db.user_sessions.aggregate([
  // 1. Filtrer aujourd'hui uniquement
  {
    $match: {
      "start_time": {
        $gte: new Date("2025-12-26T00:00:00Z")
      }
    }
  },
  
  // 2. Dérouler les événements
  { $unwind: "$events" },
  
  // 3. Garder uniquement les paiements
  {
    $match: {
      "events.type": "payment"
    }
  },
  
  // 4. Grouper par heure
  {
    $group: {
      _id: { $hour: "$events.time" },  // Extraire l'heure
      count: { $sum: 1 }                // Compter
    }
  }
]);
```

**Résultat** :

```json
[
  { "_id": 9, "count": 1250 },   // 9h : 1250 transactions
  { "_id": 10, "count": 2100 },  // 10h : 2100 transactions
  { "_id": 11, "count": 1890 }   // 11h : 1890 transactions
]
```

### 6.3 Requête géospatiale : Transactions autour de Paris

```javascript
// Toutes les sessions dans un rayon de 50km de Paris
db.user_sessions.find({
  "location.coordinates": {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [2.3522, 48.8566]  // Paris [longitude, latitude]
      },
      $maxDistance: 50000  // 50km en mètres
    }
  }
});
```

**Usage** : Détecter des transactions suspectes (ex: carte utilisée à Paris puis à Londres 10 min après).
