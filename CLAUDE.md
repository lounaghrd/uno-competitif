# UNO Compétitif — mémo du projet

Réponses en **français**. Dépôt git `lounaghrd/uno-competitif`.

## Le jeu et ses règles (à retenir)

- On joue au « **UNO compétitif** » entre amis. **6 joueurs** jouent désormais
  (Nathan, Louna, Andy, Julia, Justin, et **Tom** depuis la manche 24) ;
  **Nicolas** est attendu comme 7ᵉ (pas encore de manche jouée). L'effectif
  varie d'une manche à l'autre : tout le monde n'est pas toujours présent.
- **But** : avoir le **MOINS** de points possible sur l'ensemble des manches
  (score « de golf »).
- **Score d'une manche** :
  - le **vainqueur** de la manche marque **−10** ;
  - s'il gagne en **coupant le dernier pli**, il marque **−20** ;
  - les autres marquent la valeur (positive) des cartes restées en main ;
  - il y a exactement **un vainqueur** par manche (le seul score négatif).
- **Absents / effectif variable** : un joueur **non présent** à une manche se voit
  attribuer le **score moyen de la manche** (moyenne des scores des présents,
  gagnant compris). Le **score cumulé** est la **somme** de toutes les
  contributions (scores réels + moyens), **arrondie au supérieur** — on additionne
  d'abord, on arrondit à la fin (jamais manche par manche). Ainsi les totaux
  couvrent toutes les manches et restent comparables même à effectif variable.
  L'imputation vaut aussi pour les manches **antérieures à l'arrivée** d'un joueur
  (ex. Tom reçoit la moyenne des manches 1→23). Un joueur qui n'a **jamais** joué
  (0 manche, ex. Nicolas) est **exclu** tant qu'il n'a pas disputé une manche.
  Les stats de performance (moyenne, victoires, volatilité…) restent, elles,
  calculées sur les manches **réellement jouées**.
- **Règle des −200 (« pile sur la cible »)** : dès que le **score cumulé** d'un
  joueur (arrondi au supérieur, imputations comprises) vaut **exactement un
  multiple de 200** (200, 400, 600…), il **perd 200 points d'un coup**. C'est le
  fait de *tomber pile* sur le multiple qui déclenche la règle — le simple
  franchissement ne suffit pas. Au plus **une fois par manche** (pas de cascade :
  400 → −200 → 200 ne redéclenche pas).
- **Sièges / placement** : les numéros (1, 2, …, n) sont des **étiquettes
  cycliques** qui disent seulement **qui est à côté de qui** (… → n → 1 → …).
  Ce **n'est pas** l'ordre de jeu ; seul l'agencement **relatif** compte.
- **Sens du jeu** : **horaire** au départ (siège n → n+1), jusqu'à ce qu'une
  carte « sens inverse » le change.
- **Qui commence une manche** : le joueur **dernier au classement cumulé** (le
  plus de points) juste avant la manche — mécanique de **rattrapage**. Se
  **déduit** des scores cumulés : inutile de le noter.
- **Date/heure** : chaque manche a une date et une heure. Les **23 premières
  manches** ont eu lieu le **11/08/2026 à 15h00** ; les données couvrent
  désormais **66 manches sur 5 soirées** (11 → 15/08/2026). D'autres
  métadonnées (donneur, lieu…) pourront s'ajouter plus tard.

## Données & outils

- `manches.csv` — format **long**, une ligne par (manche, joueur) :
  `datetime,manche,joueur,siege,score`. S'étend sans effort à 7 joueurs, aux
  manches à effectif variable et aux sièges qui changent d'une manche à l'autre.
- `analyse.py` — analyse en ligne de commande, sans dépendance
  (`python3 analyse.py`). Déduit qui commence et calcule l'effet de position.
- `index.html` — **application** : saisie interactive des nouvelles manches +
  analyses en live. Persiste en `localStorage`, avec export/import CSV. Aussi
  publiée comme Artifact claude.ai.

## Rappels d'analyse

- Les **places varient enfin** (8 configurations sur 66 manches) : l'effet
  position commence à être analysable, mais l'échantillon par position reste
  modeste — à confirmer avec plus de manches.
- **Effectif variable** : le total est rendu comparable par l'**imputation du
  score moyen** aux manches non jouées (voir règles). Avec ça, Tom (43 manches
  jouées) obtient un total sur 66 (~1243) au coude-à-coude avec Andy/Louna,
  au lieu des 827 bruts qui l'avantageaient à tort.
