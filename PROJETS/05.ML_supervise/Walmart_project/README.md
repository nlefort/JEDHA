# :dart: Prédire le montant des ventes hebdomadaires des magasins

## :rocket: Objectif du projet

L'objectif de ce projet est de comprendre et de modéliser l'influence des indicateurs économiques et autres facteurs sur les ventes hebdomadaires des magasins Walmart. Les principaux objectifs sont :

- Explorer et visualiser les données mises à disposition pour identifier les tendances et les relations.
- Construire un modèle de régression linéaire pour prédire les ventes des supermarchés.
- Évaluer et interpréter le modèle pour identifier les caractéristiques les plus influentes.
- Proposer des modèles alternatifs (Ridge, Lasso) pour améliorer les performances et réduire le surapprentissage.
- Normaliser les ventes par magasin afin de comprendre l’effet purement économique, indépendamment des différences structurelles entre magasins.

## :brain: Pipeline de traitement

La collecte et le traitement des données suivante la progression suivante :

```text
Import des données 
↓
Analyse exploratoire (EDA) et statistiques descriptives
↓
Prétraitement des données (gestion des NaN, conversion des dates, suppression des outliers)
↓
Création d'un modèle de régression linéaire de référence
↓
Évaluation et interprétation des coefficients du modèle
↓
Amélioration du modèle avec régularisation (Ridge, Lasso) et optimisation des hyperparamètres
↓
Normalisation des ventes par magasin pour analyser l’influence économique pure
↓
Analyse finale des performances et des variables influentes
```

## :wheel: Technologies & outils

| Domaine    | Outils                   |
| ---------- | ---------|
| Exploitation et visualisation des données | Pandas, NumPy, Seaborn, Matplotlib, Plotly |
| Apprentissage automatique supervisé | Scikit-learn, LinearRegression, Ridge, Lasso, GridSearchCV, KFold |

## :key: Résultats clés

- **Analyse descriptive** : 

- Saisonnalité des ventes :  Plus de ventes en février, décembre et juin
- Ventes hebdomadaires plus importantes lorsqu'il y a des jours fériés
- Pas de relation linéaire entre ventes hebdomadaires vs températures/ prix du fuel / indice des prix à la consommation / chômage

- **Modèle de regression linéaire** : R² = 0.94 --> le modèle explique une grande partie de la variance des ventes. Surapprentissage du modèle (écart RMSE).

- **Modèle de regression linéaire ajusté (Ridge, Lasso)** : R² = 0.94 --> le modèle explique une grande partie de la variance des ventes. réduction du surapprentissage. Effet "Store" qui prédomine.

- **Modèle de regression linéaire normalisé des ventes (Ridge)** : R² = 0.22 --> le modèle explique peu la variance des ventes.

Pour prédire les ventes, la variable "Store" est essentielle car au-delà des aspects économiques de nombreux autres facteurs impactent les résultats d'un magasin.
L'inclusion de variables géographique, dimensions de magasin, pourrait permettre d'expliquer davanatage les résulats par magasin.


## :compass: Roadmap

- [x]  Statistiques descriptives globales et visualisations

- [x] Analyse exploratoire et synthèse des tendances

- [x] Test sur un premier modèle de régression linéaire

- [x] Interpréation des coefficents du modèle

- [x] Proposition d’un modèle régularisé (Ridge/Lasso)

- [x] Analyse des ventes normalisées par magasin

- [x] Évaluation finale des performances et interprétation des variables économiques

## :arrow_forward: Installation, exécution, tutlisation

### 0. Prérequis

Python 3.x

### 1. Lancer le notebook

Depuis votre IDE préféré, lancer le notebook

## :busts_in_silhouette: Auteurs

Projet développé par [Nadège Lefort](https://github.com/nlefort)

*La réalisation de ce projet s'inscrit dans le cadre de la [formation Data Scientist](https://www.jedha.co/formations/formation-data-scientist) développé par [Jedha](https://www.jedha.co/), en vue de l'obtention de la certification professionnelle de niveau 6 (bac+4) enregistrée au RNCP : [Concepteur développeur en science des données](https://www.francecompetences.fr/recherche/rncp/35288/).*
