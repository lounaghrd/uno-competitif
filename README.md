# 🎴 UNO Compétitif — Analyse de la ligue

Analyse des manches de UNO notées dans notre Google Sheet.

**Règle du score :** une victoire vaut **−10 points** (**−20** si la manche est
gagnée en coupant le dernier pli). Le but est d'avoir le **moins** de points.

## Contenu

| Fichier | Rôle |
|---|---|
| `index.html` | Tableau de bord interactif (classement, profils, course, thème clair/sombre) |
| `manches.csv` | Les données brutes — une ligne par joueur, une colonne par manche |
| `analyse.py` | Script d'analyse (aucune dépendance, `python3 analyse.py`) |

Le CSV et le script s'adaptent tout seuls quand on **passera à 7 joueurs** ou
qu'on ajoutera des manches : il suffit d'ajouter des lignes / colonnes.

## Classement après 23 manches

| # | Joueur | Total | Victoires |
|---|--------|------:|:---------:|
| 1 | **Louna** | 330 | 6 |
| 2 | Justin | 368 | 6 *(dont 1×−20)* |
| 3 | Andy | 401 | 5 |
| 4 | Nathan | 483 | 1 |
| 5 | Julia | 496 | 5 |

## Ce que disent les chiffres

- **Gagner ne suffit pas — il faut éviter d'exploser.** Julia a autant de
  victoires qu'Andy (5) mais finit **dernière** : ses manches perdues coûtent en
  moyenne 30 pts, avec des cartons à 91 et 102. À l'inverse **Nathan n'a gagné
  qu'une manche** et termine 4ᵉ (pas dernier) grâce à la moyenne en défaite la
  plus basse du groupe (22,4).
- **Louna gagne le duel de la régularité.** 6 victoires *et* la plus faible
  moyenne par manche : elle marque des points sans jamais s'effondrer.
- **Justin est le joueur le plus explosif** : seul −20 de la saison, mais aussi
  la pire manche notée (123 pts) et une des plus fortes volatilités.

## ⚠️ L'angle mort : l'ordre de jeu

On note l'ordre de jeu pour l'analyser, mais sur 23 manches il est resté
**quasi fixe** (Nathan toujours 1ᵉ, Louna 2ᵉ, Julia 3ᵉ ; Andy et Justin n'ont
échangé leurs sièges que sur les 3 dernières manches). Impossible donc de
mesurer l'effet de la position : il est confondu avec l'effet « joueur ».

**Pour rendre cette donnée exploitable :**
1. **Tirer les places au sort à chaque manche** — pour que chaque joueur occupe
   chaque siège un nombre comparable de fois.
2. **Noter le donneur** et le **nombre de joueurs** de la manche (une victoire à
   7 vaut mécaniquement plus qu'à 5).
3. Ajouter une colonne **date** pour distinguer les soirées et suivre la forme.
