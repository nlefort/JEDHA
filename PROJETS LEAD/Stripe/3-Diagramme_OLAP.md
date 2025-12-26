# Conception de schéma pour un système OLAP
## Le Système OLAP

### Qu'est-ce que l'OLAP ?

**OLAP = Online Analytical Processing**

C'est l'entrepôt de données pour les **analyses** :

- Quel est le chiffre d'affaires par pays ce mois ?
- Quels clients sont à risque de fraude ?
- Quelle est la tendance des abonnements ?

### Différence OLTP vs OLAP

| Aspect | OLTP | OLAP |
| ------ | ---- | ---- |
| **Usage** | Opérations quotidiennes | Analyses et rapports |
| **Requêtes** | Simples, rapides (< 10ms) | Complexes, longues (secondes) |
| **Volume** | Millions de lignes | Milliards de lignes |
| **Mise à jour** | En temps réel | Batch (quotidien) |
| **Structure** | Normalisée (3NF) | Dénormalisée (star schema) |

### Le schéma en étoile

**Concept** : Au centre les **MESURES**, autour le **CONTEXTE**

**Table de FAITS** = Les chiffres à analyser

- Combien ? → transaction_amount
- Quel revenu net ? → net_revenue
- Combien de transactions ? → transaction_count

**Tables de DIMENSIONS** = Le contexte pour filtrer

- Quand ? → DIM_DATE (année, mois, jour, trimestre)
- Qui ? → DIM_COMMERCANT, DIM_CUSTOMER
- Où ? → DIM_GEOGRAPHIE (pays, région)


```mermaid
    erDiagram
    %% SCHÉMA EN ÉTOILE SIMPLIFIÉ
    %% Au centre : la table de FAITS (mesures)
    %% Autour : les DIMENSIONS (contexte pour analyser)
    
    FACT_TRANSACTION }o--|| DIM_DATE : "quand"
    FACT_TRANSACTION }o--|| DIM_COMMERCANT : "qui vend"
    FACT_TRANSACTION }o--|| DIM_CLIENT : "qui achete"
    FACT_TRANSACTION }o--|| DIM_GEOGRAPHIE : "ou"
    
    %% TABLE DE FAITS - Les mesures à analyser
    FACT_TRANSACTION {
        int fact_id PK "Cle primaire"
        int date_key FK "Lien vers date"
        int commercant_key FK "Lien vers marchand"
        int client_key FK "Lien vers client"
        int geographie_key FK "Lien vers pays"
        decimal transaction_montant "MESURE Montant"
        decimal frais_montant "MESURE Frais"
        decimal net_revenu "MESURE Revenu net"
        int transaction_count "MESURE Nombre 1"
        decimal fraude_score "MESURE Score fraude"
        boolean est_reussie "MESURE Succes oui-non"
    }
    
    %% DIMENSION TEMPS - Pour analyser par période
    DIM_DATE {
        int date_key PK "20241222"
        date full_date "2024-12-22"
        string jour_nom "Lundi"
        int jour_du_mois "22"
        int semaine_de_annee "51"
        string mois_nom "Decembre"
        int mois_nombre "12"
        string trimestre "Q4"
        int annee "2025"
        boolean est_weekend "Vrai ou Faux"
    }
    
    %% DIMENSION COMMERCANT - Dénormalisée pour performance
    DIM_COMMERCANT {
        int commercant_key PK "Cle surrogate"
        int commercant_id "ID commercant"
        string etps_nom "Nom entreprise"
        string secteur_activite "Secteur activite"
        string pays "Pays du marchand"
        string dimension "small medium large"
    }
    
    %% DIMENSION CLIENT - Segmentation
    DIM_CLIENT {
        int client_key PK "Cle surrogate"
        int client_id "ID client"
        string client_type "particulier entreprise"
        string segment "VIP regular occasional"
        string country "Pays du client"
    }
    
    %% DIMENSION GÉOGRAPHIE - Où se passent les transactions
    DIM_GEOGRAPHIE {
        int geography_key PK "Cle surrogate"
        string pays_code "FR US GB"
        string pays_name "France USA UK"
        string region "Europe Amerique Asie"
        string continent "Europe"
    }
```

### Exemple de requête analytique

Question : "Quel est le chiffre d'affaires par pays en décembre 2025 ?"

```sql
SELECT 
    g.pays_nom,
    SUM(f.revenu_net) as total_revenu,
    COUNT(f.transaction_count) as nb_transactions
FROM FACT_TRANSACTION f
JOIN DIM_GEOGRAPHIE g ON f.geographie_key = g.geographie_key
JOIN DIM_DATE d ON f.date_key = d.date_key
WHERE d.annee = 2025 
  AND d.mois_nombre = 12
GROUP BY g.pays_nom
ORDER BY total_revenu DESC;
```

**Résultat** :

| pays_nom | total_revenu | nb_transactions |
| ------------ | ------------- | ----------- |
| USA | 50,000,000 € | 2,500,000 |
| France | 12,000,000 € | 800,000 |
| UK | 8,500,000 € | 600,000 |

### Pourquoi dénormaliser en OLAP ?

**OLTP** : Normaliser pour éviter duplication
**OLAP** : Dénormaliser pour la **vitesse**