
# :dart: Analyse plateforme de jeux vidéos

## :rocket: Objectif du projet

Le projet consiste à réaliser une analyse globale des jeux disponibles sur Steam (plateforme en ligne).
Les objectifs sont les suivants :

- Comprendre le marché et les tendances du jeu vidéo
- Identifier les facteurs influençant la popularité et les ventes d’un jeu.
- Analyser le marché mondial du jeu vidéo à différents niveaux (analyse macro, analyse des genres, analyse des plateformes)

*A des fins pédagogiques, il est demandé que l'intégralité du projet soit réalisé sous [Databricks](https://community.cloud.databricks.com/login.html?tuuid=8db9422d-a712-44ed-aacf-4945c8cafb3f). Les notebooks associés à ce travail sont publics*

## :brain: Pipeline de traitement

[Accès au jeu de données](s3://full-stack-bigdata-datasets/Big_Data/Project_Steam/steam_game_output.json)

La collecte et le traitement des données suivent la progression suivante :

- 1- Préparation des données : [Notebook - Préparation_des_données](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/1757644669073569/811571160453303/3378110399057887/latest.html)

- 2- Visualisation de la donnée : [Notebook - visualisation_données](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/1757644669073569/1637098918164767/3378110399057887/latest.html)

### Architecture et traitement des données

- Charger les données depuis S3
- Lecture du schéma

dans le schéma,

```text
<code>|-- data: struct (nullable = true)
...
|-- id: string (nullable = true)</code>
```

id est une colonne du dataframe au même niveau que data, pas à l'intérieur de la structure data. Chaque ligne du dataframe contient une colonne data (avec tous les champs imbriqués) et une colonne id, indépendante de data.

- Nettoyage & normalisation
  - Transformation des prix en numérique (.cast("double")): discount price, initial price
  - Conversion des dates (to_date):  release_date
  - réalisation d'un df_principal et de df_secondaires

#### Désimbrication des données

##### Avant : DataFrame initial

|        data        |
|--------------------|
| {appid, categories, ccu, developer, ...} |
| {appid, categories, ccu, developer, ...} |

```text
data = struct (objet)

|-- data: struct (nullable = true)  
| |-- appid: long (nullable = true) -> ceci est une colonne simple, contenant un nombre entier (long=int) et peut être nul (nullable=true)  
| |-- categories: array (nullable = true) -> ceci est un tableau/liste imbriqué (array) 
| | |-- element: string (containsNull = true) -> chaque élément est une chaîne de caractère 
... 
| |-- platforms: struct (nullable = true) -> ceci est un objet structuré, un dictionnaire (strcut)  
| | |-- linux: boolean (nullable = true) -> chaque clé renvoi renvoie une valeur oui/non  
| | |-- mac: boolean (nullable = true)  
| | |-- windows: boolean (nullable = true) </code>
```

###### Étape 1 : création d'un df principal

```text
df_main= df.select(
    col("data.appid"),
    col("data.categories"),
    col("data.ccu"),
    col("data.developer"),
    ...
) 
```

*Résultat* : DataFrame imbriqué avec 1 ligne unique par jeu

| appid | categories                    | ccu | developer | ... |
|-------|-------------------------------|-----|-----------|---- |
| 10    | [Multi-player, PvP, ...]      | 13990 | Valve | ... |
| 1000  | [Single-player, Adventure]    | 500   | Indie  | ... |

--> explode des colonnes "platforms" : Windows, Linux, MacOs

###### Étape 2 : création de df secondaires

Variables : categorie, langues, genre, tags

Résultat : une ligne = 1 catégorie du jeu. si le jeu a 4 catégories, 4 lignes sont créées.

| appid | category          |
|-------|-------------------|
| 10    | Multi-player      |
| 10    | PvP               |
| 10    | Action            |
| 1000  | Single-player     |
| 1000  | Adventure         |

- Nettoyage des valeurs nulles/incomplètes : Prix (conversion en € à la place des cts)

- Enregistrer format parquet : df principal, df secondaires

*Remarque : Il a été fait le choix d'avoir un Dataframe principal et des dataframes secondaires afin notamment d'avoir une plus grande vitesse de calculs. Ce choix est cohérent pour une exploration de données. Dans le cas où le projet devrait se poursvuivre sur des modèles d'apprentissage automatique, il conviendra de réunir les deux dataframe.*

## :toolbox: Technologies & outils

| Domaine    | Outils                   |
| ---------- | ---------|
| Stockage des datasets | s3 |
| Calculs distribués, visualisations, agrégations, dashborads | PySpark, Databricks |

## :compass: Roadmap

- [x] Collecter les données depuis s3

- [x] Charger les données dans Databricks

- [x] Identifier le schéma des données

- [x] Désimbrication du schéma

- [x] Réalisation d'un dataset principal

- [x] Réalisation de quatre datasets secondaires

- [x] Ananlyse et visualisation les résultats sur les dashboards Databricks

## :arrow_forward: Installation, exécution, tutlisation

### 0. Prérequis

Pas de prérequis

### 1. Lancer le notebook

- 1- Préparation des données : [Notebook - Préparation_des_données](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/1757644669073569/811571160453303/3378110399057887/latest.html)

- 2- Visualisation de la donnée : [Notebook - visualisation_données](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/1757644669073569/1637098918164767/3378110399057887/latest.html)

## :busts_in_silhouette: Auteurs

Projet développé par [Nadège Lefort](https://github.com/nlefort)

*La réalisation de ce projet s'inscrit dans le cadre de la [formation Data Scientist](https://www.jedha.co/formations/formation-data-scientist) développé par [Jedha](https://www.jedha.co/), en vue de l'obtention de la certification professionnelle de niveau 6 (bac+4) enregistrée au RNCP : [Concepteur développeur en science des données](https://www.francecompetences.fr/recherche/rncp/35288/).*
