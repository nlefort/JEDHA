# :dart: Conversion Rate Challenge

## :rocket: Objectif du projet

Le projet consiste à participer à une compétition d’apprentissage automatique supervisé similaire à Kaggle.
Les objectifs sont les suivants :

- Analyser et visualiser les données mises à disposition pour comprendre les comportements des utilisateurs.
- Créer un modèle de base permettant de prédire la souscription à une newsletter.
- Explorer différents modèles d’apprentissage automatique et sélectionner celui qui est le plus performant pour prédire la souscription.
- Interpréter les modèles pour identifier les leviers d’action permettant d’améliorer le taux de conversion.

## :brain: Pipeline de traitement

La collecte et le traitement des données suivante la progression suivante :

```text
Import des données
↓
Exploration et analyses statistiques
↓
Prétraitement des données (gestion des valeurs manquantes, encodage, standardisation)
↓
Création d'un modèle de base (régression logistique avec une variable)
↓
Amélioration du modèle et tests sur plusieurs modèles (DecisionTree, RandomForest, XGBoost, LightGBM, CatBoost)
↓
Évaluation et comparaison des modèles (F1-score, ROC-AUC, matrices de confusion)
↓
Interprétation des modèles et choix du plus performant
↓
Réentraînement du modèle choisi sur l'ensemble du dataset
↓
Prédictions sur le dataset test
↓
Propositions d'actions concrètes pour améliorer le taux de conversion
```

## :wheel: Technologies & outils

| Domaine    | Outils                   |
| ---------- | ---------|
| Analyse et visualisation des données | Pandas, NumPy, Seaborn, Matplotlib, Plotly |
| Apprentissage automatique supervisé | Scikit-learn (LogisticRegression, DecisionTree, RandomForest, GridSearchCV), XGBoost, LightGBM, CatBoost |

## :compass: Roadmap

- [x] Statistiques descriptives et EDA

- [x] Synthèse et analyse exploratoire

- [x] Test sur le modèle de base fourni

- [x] Amélioration du modèle et exploration d’autres modèles

- [x] Comparaison et évaluation des modèles

- [x] Interprétation des modèles et choix du meilleur modèle

- [x] Réentraînement du modèle choisi sur l’ensemble du dataset

- [x] Génération des prédictions pour le dataset test

- [x] Proposition d’actions concrètes pour augmenter le taux de conversion

## :arrow_forward: Installation, exécution, tutlisation

## :bulb: Recommandations & actions concrètes

- Encourager les utilisateurs à visiter plus de pages → recommandations de contenus, gamification.
- Cibler les jeunes utilisateurs pour améliorer le taux de conversion.
- Optimiser le parcours pour les nouveaux utilisateurs, moins enclins à convertir.
- Développer des campagnes marketing : SEO, publicité, partenariats, réseaux sociaux.

### 0. Prérequis

Python 3.x

### 1. Lancer le notebook

Depuis votre IDE préféré, lancer le notebook

## :busts_in_silhouette: Auteurs

Projet développé par [Nadège Lefort](https://github.com/nlefort)

*La réalisation de ce projet s'inscrit dans le cadre de la [formation Data Scientist](https://www.jedha.co/formations/formation-data-scientist) développé par [Jedha](https://www.jedha.co/), en vue de l'obtention de la certification professionnelle de niveau 6 (bac+4) enregistrée au RNCP : [Concepteur développeur en science des données](https://www.francecompetences.fr/recherche/rncp/35288/).*
