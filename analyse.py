#!/usr/bin/env python3
"""Analyse des manches de UNO compétitif.

Lit `manches.csv` au format long : une ligne = (manche, joueur, siege, score).

Règles :
  - une victoire vaut -10 points (-20 si gagnée en coupant le dernier pli) ;
  - le but est d'avoir le MOINS de points ;
  - la manche est COMMENCÉE par le joueur qui est DERNIER au classement
    cumulé (le plus de points) juste avant la manche — mécanique de
    rattrapage. Le script le déduit tout seul, pas besoin de le noter ;
  - les sièges (colonne `siege`) ne sont que des étiquettes CYCLIQUES qui
    disent qui est à côté de qui. Le jeu tourne dans le sens horaire
    (siège n -> n+1). Seule la position RELATIVE au joueur qui commence
    compte.

Le script s'adapte au nombre de joueurs et de manches, et à des manches où
tout le monde n'est pas présent.
"""
import csv
import math
import statistics as st
from collections import defaultdict
from pathlib import Path

CSV = Path(__file__).with_name("manches.csv")


def charger(path=CSV):
    """Retourne {manche: [(joueur, siege, score), ...]} trié par manche.

    La colonne `datetime` est optionnelle (ignorée ici, utilisée par l'app)."""
    manches = defaultdict(list)
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            manches[int(row["manche"])].append(
                (row["joueur"], int(row["siege"]), int(row["score"]))
            )
    return dict(sorted(manches.items()))


def parcours(manches):
    """Parcourt les manches dans l'ordre et calcule tout le cumul.

    Règles appliquées :
    - **imputation** : un joueur absent reçoit le score moyen de la manche ;
    - **cumul** = somme des contributions, arrondie au supérieur à l'affichage ;
    - **règle des −200** : dès que le cumul (arrondi au supérieur) d'un joueur
      vaut EXACTEMENT un multiple de 200, il perd 200 points d'un coup.
      Se base sur le cumul total (imputations comprises), et ne se déclenche
      qu'une fois par manche (pas de cascade).

    Retourne (roster, net, played, malus, starters) où `net` est le cumul net
    final (flottant) et `malus` le nombre de −200 subis par joueur.
    """
    roster = {nom for m in manches.values() for nom, _, _ in m}
    net = {nom: 0.0 for nom in roster}   # cumul net courant (malus inclus)
    played = defaultdict(list)
    malus = defaultdict(int)
    starters = {}
    for k, m in manches.items():
        present = [nom for nom, _, _ in m]
        # qui commence : dernier au cumul net avant, parmi les présents
        avant = {nom: net[nom] for nom in present}
        pire = max(avant.values())
        derniers = [nom for nom in present if avant[nom] == pire]
        starters[k] = derniers[0] if len(derniers) == 1 else None
        moyenne = sum(sc for _, _, sc in m) / len(m)
        joues = {nom: sc for nom, _, sc in m}
        for nom, _, sc in m:
            played[nom].append(sc)
        for nom in roster:
            net[nom] += joues.get(nom, moyenne)
            disp = math.ceil(net[nom])
            if disp > 0 and disp % 200 == 0:   # pile sur un multiple de 200
                net[nom] -= 200
                malus[nom] += 1
    return roster, net, played, malus, starters


def profils_depuis(roster, net, played, malus):
    """Construit les stats par joueur (total imputé/malus + perf sur le jeu réel)."""
    out = {}
    for nom in roster:
        s = played[nom]
        defaites = [x for x in s if x >= 0]
        out[nom] = {
            "total": math.ceil(net[nom]),
            "moy": sum(s) / len(s),
            "victoires": sum(1 for x in s if x < 0),
            "coupes": sum(1 for x in s if x == -20),
            "moy_defaite": st.mean(defaites) if defaites else 0.0,
            "volatilite": st.pstdev(s) if len(s) > 1 else 0.0,
            "pire": max(s),
            "manches": len(s),
            "malus": malus[nom],
        }
    return out


def analyse_position(manches, starters):
    """Score moyen selon la position relative (sens horaire) au joueur qui
    commence. offset 0 = celui qui commence."""
    par_offset = defaultdict(list)
    par_starter = defaultdict(list)
    for k, m in manches.items():
        s = starters[k]
        if s is None:
            continue
        n = len(m)
        siege = {nom: sg for nom, sg, _ in m}
        s_siege = siege[s]
        for nom, sg, sc in m:
            off = (sg - s_siege) % n
            par_offset[off].append(sc)
        par_starter[s].append(next(sc for nom, _, sc in m if nom == s))
    return par_offset, par_starter


def afficher(manches):
    roster, net, played, malus, starters = parcours(manches)
    p = profils_depuis(roster, net, played, malus)
    classement = sorted(p.items(), key=lambda kv: kv[1]["total"])
    nb_manches = len(manches)

    print(f"\n=== Classement ({nb_manches} manches) — moins = mieux ===")
    print("    (total imputé ; règle des −200 sur les multiples exacts)")
    for rang, (nom, v) in enumerate(classement, 1):
        coupe = f", {v['coupes']}x-20" if v["coupes"] else ""
        imp = f", {nb_manches - v['manches']} au score moyen" if v['manches'] < nb_manches else ""
        mal = f", {v['malus']}x-200" if v["malus"] else ""
        print(f"  {rang}. {nom:8} {v['total']:5} pts   "
              f"({v['victoires']} victoires{coupe} · {v['manches']} jouées{imp}{mal})")

    print("\n=== Profils (triés par total) ===")
    print(f"{'Joueur':8} | {'Moy':>5} | {'Vict':>4} | "
          f"{'Moy déf.':>8} | {'Volat.':>6} | {'Pire':>4}")
    print("-" * 52)
    for nom, v in classement:
        print(f"{nom:8} | {v['moy']:5.1f} | {v['victoires']:4} | "
              f"{v['moy_defaite']:8.1f} | {v['volatilite']:6.1f} | {v['pire']:4}")

    par_offset, par_starter = analyse_position(manches, starters)

    print("\n=== Qui commence (dernier au cumul) ===")
    from collections import Counter
    cnt = Counter(s for s in starters.values() if s)
    ambigu = sum(1 for s in starters.values() if s is None)
    for nom, c in cnt.most_common():
        ms = par_starter[nom]
        vic = sum(1 for x in ms if x < 0)
        print(f"  {nom:8}: commence {c:2} fois "
              f"(score moyen {st.mean(ms):5.1f}, {vic} victoire(s) en commençant)")
    if ambigu:
        print(f"  [{ambigu} manche(s) écartée(s) : égalité au cumul / début de saison]")

    print("\n=== Effet de la position (0 = celui qui commence, sens horaire) ===")
    print("  offset | n   | score moyen | victoires")
    for o in sorted(par_offset):
        v = par_offset[o]
        vic = sum(1 for x in v if x < 0)
        print(f"    {o}    | {len(v):3} | {st.mean(v):6.1f}      | {vic}")
    nconf = len({tuple(sorted((nom, sg) for nom, sg, _ in m))
                 for m in manches.values()})
    print(f"  ⚠ Interprétation prudente : {nconf} configurations de sièges, mais "
          "l'échantillon\n    par position reste modeste et un joueur ouvre encore "
          "une bonne part des\n    manches — à confirmer avec des places bien "
          "mélangées.")


if __name__ == "__main__":
    afficher(charger())
