
# Étape 1 : Préparation des données

Lien databricks : [Notebook - Préparation_des_données](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/1757644669073569/811571160453303/3378110399057887/latest.html)

## Charger les données depuis S3

<code>spark
sc=spark.sparkContext</code>
-> non nécessaire dans environnement Databricks car session spark crée automatiquement quand le notebook démarre

## lecture du schéma

dans le schéma,

<code>|-- data: struct (nullable = true)
...
|-- id: string (nullable = true)</code>

id est une colonne du dataframe au même niveau que data, pas à l'intérieur de la strcutre data.
chaque ligne du dataframe contient une colonne data (avec tous les champs imbriqués)
et une colonne id, indépendante de data

##  Nettoyage & normalisation
 - Transformation des prix en numérique (.cast("double")):  discount, price, initial price
 - Conversion des dates (to_date):  release_date
 - réalisation d'un df_main


**Avant : DataFrame initial**


|        data        |
|--------------------|
| {appid, categories, ccu, developer, ...} |
| {appid, categories, ccu, developer, ...} |


data = struct (objet)
<code>
|-- data: struct (nullable = true)  
| |-- appid: long (nullable = true) -> ceci est une colonne simple, contenant un nombre entier (long=int) et peut être nul (nullable=true)  
| |-- categories: array (nullable = true) -> ceci est un tableau/liste imbriqué (array) 
| | |-- element: string (containsNull = true) -> chaque élément est une chaîne de caractère 
... 
| |-- platforms: struct (nullable = true) -> ceci est un objet structuré, un dictionnaire (strcut)  
| | |-- linux: boolean (nullable = true) -> chaque clé renvoi renvoie une valeur oui/non  
| | |-- mac: boolean (nullable = true)  
| | |-- windows: boolean (nullable = true) </code>


**Étape 1 : création d'un df principal**

<code> df_main= df.select(
    col("data.appid"),
    col("data.categories"),
    col("data.ccu"),
    col("data.developer"),
    ...
) </code>

Résultat : DataFrame imbriqué avec 1 ligne unique par jeu

| appid | categories                    | ccu | developer | ... |
|-------|-------------------------------|-----|-----------|---- |
| 10    | [Multi-player, PvP, ...]      | 13990 | Valve | ... |
| 1000  | [Single-player, Adventure]    | 500   | Indie  | ... |


--> explode des colonnes "platforms" : Windows, Linux, MacOs

**Étape 2 : création de df secondaires**

Variables : categorie, langues, genre, tags

Résultat : une ligne = 1 catégorie du jeu. si le jeu a 4 catégories, 4 lignes sont créées.

| appid | category          | 
|-------|-------------------|
| 10    | Multi-player      | 
| 10    | PvP               | 
| 10    | Action            | 
| 1000  | Single-player     | 
| 1000  | Adventure         | 


- Nettoyage des valeurs nulles/incomplètes
    * Prix (conversion en € à la place des cts)

- Enregistrer format parquet
    * df principal
    * df secondaire : genres de jeux vidéos
    * df secondaire : langues des jeux vidéos
    * df secondaire : mot clés associés aux jeux vidéos

# Etape 2 : visualisation des données

Lien databricks : [Notebook - visualisation_données](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/1757644669073569/1637098918164767/3378110399057887/latest.html)

## Analyses macro
**Période étudiée** : après des années Covid record, les chiffres de ventes de jeux vidéos se sont tassées légèrement.

**Éditeurs les plus prolifiques** : Un grand nombre d'éditeurs indépendants

**Langues représentées** : L'anlglais, langue la plus fréquente 

**Prix des jeux vidéos**: La moitié des jeux à moins de 5 €

**Age requis** : près de 99% des jeux sont tout publics

**Genre** : Le jeux vidéos un passe-temps plutôt qu'une passion

**Catégories**: Jouer seul, n'importe où et n'importe quand

**Palteforme**: Windows incontournable

## Analyses par genres

**Genres les plus populaires** : Les genres de jeux les mieux notés ne sont pas forcément les plus représentés

**Combinaison de genre et de catégories les mieux notées** : Le principe de joueur unique prédominant

**Genre de jeux réalisés par éditeur** : la plupart déjà sur les créneaux "casual"

**Prix médian par genre** : entre 4 et 6 € par jeu

## Synthèse

Voir aussi : [Bilan du marché français 2024](https://www.sell.fr/sites/default/files/essentiel-jeu-video/def_ejv_mars_2025.pdf)

