# :phone: Détecter spams – Apprentissage profond

## :dart: Objectif du projet

Le projet consiste à identifier les **messages SPAMS**  reçus par sms pour en automatiser la détection.

Les objectifs sont les suivants :

- Analyser et visualiser les données spams
- Appliquer un **algorithme de classification** pour prédire la classification du message
- Interpréter et analyser les performances du modèle
- Appliquer deux modèles d'**algorithme de d'apprentissage profond** pour classifier les messages
- Réaliser un **apprentissage pae transfert** pour améliorer la puissance du modèle sur un plus grans nombre d'observations
- Proposer des pistes d’amélioration

## :brain: Pipeline de traitement

Le traitement des données suit la progression suivante :

```text
Import et nettoyage des données
↓
Exploration et analyse descriptive
↓
Prétraitement des données
↓
Création d'un modèle de classification (LogisitcRegression)
↓
Évaluation du modèle
↓
Création d'un modèle d'apprentissage profond (CNN)
↓
Évaluation du modèle
↓
Application d'un modèle d'apprentissage par transfert(HuggingFace)
↓
Evaluation du modèle et comparaisons avec les autres modèles
```

## :toolbox: Technologies & outils

| Domaine    | Outils                   |
| ---------- | ---------|
| Nettoyage & feature engineering | pandas / numpy |
| Apprentissage automatique | Regression Logisitique |
| Apprentissage profond| CNN, HuggingFace |
| Visualiser | Plotly / Mapbox |

## :key: Résultats clés

Tests sur 3 modèles : Logistique Regression, CNN et apprentissage par transfert.
Apprentissage par transfert, le plus performant (0 prédiction de spams pour un vrai message):

- 99.5 % des prédictions de la classe 0 (ham) sont correctes
- 100 % des prédictions de la classe 1 (spam) sont correctes

- 100% des vrais 'ham' de la classe 'ham' ont été correctement prédits
- 96.64 % des vrais 'spams' de la classe 'spams' ont été correctement prédits

Métriques globales :

- Accuracy = 0.9955 -> 99,5 % des prédictions correctes.
- ROC-AUC = 0.998 -> modèle quasi parfait pour séparer les classes.

## :compass: Roadmap

- [x] Nettoyage et exploration des données

- [x] Prétraitement des données

- [x] Implémentation d'un modèle de ML

- [x] Implémentation de deux modèle de DL

- [x] Évaluation des modèles

- [ ] Déploiement du modèle (météo, événements)

## :arrow_forward: Installation, exécution, tutlisation

### 0. Prérequis

Python ≥ 3.9 et les librairies suivantes :

``` bash
pip install pandas ...
```

### 1. Lancer le notebook

Ouvrez le notebook principal dans Jupyter / VSCode :

``` bash
jupyter notebook spams_detector.ipynb
```

### 2. Visualiser les résultats

Les cartes interactives s’affichent directement dans le notebook.

## :busts_in_silhouette: Auteurs

Projet développé par [Nadège Lefort](https://github.com/nlefort)

*La réalisation de ce projet s'inscrit dans le cadre de la [formation Data Scientist](https://www.jedha.co/formations/formation-data-scientist) développé par [Jedha](https://www.jedha.co/), en vue de l'obtention de la certification professionnelle de niveau 6 (bac+4) enregistrée au RNCP : [Concepteur développeur en science des données](https://www.francecompetences.fr/recherche/rncp/35288/).*