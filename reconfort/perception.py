"""
Perception : ce que le robot recoit du monde a chaque tour.

C'est la SEULE information qui passe du simulateur (monde.py) vers l'agent.
L'agent ne voit jamais l'objet Monde lui-meme.
"""


from typing import Dict, Optional, Tuple



class Perception:
    """Ce que le robot percoit depuis sa position, a un tour donne.
    position       : case actuelle du robot (il connait sa position)
    voisins        : type des 4 cases adjacentes,
                     {"N": "libre", "S": "mur", "E": "armoire", "O": "libre"}
    contenu_casier : objet du casier courant si le robot est devant
                     l'armoire, None sinon (rempli plus tard, avec fouille.py) ...
    """

    def __init__(self, position: Tuple[int, int], voisins: Dict[str, str],
                 contenu_casier: Optional[str] = None) -> None:
        self.position = position
        self.voisins = voisins
        self.contenu_casier = contenu_casier

    def voit(self, valeur: str) -> bool:
        """True si l'une des 4 voisines est de ce type."""
        return valeur in self.voisins.values()