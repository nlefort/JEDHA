# Plan de sécurité et conformité Stripe

## 1. Pourquoi la sécurité est importante chez Stripe ?

### 1.1 Les risques

Stripe traite des données sensibles: Numéros de cartes bancaires, données personnelles (emails, adresses), transactions financières (qui paie qui, combien)

Si ces données sont volées ou compromises: fraude bancaire (utilisation frauduleuse des cartes), vol d'identité, perte de confiance des clients

### 1.2 Les 3 objectifs de sécurité

```ascii
          CONFIDENTIALITÉ
        (Seules les personnes
         autorisées voient les données)
                 │
                 ├────────────────┐
                 │                │
            INTÉGRITÉ        DISPONIBILITÉ
      (Données exactes      (Données accessibles
       et non modifiées)     quand on en a besoin)
```

## 2. Les 5 Couches de Protection

### Couche 1 : Chiffrement

**Le principe** : Rendre les données illisibles sans la clé de déchiffrement.

#### Chiffrement en transit (TLS)

**Quand** : Quand les données voyagent sur le réseau

```ascii
Client ──[HTTPS/TLS]──> API Stripe ──[TLS]──> Base de données
        (chiffré)                    (chiffré)
```

**Pourquoi** : Si quelqu'un intercepte les données sur le réseau, il voit des données illisible.

#### Chiffrement au repos (AES-256)

**Quand** : Quand les données sont stockées sur disque

```ascii
Disque dur PostgreSQL : [encrypted_data.db]
├─ transaction_123 : "xK9mL2p..." (chiffré)
├─ customer_456 : "aZ8nQ5r..." (chiffré)
└─ merchant_789 : "bY7oP4t..." (chiffré)
```

**Pourquoi** : Si quelqu'un vole le disque dur physique, les données sont inutilisables.

### Couche 2 : Contrôle d'accès (RBAC)

**Le principe** : Chaque personne n'a accès qu'à ce dont elle a **vraiment besoin**.

#### Les rôles chez Stripe

| Rôle | Peut faire | Ne peut PAS faire |
| ---- | --------- | ----------------- |
| **Data Analyst** | Lire les données agrégées (OLAP) | Modifier les données, voir les données sensibles clients (mail, cartes bancaires) |
| **Data Engineer** | Lire/écrire dans staging, développer pipelines | Accéder à la production, voir données sensibles |
| **ML Engineer** | Lire features ML, déployer modèles | Accéder aux cartes bancaires brutes |
| **Security Auditor** | Lire tous les logs d'audit | Modifier quoi que ce soit |
| **Admin** | Tout | (contrôlé et audité) |

### Couche 3 : Protection des données bancaires (PCI-DSS)

**PCI-DSS** = Payment Card Industry Data Security Standard  
**C'est quoi** : Les règles **obligatoires** pour manipuler des cartes bancaires.

#### Tokenization

**JAMAIS stocker** :

- Le numéro complet de carte (4242 4242 4242 4242)
- Le CVV (123)
- Le code PIN

**À la place** : Tokenization

```ascii
Client tape sa carte :
  Numéro : 4242 4242 4242 4242
  CVV : 123
       ↓
Service de tokenization (Vault sécurisé)
       ↓
Stripe stocke uniquement :
  Token : "tok_abc123xyz"     < Inutile si volé
  Last4 : "4242"              < 4 derniers chiffres (OK)
  Brand : "Visa"              < Marque (OK)
```

**Pourquoi c'est sécurisé** :

- Le token "tok_abc123xyz" ne peut être utilisé que par Stripe
- Si un pirate vole la base de données, il n'a que des tokens (inutiles)
- Le vrai numéro de carte est stockée ailleurs

### Couche 4 : Conformité RGPD et autres réglementations en vigueur

**RGPD** = Règlement Général sur la Protection des Données  
**C'est quoi** : Loi européenne qui protège les données personnelles.

#### Les 3 droits principaux

**Droit à l'oubli** : Si un client demande la suppression de ses données,

- son identité est vérifiée pour s'assurer que c'est bien lui qui en fait la demande
- ses données personnelles sont anonymisées (on garde les données mais on ne peut plus remonter à la personne)
- ses transactions sont conservées mais ne sont pas liées à son compte

**Droit à la portabilité** : Le client peut demander toutes ses données dans un format lisible (JSON, CSV).

**Consentement explicite** : On doit demander explicitement l'autorisation avant de,

- Utiliser les données pour du marketing
- Partager les données avec des tiers
- Faire du profilage (ML)

### 2.5 Couche 5 : Audit et Monitoring

**Le principe** : Tout doit être tracé, et les logs doivent être immutables (non modifiables).

- Stocké dans AWS
- Impossible de modifier ou supprimer
- Si un pirate compromet le système, il ne peut pas effacer ses traces

#### Monitoring en temps réel (SIEM)

**SIEM** = Security Information and Event Management

**Ce qu'on surveille** :

- Tentatives de connexion échouées
- Requêtes à données sensibles
- Transfert de données
- Accès hors horaires

**Exemple de détection d'intrusion** :

Notre outil détecte :

- 15:30 : je me connecte depuis Paris (OK, habituel)
- 15:35 : j'accède à 50 emails clients (OK, dans mon rôle)
- 15:40 : j'accède à 1000 emails en 2 minutes (SUSPECT)
=> ALERTE
- Action automatique : Suspendre le compte temporairement, alerter le manager et la sécurité

## 3. Outils de Sécurité

### 3.1 Ce qu'on surveille

**Métriques de sécurité** :

- Tentatives connexion échouées
- Requêtes API non autorisées
- Transfert données sortant

### 3.2 Gouvernance par le data catalog

Pour éviter que l'architecture ne devienne une "boîte noire", un Catalogue de Données (type DataHub) est implémenté en couche transverse.

- Moissonnage (Harvesting) : Il scanne les métadonnées de PostgreSQL, Snowflake et MongoDB sans jamais accéder au contenu des transactions.
- Lignage (Lineage) : Il permet de visualiser le trajet d'une donnée, par exemple : Table Transaction (OLTP) ➔ Job Spark ➔ Table de Faits (OLAP).
- Conformité facilitée : En cas de demande de suppression RGPD, le catalogue indique instantanément tous les endroits où l'email du client est stocké.

### Les 5 points clés à retenir

1. Chiffrement partout : TLS (transit) + AES-256 (repos) + KMS (clés)
2. Contrôle d'accès strict : RBAC (rôles) + Least Privilege (minimum nécessaire)
3. Tokenization obligatoire : JAMAIS stocker les cartes en clair (PCI-DSS)
4. RGPD respecté : Droit à l'oubli + Portabilité + Consentement
5. Monitoring temps réel : détection des intrusions
6. Gouvernance par le data catalog : les données sont documentées et suivies
