"""
Boucle de deplacement : perception -> memoire -> decision -> action.

C'est la boucle de l'annexe B.5, appliquee a un seul objectif : rejoindre
une case adjacente a une cible. Elle sera reutilisee par la boucle
principale de l'agent (agent.py) pour les trois trajets de chaque demande.

C'est le seul endroit qui tient a la fois le Monde et la CarteMentale :
il fait passer la perception de l'un a l'autre, et l'action de l'agent
vers le monde. La decision, elle, ne voit que la carte mentale.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from reconfort.decision import ARRIVE, INACCESSIBLE, choisir_pas
from reconfort.memoire import CarteMentale
from reconfort.monde import Monde
from reconfort.perception import Perception

Case = Tuple[int, int]

# Garde-fou : aucune carte raisonnable ne demande autant de pas.
MAX_PAS = 10_000


class Resultat:
    """Bilan d'un trajet."""

    def __init__(self, arrive: bool) -> None:
        self.arrive = arrive    # True : adjacent a la cible
        self.pas = []           # chaque pas = (perception AVANT l'action, direction jouee)

def aller_vers(
    monde: Monde,
    carte: CarteMentale,
    cible: Case,
    observateur: Optional[Callable[[Perception, str], None]] = None,
) -> Resultat:
   
    resultat = Resultat(arrive=False)

    for _ in range(MAX_PAS):
        perception = monde.percevoir()                               # 1. perception
        carte.mettre_a_jour(perception.position, perception.voisins)  # 2. memoire
        decision, direction = choisir_pas(carte, perception.position, cible)  # 3. decision

        if decision == ARRIVE:
            resultat.arrive = True
            return resultat
        if decision == INACCESSIBLE:
            return resultat

        if observateur is not None:
            observateur(perception, direction)
        monde.avancer(direction)                                     # 4. action
        resultat.pas.append((perception, direction))

    raise RuntimeError(f"plus de {MAX_PAS} pas vers {cible} : boucle infinie ?")



"""Fait marcher le robot jusqu'a une case adjacente a `cible`.

    observateur : fonction optionnelle appelee a chaque pas avec(perception, direction). 
    Servira a remplir la Trace,et a l'affichage pour la video,on peut l'ignorer dans la teste unitaire pour l'instant 

    Termine toujours : chaque tour soit rapproche le robot, soit revele
    des murs (ce qui ne peut arriver qu'un nombre fini de fois).
    MAX_PAS n'est qu'un filet de securite contre un bug.
"""
