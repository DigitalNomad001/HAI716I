"""
Le monde reel : le simulateur.

C'est le SEUL module autorise a lire carte["grille"] (section 3.2). Il joue
le role de la realite : il repond aux perceptions et verifie la legalite des
deplacements. L'agent ne recoit jamais cet objet, seulement des Perception.
"""


from typing import Any, Dict, Tuple

from reconfort.perception import Perception
from reconfort.planification import Directions, voisins

Case = Tuple[int, int]

# Symbole de la grille -> valeur de perception (sections 3.1 et 5.5).
# La case de depart 'R' est une case libre comme une autre.
SYMBOLES = {
    "#": "mur",
    ".": "libre",
    "R": "libre",
    "A": "armoire",
    "D": "dictionnaire",
    "P": "resident",
}


class DeplacementIllegal(Exception):
    """L'agent a demande une action impossible. C'est un BUG de l'agent :
    on prefere planter tout de suite que produire une trace fausse
    (section 10 : un deplacement illegal annule les points du jeu)."""


class Monde:
    """Simulateur d'un appartement.

    Pour l'instant : position du robot, perception, deplacement.
    (Plus tard : contenu reel de l'armoire et selecteur.)
    """

    def __init__(self, carte: Dict[str, Any]) -> None:
        self._grille = carte["grille"]                 # reserve au simulateur,lire la grille de la carte dans le json
        self.hauteur = carte["dimensions"]["hauteur"] #lire les dimension(hauteur) de la carte dans json
        self.largeur = carte["dimensions"]["largeur"]  #lire les dimension(largeur) de la carte dans json
        self.position: Case = tuple(carte["depart_robot"]) #lire la position(case) du départ de robit

    # -- la realite --------------------------------------------------------

    def type_case(self, case: Case) -> str:
        """Type reel d'une case. Hors grille = mur (le bord est toujours
        un mur, donc on n'y arrive jamais en pratique)."""
        l, c = case
        if not (0 <= l < self.hauteur and 0 <= c < self.largeur):
            return "mur"
        return SYMBOLES[self._grille[l][c]]

    # -- ce que le robot recoit --------------------------------------------

    def percevoir(self) -> Perception:
        """Les 4 cases adjacentes a la position actuelle, et rien d'autre."""
        vus = {direction: self.type_case(case)
               for direction, case in voisins(self.position)}
        return Perception(position=self.position, voisins=vus)

    # -- ce que le robot fait ----------------------------------------------

    def avancer(self, direction: str) -> None:
        """Action AVANCER : la case visee doit etre libre (section 3.4)."""
        if direction not in Directions:
            raise DeplacementIllegal(f"direction inconnue {direction!r}")
        dl, dc = Directions[direction]
        cible = (self.position[0] + dl, self.position[1] + dc)
        if self.type_case(cible) != "libre":
            raise DeplacementIllegal(
                f"AVANCER {direction} depuis {self.position} : "
                f"{cible} est {self.type_case(cible)}"
            )
        self.position = cible

    def est_adjacent(self, cible: Case) -> bool:
        """Le robot est-il orthogonalement adjacent a `cible` ?
        (condition de CONSULTER, CHERCHER, PRENDRE, DONNER)"""
        return tuple(cible) in {v for _, v in voisins(self.position)}
