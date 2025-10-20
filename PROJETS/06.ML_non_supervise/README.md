# :taxi: Uber Hotspots – Apprentissage non supervisé

## :dart: Objectif du projet

Le projet consiste à identifier les **zones chaudes ("hotspots") de prise en charge Uber** à New York, afin d’aider les chauffeurs à se positionner là où la demande est la plus forte.

Les objectifs sont les suivants :

- Analyser et visualiser les données Uber NYC
- Appliquer des **algorithmes de clustering non supervisés** pour détecter les zones chaudes
- Comparer les performances de **KMeans** et **HDBSCAN**
- Visualiser les résultats sur une **carte interactive**
- Proposer des pistes d’amélioration (dashboard, automatisation, prédiction temporelle)

## :brain: Pipeline de traitement

Le traitement des données suit la progression suivante :

```text
Import et nettoyage des données
↓
Exploration et analyse descriptive
↓
Création des variables temporelles (jour, heure)
↓
Clustering spatial avec KMeans et HDBSCAN
↓
Évaluation et comparaison des modèles
↓
Visualisation des hotspots sur carte interactive
↓
Synthèse des zones les plus actives par jour et heure
```

## :wheel: Technologies & outils

| Domaine    | Outils                   |
| ---------- | ---------|
| Nettoyage & feature engineering | pandas / numpyo |
| Clustering | scikit-learn (MiniBatchKMeans) + hdbscan |
| Évaluation | métriques sklearn |
| Visualiser | Plotly / Mapbox |

## :key: Résultats clés

- **MiniBatchKMeans** : silhouette ≈ 0.42, zones globales stables

- **HDBSCAN** : silhouette ≈ 0.38, meilleure détection de micro-hotspots

- Hotspots principaux :

  - Midtown Manhattan
  - Financial District
  - Williamsburg / Brooklyn
  - JFK Airport (en soirée)

Les zones chaudes varient fortement selon le jour et l’heure : le modèle capte bien ces dynamiques spatio-temporelles.

## :compass: Roadmap

- [x] Nettoyage et exploration des données

- [x] Création des variables temporelles

- [x] Implémentation de MiniBatchKMeans

- [x] Implémentation de HDBSCAN

- [x] Évaluation des modèles

- [x] Visualisation interactive des clusters

- [ ] Déploiement d’un dashboard Streamlit

- [ ] Ajout de données contextuelles (météo, événements)

- [ ] Prédiction de la demande future (modèle supervisé)

## :arrow_forward: Installation, exécution, tutlisation

### 0. Prérequis

Python ≥ 3.9 et les librairies suivantes :

``` bash
pip install pandas numpy scikit-learn hdbscan plotly
```

### 1. Lancer le notebook

Ouvrez le notebook principal dans Jupyter / VSCode :

``` bash
jupyter notebook Best_place_to_be.ipynb
```

### 2. Visualiser les résultats

Les cartes interactives sont éditées sur des fichiers html annexes, classés par ordre croissant.

## :busts_in_silhouette: Auteurs

Projet développé par [Nadège Lefort](https://github.com/nlefort)

*La réalisation de ce projet s'inscrit dans le cadre de la [formation Data Scientist](https://www.jedha.co/formations/formation-data-scientist) développé par [Jedha](https://www.jedha.co/), en vue de l'obtention de la certification professionnelle de niveau 6 (bac+4) enregistrée au RNCP : [Concepteur développeur en science des données](https://www.francecompetences.fr/recherche/rncp/35288/).*