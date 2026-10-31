"""
Memoire du robot : la carte mentale.

C'est ce que le robot CROIT savoir de l'appartement. Elle est distincte de
la carte reelle (monde.py) : elle ne lit jamais le champ `grille`. Elle ne
se remplit qu'a partir de deux sources autorisees (section 3.2) :

  1. ce que le robot connait au depart : dimensions, sa position, celle de
     l'armoire, du dictionnaire et des residents ;
  2. ses perceptions successives (les 4 cases voisines a chaque tour).

Regle de planification : hypothese optimiste (annexe B.5). Une case jamais
vue est supposee traversable.
"""

from typing import Dict,Tuple,Iterable,List,Mapping,Optional

from reconfort.planification import voisins

Case = Tuple[int, int]

#Etat possible d'un état dans une carte mentale

INCONNU = "inconnu"
LIBRE = "libre"
MUR = "mur"
ARMOIRE = "armoire"
DICTIONNAIRE = "dictionnaire"
RESIDENT = "resident"

# Valeurs qu'une perception peut annoncer (section 5.5).
VALEURS_PERCUES = {LIBRE, MUR, ARMOIRE, DICTIONNAIRE, RESIDENT}

# Cases que le robot ne peut pas traverser (section 3.1).
OBSTACLES = {MUR, ARMOIRE, DICTIONNAIRE, RESIDENT}

class CarteMentale:
    """Carte mentale du robot.

    Representation : un dictionnaire {case: etat} qui ne contient que les
    cases CONNUES. Une case absente du dictionnaire est INCONNU. C'est
    economique : au debut, presque tout est inconnu.
    """
    def __init__(
        self,
        hauteur: int,
        largeur: int,
        depart: Case,
        armoire: Case,
        dictionnaire: Case,
        residents: Iterable[Case],
        bord_connu: bool = True,
    ) -> None:
        """
        bord_connu : la section 3.1 affirme que le bord de la grille est
        toujours un mur. C'est une regle du monde, pas une lecture de la
        grille ; on peut donc l'inscrire d'emblee. Mettre False pour ne
        rien supposer.
        """
        self.hauteur = hauteur
        self.largeur = largeur
        self.cases: Dict[Case, str] = {}

        if bord_connu:
            for c in range(largeur):
                self.cases[(0, c)] = MUR
                self.cases[(hauteur - 1, c)] = MUR
            for l in range(hauteur):
                self.cases[(l, 0)] = MUR
                self.cases[(l, largeur - 1)] = MUR

        # Ce que le robot sait des le depart (section 3.2).
        self.cases[tuple(depart)] = LIBRE
        self.cases[tuple(armoire)] = ARMOIRE
        self.cases[tuple(dictionnaire)] = DICTIONNAIRE
        for position in residents:
            self.cases[tuple(position)] = RESIDENT



# -- consultation ------------------------------------------------------


    def dans_grille(self, case: Case) -> bool:
        l, c = case
        return 0 <= l < self.hauteur and 0 <= c < self.largeur

    def etat(self, case: Case) -> str:
        """Return état connu (valeur ou string ) de la case si non return INCONNU si jamais vue."""
        return self.cases.get(case, INCONNU)

    def est_traversable(self, case: Case) -> bool:
        """Hypothese optimiste : inconnu = traversable.
        Hors grille et obstacles connus = non traversable.
        C'est cette methode qu'on passe au BFS."""
        if not self.dans_grille(case):
            return False
        return self.etat(case) not in OBSTACLES

    def arrivees_autour(self, cible: Case) -> List[Case]:
        """Cases ou le robot peut se placer pour interagir avec `cible`
        (armoire, dictionnaire, resident) : ses voisines orthogonales,
        si elles sont encore supposees traversables.

        A recalculer a chaque tour : une voisine peut se reveler etre un mur."""
        return [v for _, v in voisins(tuple(cible)) if self.est_traversable(v)]


 # -- mise a jour -------------------------------------------------------

    def mettre_a_jour(self, position: Case, perception: Mapping[str, str]) -> None:
        """Inscrit une perception : la case du robot est libre, et chacune
        des 4 voisines prend l'etat percu.

        perception : {"N": "libre", "S": "mur", "E": ..., "O": ...}
        """
        position = tuple(position)
        self.cases[position] = LIBRE
        for direction, voisin in voisins(position):
            valeur = perception[direction]
            if valeur not in VALEURS_PERCUES:
                raise ValueError(f"perception inconnue {valeur!r} en {direction}")
            self.cases[voisin] = valeur

    # -- affichage  ------------------------------------------

    def dessiner(self, robot: Optional[Case] = None) -> str:
        """Representation texte de la carte mentale. '?' = inconnu."""
        symboles = {INCONNU: "?", LIBRE: ".", MUR: "#", ARMOIRE: "A",
                    DICTIONNAIRE: "D", RESIDENT: "P"}
        lignes = []
        for l in range(self.hauteur):
            ligne = ""
            for c in range(self.largeur):
                if robot is not None and (l, c) == tuple(robot):
                    ligne += "R"
                else:
                    ligne += symboles[self.etat((l, c))]# Si c'est INCONNU retourné par "self.etat((l,c))" alors ligne += "?"
            lignes.append(ligne)
        return "\n".join(lignes)







"""
>>> list((6, 4))      # tuple → list
[6, 4]
>>> tuple([6, 4])     # list → tuple
(6, 4)
"""