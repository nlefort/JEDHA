
# Étape 1 : Préparation des données

Lien databricks : [Notebook - Préparation des données](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/1757644669073569/811571160453303/3378110399057887/latest.html)

## Charger les données depuis S3

spark
sc=spark.sparkContext
-> non nécessaire dans environnement Databricks car session spark crée automatiquement quand le notebook démarre

## lecture du schéma

dans le schéma,/
|-- data: struct (nullable = true)

...

|-- id: string (nullable = true)

id est une colonne du dataframe au même niveau que data, pas à l'intérieur de la strcutre data.
chaque ligne du dataframe contient une colonne data (avec tous les champs imbriqués)
et une colonne id, indépendante de data

##  Nettoyage & normalisation
 - Transformation des prix en numérique (.cast("double"))

 discount, price, initial price

 - Conversion des dates (to_date)

 release_date

 - réalisation d'un df_main


**Avant : DataFrame initial**


|        data        |
|--------------------|
| {appid, categories, ccu, developer, ...} |
| {appid, categories, ccu, developer, ...} |


data = struct (objet)

|-- data: struct (nullable = true)  

| |-- appid: long (nullable = true) -> ceci est une colonne simple, contenant un nombre entier (long=int) et peut être nul (nullable=true)  

| |-- categories: array (nullable = true) -> ceci est un tableau/liste imbriqué (array) 

| | |-- element: string (containsNull = true) -> chaque élément est une chaîne de caractère 

... 

| |-- platforms: struct (nullable = true) -> ceci est un objet structuré, un dictionnaire (strcut)  

| | |-- linux: boolean (nullable = true) -> chaque clé renvoi renvoie une valeur oui/non  

| | |-- mac: boolean (nullable = true)  

| | |-- windows: boolean (nullable = true) 


**Étape 1 : création d'un df principal**
df_main= df.select(

    col("data.appid"),

    col("data.categories"),

    col("data.ccu"),

    col("data.developer"),

    ...
)

Résultat : DataFrame imbriqué avec 1 ligne unique par jeu

| appid | categories                    | ccu | developer | ... |
|-------|-------------------------------|-----|-----------|---- |
| 10    | [Multi-player, PvP, ...]      | 13990 | Valve | ... |
| 1000  | [Single-player, Adventure]    | 500   | Indie  | ... |


--> ajout colonnes "platforms"

Étape 2 : création de df secondaires

categorie, langues, genre, tags

Résultat : une ligne = 1 catégorie du jeu. si le jeu a 4 catégories, 4 lignes sont créées.

| appid | category          | 
|-------|-------------------|
| 10    | Multi-player      | 
| 10    | PvP               | 
| 10    | Action            | 
| 1000  | Single-player     | 
| 1000  | Adventure         | 


- Nettoyage des valeurs nulles/incomplètes

- Enregistrer format parquet

# Etape 2 : visualisation des données

Lien databricks : [Notebook - visualisation des données](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/1757644669073569/1637098918164767/3378110399057887/latest.html)

Étape 2.1 : Analyses "macro"
Éditeurs les plus prolifiques

root
 |-- appid: long (nullable = true)
 |-- name: string (nullable = true)
 |-- developer: string (nullable = true)
 |-- publisher: string (nullable = true)
 |-- release_yyyy_mm: string (nullable = true)
 |-- required_age: string (nullable = true)
 |-- ccu: long (nullable = true)
 |-- positive: long (nullable = true)
 |-- negative: long (nullable = true)
 |-- price: double (nullable = true)
 |-- initialprice: double (nullable = true)
 |-- discount: double (nullable = true)
 |-- platform_windows: boolean (nullable = true)
 |-- platform_mac: boolean (nullable = true)
 |-- platform_linux: boolean (nullable = true)


df.groupBy("publisher").count().orderBy("count", ascending=False).show(10)


Jeux les mieux notés
Utiliser positive_ratings, negative_ratings et calculer un score ratio = positive/(positive+negative).

Tendances temporelles
Nombre de sorties par année, focus sur période Covid (2019-2021).

Distribution des prix & réductions
Histogramme prix, proportion de jeux gratuits / en promo.

Langues représentées
explode(languages) → top 10.

Âge requis
Répartition des restrictions (3+, 12+, 16+, 18+).

🔹 Étape 3 : Analyses par genres

Genres les plus populaires
explode(genres) + count().

Genres mieux notés
Moyenne du ratio de critiques positives par genre.

Genres favoris par éditeur
Croisement publisher × genre.

Genres les plus lucratifs
Moyenne/prix médian par genre.

🔹 Étape 4 : Analyses par plateformes

Disponibilité par OS
Proportion de jeux sur Windows/Mac/Linux.

Genres par plateforme
Croiser platform × genre.

🔹 Étape 5 : Visualisations dans Databricks

👉 Quelques idées de graphiques à créer dans les cellules du notebook :

Bar chart : top 10 éditeurs (nb de jeux)

Line chart : nombre de sorties par année

Histogramme : distribution des prix

Pie chart : répartition des plateformes

Heatmap : genre × note moyenne

Treemap ou stacked bar : genres par éditeur

🔹 Étape 6 : Structuration du livrable

Crée 1 notebook par grande partie (Macro / Genres / Plateformes) → si un seul devient trop lourd.

Publie chaque notebook (Databricks → « Publish » → lien public).

Mets les liens publiés dans ton repo GitHub (README clair + explications).

👉 Résultat attendu : une analyse claire et segmentée qui montre :

Les tendances de marché

Les éditeurs et genres clés

L’impact du prix, des plateformes et du temps

Des visualisations parlantes dans Databricks







