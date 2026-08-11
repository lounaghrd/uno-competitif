# UNO Compétitif — mémo du projet

Réponses en **français**. Dépôt git `lounaghrd/uno-competitif`.

## Le jeu et ses règles (à retenir)

- On joue au « **UNO compétitif** » entre amis. Actuellement **5 joueurs**
  (Nathan, Louna, Julia, Justin, Andy) ; on passera à **7** plus tard.
- **But** : avoir le **MOINS** de points possible sur l'ensemble des manches
  (score « de golf »).
- **Score d'une manche** :
  - le **vainqueur** de la manche marque **−10** ;
  - s'il gagne en **coupant le dernier pli**, il marque **−20** ;
  - les autres marquent la valeur (positive) des cartes restées en main ;
  - il y a exactement **un vainqueur** par manche (le seul score négatif).
- **Sièges / placement** : les numéros (1, 2, …, n) sont des **étiquettes
  cycliques** qui disent seulement **qui est à côté de qui** (… → n → 1 → …).
  Ce **n'est pas** l'ordre de jeu ; seul l'agencement **relatif** compte.
- **Sens du jeu** : **horaire** au départ (siège n → n+1), jusqu'à ce qu'une
  carte « sens inverse » le change.
- **Qui commence une manche** : le joueur **dernier au classement cumulé** (le
  plus de points) juste avant la manche — mécanique de **rattrapage**. Se
  **déduit** des scores cumulés : inutile de le noter.
- **Date/heure** : chaque manche a une date et une heure. Les **23 premières
  manches** ont eu lieu le **11/08/2026 à 15h00**. D'autres métadonnées
  (nombre de joueurs présents, donneur, lieu…) pourront s'ajouter plus tard.

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

- La position ne pourra être analysée proprement que lorsque les **places
  varieront** (tirage au sort) : sinon l'effet position reste confondu avec
  l'identité des joueurs.
