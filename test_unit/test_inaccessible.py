"""Tests du cas inaccessible (section 8, point 7).

Un resident est emmure : le robot doit le decouvrir en explorant, conclure
qu'il est inaccessible, et S'ARRETER (pas de boucle infinie).
"""

import unittest

from reconfort.memoire import CarteMentale
from reconfort.monde import Monde
from reconfort.navigation import aller_vers


# Petite grille ecrite a la main :
#
#          c=0 1 2 3 4 5 6
#   l=0      # # # # # # #
#   l=1      # R . . # . #      R = depart (1, 1)
#   l=2      # . . . # P #      P = resident (2, 5)
#   l=3      # A D . # # #      A = armoire (3, 1), D = dictionnaire (3, 2)
#   l=4      # # # # # # #
#
# Le resident (2, 5) n'a qu'une voisine libre, (1, 5), elle-meme entouree
# de murs : aucun chemin depuis R. Le robot ne le sait pas au depart.

GRILLE = [
    "#######",
    "#R..#.#",
    "#...#P#",
    "#AD.###",
    "#######",
]

HAUTEUR = 5
LARGEUR = 7
DEPART = (1, 1)
ARMOIRE = (3, 1)
DICTIONNAIRE = (3, 2)
RESIDENT = (2, 5)

# Le dictionnaire qu'on obtiendrait en lisant le fichier carte.
# Monde n'utilise que "grille", "dimensions" et "depart_robot".
CARTE = {
    "dimensions": {"hauteur": HAUTEUR, "largeur": LARGEUR},
    "grille": GRILLE,
    "depart_robot": list(DEPART),
}


class TestInaccessible(unittest.TestCase):

    def setUp(self):
        # Le monde reel (le simulateur, qui connait la grille)...
        self.monde = Monde(CARTE)
        # ... et la memoire du robot, qui ne recoit PAS la grille.
        self.memoire = CarteMentale(HAUTEUR, LARGEUR, DEPART, ARMOIRE,
                                    DICTIONNAIRE, [RESIDENT])

    def test_resident_emmure_echoue(self):
        resultat = aller_vers(self.monde, self.memoire, RESIDENT)
        self.assertFalse(resultat.arrive)
        self.assertFalse(self.monde.est_adjacent(RESIDENT))

    def test_la_preuve_vient_de_l_exploration(self):
        # Au depart, la carte mentale suppose l'inconnu traversable :
        # le robot croit pouvoir y aller. Il doit donc marcher et decouvrir
        # les murs avant de conclure.
        resultat = aller_vers(self.monde, self.memoire, RESIDENT)
        self.assertGreater(len(resultat.pas), 0)
        # Il a bien decouvert le mur de la colonne 4.
        self.assertEqual(self.memoire.etat((1, 4)), "mur")

    def test_le_robot_s_arrete(self):
        # Si aller_vers bouclait, il leverait RuntimeError apres MAX_PAS pas.
        # Ici il doit conclure bien avant.
        resultat = aller_vers(self.monde, self.memoire, RESIDENT)
        self.assertLess(len(resultat.pas), 50)

    def test_temoin_dictionnaire_accessible(self):
        # Sur la meme grille, le dictionnaire est atteignable :
        # le test precedent n'echoue donc pas pour une mauvaise raison.
        resultat = aller_vers(self.monde, self.memoire, DICTIONNAIRE)
        self.assertTrue(resultat.arrive)
        self.assertTrue(self.monde.est_adjacent(DICTIONNAIRE))


if __name__ == "__main__":
    unittest.main()