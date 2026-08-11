#!/usr/bin/env python3
"""Analyse des manches de UNO compétitif.

Lit `manches.csv` (une ligne par joueur : joueur, siege, m1, m2, ...) et
affiche le classement et le profil de chaque joueur.

Règles : une victoire vaut -10 points (-20 si la manche est gagnée en
coupant le dernier pli). Le but est d'avoir le MOINS de points.

Le script s'adapte automatiquement au nombre de joueurs (5, 7, ...) et
au nombre de manches : il suffit d'ajouter des lignes/colonnes au CSV.
"""
import csv
import statistics as st
from pathlib import Path

CSV = Path(__file__).with_name("manches.csv")


def charger(path=CSV):
    joueurs = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nom = row["joueur"]
            manches = [
                int(v) for k, v in row.items()
                if k.startswith("m") and v not in ("", None)
            ]
            joueurs[nom] = {"siege": int(row["siege"]), "manches": manches}
    return joueurs


def stats(joueurs):
    n = max(len(j["manches"]) for j in joueurs.values())
    out = {}
    for nom, j in joueurs.items():
        m = j["manches"]
        defaites = [x for x in m if x >= 0]
        out[nom] = {
            "total": sum(m),
            "moy": sum(m) / len(m),
            "victoires": sum(1 for x in m if x < 0),
            "coupes": sum(1 for x in m if x == -20),   # gagnées au dernier pli
            "moy_defaite": st.mean(defaites) if defaites else 0.0,
            "volatilite": st.pstdev(m) if len(m) > 1 else 0.0,
            "pire": max(m),
            "siege": j["siege"],
        }
    return out, n


def afficher(joueurs):
    s, n = stats(joueurs)
    classement = sorted(s.items(), key=lambda kv: kv[1]["total"])

    print(f"\n=== Classement ({n} manches, {len(s)} joueurs) — moins = mieux ===")
    for rang, (nom, v) in enumerate(classement, 1):
        coupe = f", dont {v['coupes']}×-20" if v["coupes"] else ""
        print(f"  {rang}. {nom:8} {v['total']:4} pts   "
              f"({v['victoires']} victoires{coupe})")

    print("\n=== Profils ===")
    print(f"{'Joueur':8} | {'Moy':>5} | {'Vict':>4} | "
          f"{'Moy déf.':>8} | {'Volat.':>6} | {'Pire':>4}")
    print("-" * 52)
    for nom, v in classement:
        print(f"{nom:8} | {v['moy']:5.1f} | {v['victoires']:4} | "
              f"{v['moy_defaite']:8.1f} | {v['volatilite']:6.1f} | {v['pire']:4}")

    # Vérification d'intégrité : une victoire par manche
    print("\n=== Vainqueur par manche ===")
    victoires = {nom: 0 for nom in joueurs}
    for r in range(n):
        vals = {nom: j["manches"][r] for nom, j in joueurs.items()
                if r < len(j["manches"])}
        gagnant = min(vals, key=vals.get)
        victoires[gagnant] += 1
    total = sum(victoires.values())
    print("  " + ", ".join(f"{k}: {x}" for k, x in victoires.items())
          + f"  (total {total}/{n})")


if __name__ == "__main__":
    afficher(charger())
