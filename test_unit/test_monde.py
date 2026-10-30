"""Tests du simulateur (monde.py)."""

import unittest

from reconfort.monde import DeplacementIllegal, Monde


# Grille de appartement_01, avec les coordonnees :
#
#          c=0 1 2 3 4 5 6 7 8 9 10 11 12
#   l=0      # # # # # # # # # # #  #  #
#   l=1      # . . . . . . # . . .  .  #
#   l=2      # . . . . . . . . . .  .  #
#   l=3      # . . P . . . # . . .  .  #
#   l=4      # . # # # # # # # # #  .  #
#   l=5      # . . . . . . # . . .  .  #
#   l=6      # R . . A . . # . . .  P  #      R = depart (6, 1), A = armoire (6, 4)
#   l=7      # . . . . . D # . . .  .  #      D = dictionnaire (7, 6)
#   l=8      # # # # # # # # # # #  #  #

# Le dictionnaire qu'on obtiendrait en lisant le fichier carte.
# Monde n'utilise que "grille", "dimensions" et "depart_robot".
CARTE = {
    "dimensions": {"hauteur": 9, "largeur": 13},
    "grille": [
        "#############",
        "#......#....#",
        "#...........#",
        "#..P...#....#",
        "#.#########.#",
        "#......#....#",
        "#R..A..#...P#",
        "#.....D#....#",
        "#############",
    ],
    "depart_robot": [6, 1],
}


class TestMonde(unittest.TestCase):

    def setUp(self):
        # Un monde neuf avant chaque test : le robot est toujours au depart.
        self.monde = Monde(CARTE)

    # -- position ---------------------------------------------------------

    def test_position_de_depart(self):
        # [6, 1] dans le fichier devient le tuple (6, 1).
        self.assertEqual(self.monde.position, (6, 1))

    # -- perception -------------------------------------------------------

    def test_perception_au_depart(self):
        # Depuis (6, 1) : N = (5, 1) '.', S = (7, 1) '.', E = (6, 2) '.', O = (6, 0) '#'
        p = self.monde.percevoir()
        self.assertEqual(p.position, (6, 1))
        self.assertEqual(p.voisins, {"N": "libre", "S": "libre",
                                     "E": "libre", "O": "mur"})

    def test_perception_voit_l_armoire(self):
        # Depuis (6, 3), l'armoire (6, 4) est a l'est.
        self.monde.position = (6, 3)
        p = self.monde.percevoir()
        self.assertEqual(p.voisins["E"], "armoire")

    def test_perception_voit_dictionnaire_et_mur(self):
        # Depuis (6, 6) : le dictionnaire (7, 6) est au sud, le mur (6, 7) a l'est.
        self.monde.position = (6, 6)
        p = self.monde.percevoir()
        self.assertEqual(p.voisins["S"], "dictionnaire")
        self.assertEqual(p.voisins["E"], "mur")

    def test_perception_voit_un_resident(self):
        # Depuis (6, 10), le resident (6, 11) est a l'est.
        self.monde.position = (6, 10)
        p = self.monde.percevoir()
        self.assertEqual(p.voisins["E"], "resident")

    # -- deplacement ------------------------------------------------------

    def test_avancer_sur_case_libre(self):
        self.monde.avancer("E")
        self.assertEqual(self.monde.position, (6, 2))

    def test_avancer_deux_fois(self):
        self.monde.avancer("N")          # (6, 1) -> (5, 1)
        self.monde.avancer("N")          # (5, 1) -> (4, 1)
        self.assertEqual(self.monde.position, (4, 1))

    def test_avancer_dans_un_mur_refuse(self):
        with self.assertRaises(DeplacementIllegal):
            self.monde.avancer("O")      # (6, 0) est un mur
        self.assertEqual(self.monde.position, (6, 1))   # le robot n'a pas bouge

    def test_avancer_dans_l_armoire_refuse(self):
        self.monde.position = (6, 3)
        with self.assertRaises(DeplacementIllegal):
            self.monde.avancer("E")      # (6, 4) est l'armoire

    def test_direction_inconnue_refusee(self):
        with self.assertRaises(DeplacementIllegal):
            self.monde.avancer("X")

    # -- adjacence --------------------------------------------------------

    def test_est_adjacent(self):
        self.monde.position = (6, 3)
        self.assertTrue(self.monde.est_adjacent((6, 4)))    # armoire juste a cote
        self.assertFalse(self.monde.est_adjacent((7, 6)))   # dictionnaire loin


if __name__ == "__main__":
    unittest.main()