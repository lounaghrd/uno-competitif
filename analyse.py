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


def profils(manches):
    """Profil de chaque joueur. Les statistiques de performance (moy,
    victoires, volatilité…) portent sur les manches réellement jouées.
    En revanche le **total** applique l'imputation : un joueur absent d'une
    manche reçoit le score moyen de cette manche, et le cumul est la SOMME
    de ces contributions, arrondie au supérieur (arrondi à la fin)."""
    roster = {nom for m in manches.values() for nom, _, _ in m}
    scores = defaultdict(list)
    impute = defaultdict(float)  # somme imputée (flottant)
    for m in manches.values():
        moyenne = sum(sc for _, _, sc in m) / len(m)
        joues = {nom: sc for nom, _, sc in m}
        for nom, _, sc in m:
            scores[nom].append(sc)
        for nom in roster:
            impute[nom] += joues.get(nom, moyenne)
    out = {}
    for nom in roster:
        s = scores[nom]
        defaites = [x for x in s if x >= 0]
        out[nom] = {
            "total": math.ceil(impute[nom]),
            "moy": sum(s) / len(s),
            "victoires": sum(1 for x in s if x < 0),
            "coupes": sum(1 for x in s if x == -20),
            "moy_defaite": st.mean(defaites) if defaites else 0.0,
            "volatilite": st.pstdev(s) if len(s) > 1 else 0.0,
            "pire": max(s),
            "manches": len(s),
        }
    return out


def qui_commence(manches):
    """Déduit le joueur qui commence chaque manche : le dernier au cumul
    (imputé) parmi les présents. Retourne {manche: joueur ou None si égalité}."""
    roster = {nom for m in manches.values() for nom, _, _ in m}
    cumul = defaultdict(float)
    starters = {}
    for k, m in manches.items():
        presents = [nom for nom, _, _ in m]
        avant = {nom: cumul[nom] for nom in presents}
        pire = max(avant.values())
        derniers = [nom for nom in presents if avant[nom] == pire]
        starters[k] = derniers[0] if len(derniers) == 1 else None
        moyenne = sum(sc for _, _, sc in m) / len(m)
        joues = {nom: sc for nom, _, sc in m}
        for nom in roster:
            cumul[nom] += joues.get(nom, moyenne)
    return starters


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
    p = profils(manches)
    classement = sorted(p.items(), key=lambda kv: kv[1]["total"])
    nb_manches = len(manches)

    print(f"\n=== Classement ({nb_manches} manches) — moins = mieux ===")
    print("    (total imputé : les manches non jouées comptent au score moyen "
          "de la manche,\n     cumul = somme arrondie au supérieur)")
    for rang, (nom, v) in enumerate(classement, 1):
        coupe = f", dont {v['coupes']}x-20" if v["coupes"] else ""
        imp = f", {nb_manches - v['manches']} au score moyen" if v['manches'] < nb_manches else ""
        print(f"  {rang}. {nom:8} {v['total']:5} pts   "
              f"({v['victoires']} victoires{coupe} · {v['manches']} jouées{imp})")

    print("\n=== Profils (triés par total) ===")
    print(f"{'Joueur':8} | {'Moy':>5} | {'Vict':>4} | "
          f"{'Moy déf.':>8} | {'Volat.':>6} | {'Pire':>4}")
    print("-" * 52)
    for nom, v in classement:
        print(f"{nom:8} | {v['moy']:5.1f} | {v['victoires']:4} | "
              f"{v['moy_defaite']:8.1f} | {v['volatilite']:6.1f} | {v['pire']:4}")

    starters = qui_commence(manches)
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
