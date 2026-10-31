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

    def __init__(self, carte: Dict[str, Any],armoire: Dict[str, Any] = None) -> None:
        self._grille = carte["grille"]                 # reserve au simulateur,lire la grille de la carte dans le json
        self.hauteur = carte["dimensions"]["hauteur"] #lire les dimension(hauteur) de la carte dans json
        self.largeur = carte["dimensions"]["largeur"]  #lire les dimension(largeur) de la carte dans json
        self.position: Case = tuple(carte["depart_robot"]) #lire la position(case) du départ de robit

        # Contenu reel de l'armoire : SEUL endroit ou l'on lit le champ "objet".
        self._contenu: Dict[Case, Any] = {}
        self.selecteur: Case = (0, 0)
        self.nb_lignes = 3
        self.nb_colonnes = 8
        if armoire is not None:
            for casier in armoire["casiers"]:
                self._contenu[(casier["ligne"], casier["colonne"])] = casier["objet"]
            self.selecteur = tuple(armoire["casier_depart"])
            self.nb_lignes = len(armoire["intensites"])
            self.nb_colonnes = len(armoire["emotions"])

 
    # -- l'armoire --------------------------------------------------------
 #les fonction dans fouille_armoire.py vont appeler cette fonction pour savoir l'objet
    def contenu_casier(self, ligne: int, colonne: int):
        """Ce qu'il y a reellement dans ce casier (None s'il est vide).
        Passee a chercher_objet sous le nom voir_casier."""
        return self._contenu.get((ligne, colonne))
 
    def prendre(self, ligne: int, colonne: int):
        """Action PRENDRE : retire l'objet du casier et le renvoie."""
        return self._contenu.pop((ligne, colonne), None)

    def chercher(self, direction: str) -> None:
            """Action CHERCHER : deplace le selecteur d'un casier.
            N/S changent la ligne SANS bouclage, E/O changent la colonne AVEC bouclage."""
            l, c = self.selecteur
            if direction == "N":
                l -= 1
            elif direction == "S":
                l += 1
            elif direction == "E":
                c = (c + 1) % self.nb_colonnes
            elif direction == "O":
                c = (c - 1) % self.nb_colonnes
            else:
                raise DeplacementIllegal(f"direction inconnue {direction!r}")
            if not 0 <= l < self.nb_lignes:
                raise DeplacementIllegal(f"CHERCHER {direction} : le selecteur sortirait de l'armoire")
            self.selecteur = (l, c)
    
    def contenu_courant(self):
        """L'objet du casier devant lequel se trouve le selecteur (None si vide)."""
        return self._contenu.get(self.selecteur)


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

    

    

    