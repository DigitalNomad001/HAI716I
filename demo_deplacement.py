#!/usr/bin/env python3
"""
Demonstration du deplacement seul : le robot rejoint une case adjacente a
une cible, en affichant sa carte mentale a chaque pas.

    python3 demo_deplacement.py cartes/appartement_01.json R1
    python3 demo_deplacement.py cartes/appartement_01.json dictionnaire
    python3 demo_deplacement.py cartes/appartement_01.json R1 --pause 0.2

'?' = case jamais vue, '#' = mur decouvert, 'R' = robot.
"""

import sys
import time

from reconfort import reconfort_io as rio
from reconfort.memoire import CarteMentale
from reconfort.monde import Monde
from reconfort.navigation import aller_vers


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip())
        return 2
    pause = float(argv[argv.index("--pause") + 1]) if "--pause" in argv else 0.0

    try:
        carte = rio.charger_carte(argv[1])
    except rio.ErreurFichier as err:
        print(f"erreur : {err}", file=sys.stderr)
        return 1

    # Ce que le robot a le droit de connaitre au depart (section 3.2).
    residents = {r["id"]: tuple(r["position"]) for r in carte["residents"]}
    memoire = CarteMentale(
        hauteur=carte["dimensions"]["hauteur"],
        largeur=carte["dimensions"]["largeur"],
        depart=tuple(carte["depart_robot"]),
        armoire=tuple(carte["armoire"]["position"]),
        dictionnaire=tuple(carte["dictionnaire"]["position"]),
        residents=residents.values(),
    )
    monde = Monde(carte)                      # le simulateur, seul a voir la grille

    nom = argv[2]
    if nom == "armoire":
        cible = tuple(carte["armoire"]["position"])
    elif nom == "dictionnaire":
        cible = tuple(carte["dictionnaire"]["position"])
    elif nom in residents:
        cible = residents[nom]
    else:
        print(f"cible inconnue : {nom}", file=sys.stderr)
        return 1

    compteur = [0]

    def afficher(perception, direction):
        compteur[0] += 1
        print(f"\npas {compteur[0]} : en {perception.position}, AVANCER {direction}")
        print(memoire.dessiner(robot=perception.position))
        time.sleep(pause)

    resultat = aller_vers(monde, memoire, cible, observateur=afficher)

    print("\n" + memoire.dessiner(robot=monde.position))
    if resultat.arrive:
        print(f"\narrive a cote de {nom} {cible} en {len(resultat.pas)} pas, "
              f"position {monde.position}")
    else:
        print(f"\n{nom} {cible} inaccessible (prouve apres {len(resultat.pas)} pas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))