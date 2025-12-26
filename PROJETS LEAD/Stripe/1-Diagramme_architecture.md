# Diagramme architecture

## Organisation de l'architecture et des flux

![Stripe](./Stripe-architecture-complete.drawio.svg)

## Principes de conception

### Stratégie de stockage hybride

Utilisation de solutions hybrides :

- PostgreSQL (OLTP) garantit qu'aucune transaction n'est perdue (ACID).

- Snowflake (OLAP) permet aux analystes de lancer des requêtes lourdes sans ralentir les paiements en direct.

- MongoDB (NoSQL) offre la flexibilité nécessaire pour capturer des données de navigation variées sans figer le schéma.

### Stratégie d'intégration par les changements

Utilisation de la Capture de Données Modifiées (CDC) avec Debezium : 

- On ne prend que le "delta" : Si sur 1 million de clients, seulement 10 nouveaux paiements on été mis à jour depuis la dernière synchronisation, le pipeline ne va lire et transporter que les 10 lignes modifiées.

### Strtégie de modélisation OLAP

Choix d'utiliser le modèle de schéma en étoile :

- Efficacité : En dénormalisant les données (comme le nom du pays ou la catégorie du marchand), on réduis le nombre de jointures nécessaires.

- Scalabilité : Cela permet à Stripe de stocker des années d'historique (milliards de lignes) tout en gardant des rapports rapides.

### Strétégie sécurité et ML

- Conformité : la tokenisation et le chiffrement des données sont des prérequis pour des entreprises comme Stripe.
- Machine Learning : Le réentraînement via Airflow et l'utilisation de test A/B permettent de faire évoluer continuellement les modèles ML et limiter les risques de fraudes

### Stratégie de gouvernance

Utilisation d'un outil de data catalogue qui vient scanner les métadonnées de chaque composant :

**1. Dans les bases de données**
Le catalogue se connecte via des connecteurs aux trois systèmes conçus :

- PostgreSQL (OLTP) : Il répertorie les tables TRANSACTION, CLIENT, etc., avec leurs types de colonnes et leurs contraintes.
- Snowflake (OLAP) : Il documente le schéma en étoile (ex: définition du champ net_revenue).
- MongoDB (NoSQL) : Il aide à comprendre la structure des documents JSON qui, par nature, n'ont pas de schéma fixe.

**2. Dans le pipeline**
Le catalogue s'intègre aux outils de mouvement de données pour créer le Lineage (lignage) :

- Airflow & Spark : Le catalogue enregistre quel job Spark a transformé la donnée de PostgreSQL pour l'envoyer vers Snowflake.
- Kafka : Il permet de savoir quels sujets (topics) alimentent le modèle de Machine Learning.

**3. Dans le flux de travail**
Le catalogue devient l'interface entre tes systèmes techniques et tes utilisateurs :

- Data Engineers : Pour voir l'impact d'une modification de colonne dans l'OLTP sur les rapports de l'OLAP (Analyse d'impact).
- Data Scientists : Pour trouver quelles features sont disponibles dans MongoDB pour l'entraînement du modèle de fraude.
- Data Analysts : Pour vérifier la certification d'une table dans Snowflake avant de créer un rapport financier.