# Diagramme entité-relation (ERD) pour système OLTP

## Principe

### Qu'est ce que l'OLTP ?

OLTP = Online Transaction Processing

- Base de données qui gère les opérations quotidiennes : 
 - Un client paie -> `INSERT` dans transactions
 - Un remboursement → `UPDATE` du statut

### Choix outils

| Critère | PostgreSQL | Justification |
| ------- | ---------- | ------------- |
| ACID | Oui | Garantie la Cohérence |
| Performance | gère +10 000 transactions/sec | Latence faible |
| Réplication | standby automatique | Disponibilité des données en cas de panne |
| Maturité | +25 ans | Technologie éprouvée |

## Introduction au schéma

Ce diagramme ERD représente l'architecture d'un système de traitement de paiements à haute disponibilité, pour l'entreprise Stripe. L'objectif de cette modélisation est d'assurer une intégrité transactionnelle absolue tout en garantissant la traçabilité complète de chaque mouvement de fonds, de l'initiation du paiement jusqu'au règlement final ou aux éventuels litiges (retrofacturations).

### Tables essentielles

### Principe : Normalisation

### Règles de gestion et contraintes métier

*Règle 1: Unicité de l'identité*

- Règle: un même utilisateur ne peut posséder qu'un seul `compte` idenitifié par son adresse mail
- Implémentation: contraine `unique` sur le champ `email` de la table `COMPTE`

*Règle 2: Traçabilité des flux*

- Règle: une transaction financière ne doit jamais être supprimée. Toute modification de son cycle de vie (échec, succès, remboursement) doit être traçée par un changement de `statut` et une mise à jour du champ `updated_at`.
- Implémentation: interdiction des `DELETE` physiques, utilisation de `DateTime` pour l'audit

*Règle 3: Intégrité des montants*

- Règle: Tous les montants financiers doivent être stockés en centimes d'unité monétaire (exemple: 1000 pour 10.00 €)
- Implémentation: Utilisation du type `Interger` pour `amount_cents` afin de garantir une prédiction arithmétique de 100%

*Règle 4: Cohérence des remboursements*

- Règle: Le montant total cumulé des remboursements (`REMBOURSEMENTS`) liés à une transaction ne peut excéder le montant minimal (`amount_cents`) de cette `TRANSACTION`
- Implémentation: Logique de validation applicative (ou Trigger SQL) vérifiant la somme des remboursements par rapport à la transaction source.

*Règle 5: Sécurité bancaire (PCI-DSS)*

- Règle : Le numéro complet de la carte bancaire ne doit jamais être stocké en base de données. Seule la représentation masquée (`last4`) et le jeton sécurisé (`token`) sont autorisés.
- Implémentation : La table `METHODE_PAIEMENT` ne contient aucun champ pour le numéro de carte complet (`PAN`) ou le code de sécurité (`CVV`).

## Diagramme

```mermaid
---
Diagramme ERD - Système OLTP Stripe
---

erDiagram
%% ENTITÉS PRINCIPALES
    COMMERCANT ||--o{ TRANSACTION : "traite"
    CLIENT ||--o{ TRANSACTION : "effectue"
    TRANSACTION }o--|| DEVISE : "utilise"
    TRANSACTION ||--o| REMBOURSEMENT : "peut avoir (approuvé commerçant)"
    TRANSACTION ||--o| RETROFACTURATION : "peut avoir (suite litige)"
    CLIENT ||--o{ METHODE_PAIEMENT : "possède"
    METHODE_PAIEMENT }o--o{ TRANSACTION : "utilisée pour"
    COMMERCANT }o--|| PAYS : "situé en"
    CLIENT }o--|| PAYS : "situé en"    
    COMMERCANT ||--o{ PRODUITS : "possède et propose"
    CLIENT ||--o| COMPTE : "est profil" 
    COMMERCANT ||--o| COMPTE : "est profil"  
         
    
    %% COMMERCANT - Celui qui VEND (ex: Netflix, Amazon)
    COMMERCANT {
        uuid commercant_id PK "Identifiant unique"
        uuid compte_ID FK "ID de compte Stripe"        
        string business_name "Nom entreprise"
        string industry "Secteur d activite"
        string country_id FK "Pays"
        date registration_date "Date inscription"
        string status "active ou suspended"
        timestamp created_at "Date de creation"
        timestamp updated_at "Date de dernière modification"
    }
    
    %% CLIENT - Celui qui ACHETE (peut être individu ou etps)
    CLIENT {
        uuid customer_id PK "Identifiant unique"
        uuid compte_ID "ID de compte Stripe"
        string adresse        
        string nom_complet "nom complet ou raison sociale"
        string phone "Telephone optionnel"
        string expedition "adresse postale livraison"
        string customer_type "individual ou business"
        string code_pays FK "ISO" 
        timestamp created_at "Date de creation"
        timestamp updated_at "Date de dernière modification"            
    }
    
    %% MOYEN PAIEMENT - Comment le client paie
    METHODE_PAIEMENT {
        uuid payment_method_id PK "Identifiant unique"
        uuid customer_id FK "Propriétaire du moyen de paiement"
        string token UK "Token securise PCI-DSS"
        string marque_service "carte ou service paiement"
        string last4 "4 derniers chiffres carte"
        int exp_month_year "Date expiration pour validation"
        timestamp created_at "Date de creation"
        timestamp updated_at "Date de dernière modification"        
    }
    
    %% TRANSACTION - Le coeur du système
    TRANSACTION {
        uuid transaction_id PK "Identifiant unique"
        uuid merchant_id FK "Qui recoit l argent"
        uuid customer_id FK "Qui paie"
        int amount_cents "Montant paye en centimes"
        string currency_id FK "CODE ISO 3: EUR, USD..."
        string statut "ENUM: reussi-echoue-rembourse"
        int mountant_frais "Frais Stripe en cts"
        decimal taux_change "taux au moment T"
        uuid mode_paiement_id FK "Moyen paiement"
        datetime timestamp "Date et heure"
        string localisation_IP "basée sur adresseIP"
        decimal score_fraude "Score de fraude 0-1"
        timestamp created_at "Date de creation"
        timestamp updated_at "Date de dernière modification"        
    }
    
    %% REMBOURSEMENT - Remboursements
    REMBOURSEMENT {
        uuid refund_id PK "Identifiant unique"
        uuid transaction_id FK "Transaction remboursee"
        decimal amount_cents "Montant rembourse en cts"
        string reason "Raison du remboursement"
        datetime refund_date "Date remboursement"
        timestamp created_at "Date de creation"
        timestamp updated_at "Date de dernière modification"        
    }

    %% RETROFACTURATION - Remboursements
    RETROFACTURATION {
        uuid retrofacturation_id PK "Identifiant unique"
        uuid transaction_id FK "Transaction remboursee"
        decimal amount_cents "Montant rétrofacruté en cts"
        string reason "Raison du litige"
        datetime refund_date "Date rétrofacturation"
        timestamp created_at "Date de creation"
        timestamp updated_at "Date de dernière modification"        
    }    
    
    %% DEVISE - Devises (table de référence)
    DEVISE {
        uuid currency_id PK "Identifiant unique"
        string code "ISO USD EUR GBP"
        string symbole "dollar euro livre"
        timestamp created_at "Date de creation"
        timestamp updated_at "Date de dernière modification"        
    }

    %% PAYS - PAYS (table de référence)
    PAYS {
        uuid pays_ID PK "Identifiant unique"
        string code_pays "ISO"
        string code_fiscal FK "ISO"
        string country_name
        string region
        string timezone
        timestamp created_at "Date de creation"
        timestamp updated_at "Date de dernière modification"        
    }

    %% PRODUITS - PRODUITS (table de référence)
    PRODUITS {
        uuid produit_ID PK "identifiant unique"
        boolean actif "oui/non"
        decimal prix "prix par défaut"
        string description "description pour client"
        string nom "nom du produit"
        string code_fiscal "calcul TVA"
        date date_creation "date creation produit"
        date date_maj "date dernière MAJ"
        boolean expediable "oui/non"
        string dimension "dimension produit"
        timestamp created_at "Date de creation"
        timestamp updated_at "Date de dernière modification"
    }

    %% COMPTE - COMPTE
    COMPTE {
        uuid compte_id PK "identifiant_unique"
        string email UK "doit être unique"
        string mot_de_passe "jamais en texte clair"
        string type_compte "Enum: client/commerçant"
        boolean est_actif "oui/non"
        timestamp created_at "Date de creation"
        timestamp updated_at "Date de dernière modification"
    }

    %% 
```