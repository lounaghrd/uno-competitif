# 🎴 UNO Compétitif — Analyse de la ligue

Analyse des manches de UNO notées dans notre Google Sheet.

**Règle du score :** une victoire vaut **−10 points** (**−20** si la manche est
gagnée en coupant le dernier pli). Le but est d'avoir le **moins** de points.

## Contenu

| Fichier | Rôle |
|---|---|
| `index.html` | **L'application** : saisie interactive + analyses en live (local ou synchro Supabase) |
| `manches.csv` | Les données brutes au format long — une ligne par (manche, joueur) |
| `analyse.py` | Script d'analyse (aucune dépendance, `python3 analyse.py`) |
| `supabase-schema.sql` | Schéma SQL à exécuter une fois pour activer la synchro temps réel |

Le CSV et le script s'adaptent tout seuls à l'**effectif variable** (Tom est
arrivé à la manche 24, Nicolas est attendu en 7ᵉ) : il suffit d'ajouter des lignes.

## Classement après 66 manches (5 soirées, 11 → 15/08/2026)

| # | Joueur | Total | Moy./manche | Manches | Victoires |
|---|--------|------:|:-----------:|:-------:|:---------:|
| 1 | **Tom** | 827 | 19,2 | 43 | 7 *(3×−20)* |
| 2 | Andy | 1268 | 19,2 | 66 | 13 |
| 3 | Louna | 1284 | 19,5 | 66 | 14 *(1×−20)* |
| 4 | Julia | 1422 | 21,5 | 66 | 13 *(3×−20)* |
| 5 | Nathan | 1471 | 22,3 | 66 | 7 |
| 6 | Justin | 1626 | 24,6 | 66 | 12 *(3×−20)* |

> ⚠️ **Attention aux totaux :** Tom mène au total mais n'a joué que **43 manches
> sur 66** — le score « golf » avantage mécaniquement qui joue moins. À la
> **moyenne par manche**, Tom et Andy sont au coude-à-coude (19,2), et Justin
> reste le plus en difficulté (24,6).

## La position de jeu

Les numéros de siège (`siege`) sont des **étiquettes cycliques** : ils disent
seulement qui est à côté de qui. Le jeu tourne dans le **sens horaire**
(siège n → n+1). La manche est **ouverte par le dernier au classement cumulé**
(mécanique de rattrapage) — le script le déduit tout seul, inutile de le noter.

Ce qui compte pour analyser la position, ce n'est donc pas le n° de siège mais
l'**écart, dans le sens horaire, par rapport à celui qui commence**.

Ce qu'on observe pour l'instant :

- **Ouvrir n'aide pas à gagner.** Le dernier au cumul ouvre la manche ; sur les
  66 manches, c'est **Julia qui a le plus ouvert (33 fois)**, sans que ça la
  fasse remonter.
- Les places **varient enfin** (8 configurations distinctes) : le score moyen par
  position relative (`analyse.py`) devient plus lisible, mais l'échantillon par
  position reste **modeste** — à interpréter avec prudence tant qu'on n'a pas
  plus de manches avec des places bien mélangées.

**Pour rendre la position pleinement analysable :**
1. **Changer les places à chaque manche** (tirage au sort) — chaque joueur
   occupera alors chaque position relative un nombre comparable de fois.
2. Continuer à noter le **siège de chacun par manche** (déjà en place) et le
   **nombre de joueurs** présents (une victoire à 7 vaut plus qu'à 5).
3. Ajouter une colonne **date** pour distinguer les soirées et suivre la forme.

## Format des données

`manches.csv` est au **format long** : une ligne par (manche, joueur), avec son
siège et son score. Ça s'étend sans effort à 7 joueurs, à des manches où tout le
monde n'est pas présent, et à des sièges qui changent à chaque manche.

```
manche,joueur,siege,score
1,Nathan,1,15
1,Louna,2,46
...
```

## Synchro temps réel (Supabase + GitHub Pages)

Par défaut l'app fonctionne en **local** (données dans le navigateur, export/import
CSV pour partager). Pour que **tout le monde saisisse et voie le classement en
direct**, on la branche sur Supabase (gratuit) et on l'héberge sur GitHub Pages.

**Mise en place (une seule fois) :**

1. Créer un projet sur [supabase.com](https://supabase.com) (gratuit).
2. Dans **SQL Editor**, coller le contenu de `supabase-schema.sql` puis **Run**.
3. Dans **Project Settings → API**, copier :
   - la **Project URL** (ex. `https://xxxx.supabase.co`) ;
   - la clé **anon public**.
4. Les reporter dans `index.html`, tout en haut du script :
   ```js
   const SUPA={ url:"https://xxxx.supabase.co", key:"votre-clé-anon" };
   ```
5. **Héberger sur Vercel** : sur [vercel.com](https://vercel.com), *Add New → Project*,
   importer ce dépôt. Framework = **Other**, aucune commande de build (le
   `vercel.json` sert le dépôt tel quel). Chaque push crée un déploiement ;
   Vercel fournit l'URL du site.

À l'ouverture, l'app charge l'état partagé, sème les 23 manches d'origine si la
base est vide, et **se met à jour en direct** chez tout le monde à chaque manche.

**Note de sécurité :** l'accès se fait avec la clé *anon* (publique) et des règles
ouvertes — parfait pour une petite ligue privée. Ne partagez pas l'URL du site
publiquement ; on pourra ajouter un mot de passe partagé si besoin.

**Concurrence :** l'état est une seule ligne JSON (« dernier qui écrit gagne »).
Si deux personnes enregistrent exactement au même instant, une manche pourrait
être écrasée — négligeable quand on saisit à tour de rôle.
