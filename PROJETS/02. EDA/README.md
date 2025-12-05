# :dart: Speed Dating Project

## :rocket: Objectif du projet

Ce projet vise à analyser un jeu de données issu d’expériences de speed dating menées entre 2002 et 2004.
L’objectif est de comprendre quels facteurs influencent l’intérêt mutuel entre deux personnes et quels attributs motivent la décision d’un second rendez-vous.

- Plus précisément, l’analyse cherche à répondre aux questions suivantes :

- Quels sont les critères les plus déterminants pour un second rendez-vous ?

- Ces critères diffèrent-ils selon le genre ?

- Existe-t-il un écart entre ce que les participants pensent rechercher et ce qu’ils choisissent réellement ?

## :brain: Pipeline d'analyse

L'intégralité du traitement est réalisé dans un unique notebook.

```text
Contexte et méthode
    ↓
Import et lecture du dataset
    ↓
Nettoyage et exploration des données
    ↓
Description des participants
    ↓
Attributs recherchés par les participants
    ↓
Facteurs influençant la décision finale
    ↓
Conclusion et perspectives
```

## :wheel: Technologies & outils

| Domaine    | Outils                   |
| ---------- | ---------|
| Traitement et statistiques | Pandas, NumPy |
| Visualisations | Matplotlib, Seaborn |

## :compass: Roadmap

- [x] Lecture et compréhension du dataset

- [x] Nettoyage et traitement des données manquantes

- [x] Analyse descriptive des participants

- [x] Exploration des critères d’attractivité et de préférence

- [x] Étude des facteurs influençant la décision de second rendez-vous

- [x] Visualisations et interprétations des résultats

- [ ] Mettre en place une analyse prédictive (régression logistique) pour estimer la probabilité d’un match.

## :key: Résultats princpaux

- L’attractivité physique et le fun sont les critères les plus corrélés à la décision d’un second rendez-vous.

- Les intérêts communs jouent un rôle significatif, mais moins fort que l’apparence.

- Les femmes accordent plus d’importance à la sincérité et à la compatibilité, tandis que les hommes valorisent davantage l’attractivité.

- On observe un décalage entre les intentions déclarées et les choix réels : les participants surestiment souvent l’importance de l’intelligence ou de la sincérité.

## :arrow_forward: Installation, exécution, tutlisation

### 0. Prérequis

- Disposer du dataset Speed Dating Data.csv

- Avoir installé Python ≥ 3.9 et les librairies suivantes :

```bash
pip install pandas numpy matplotlib seaborn 
```

### 1. Lancer le notebook

Ouvrir le notebook dans votre IDE préféré (JupyterLab, VSCode, Google Colab, etc.) puis exécuter les cellules séquentiellement.

## :busts_in_silhouette: Auteurs

Projet développé par [Nadège Lefort](https://github.com/nlefort)

*La réalisation de ce projet s'inscrit dans le cadre de la [formation Data Scientist](https://www.jedha.co/formations/formation-data-scientist) développé par [Jedha](https://www.jedha.co/), en vue de l'obtention de la certification professionnelle de niveau 6 (bac+4) enregistrée au RNCP : [Concepteur développeur en science des données](https://www.francecompetences.fr/recherche/rncp/35288/).*
