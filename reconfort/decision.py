"""
Decision : choisir la prochaine action a partir de la memoire SEULEMENT.

Pour l'instant, une seule decision : le prochain pas vers une cible
(dictionnaire, armoire ou resident). La machine a etats complete
(consulter, fouiller, prendre, donner) viendra ensuite.

Ce module ne connait pas Monde : il raisonne uniquement sur la CarteMentale.
"""

from __future__ import annotations

from typing import Optional, Tuple

from reconfort.memoire import CarteMentale
from reconfort.planification import direction_vers, plus_court_chemin

Case = Tuple[int, int]

ARRIVE = "ARRIVE"            # deja adjacent a la cible
INACCESSIBLE = "INACCESSIBLE"  # preuve qu'aucun chemin n'existe (annexe B.6)


def choisir_pas(carte: CarteMentale, position: Case, cible: Case) -> Tuple[str, Optional[str]]:
    """Decide du prochain pas pour se placer a cote de `cible`.

    Renvoie :
      (ARRIVE, None)          si le robot est deja sur une case adjacente ;
      ("AVANCER", direction)  le premier pas du plus court chemin ;
      (INACCESSIBLE, None)    si le BFS echoue sur la carte mentale.

    On replanifie a chaque appel (annexe B.5) : la carte vient d'etre mise
    a jour, donc un mur decouvert est automatiquement contourne.
    """
    arrivees = carte.arrivees_autour(cible)          # recalcule a chaque tour
    chemin = plus_court_chemin(tuple(position), arrivees, carte.est_traversable)
    if chemin is None:
        return INACCESSIBLE, None
    if len(chemin) == 1:
        return ARRIVE, None
    return "AVANCER", direction_vers(chemin[0], chemin[1])
