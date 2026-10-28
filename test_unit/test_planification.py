"""Tests de la planification (section 8, point 1)."""

import unittest

from reconfort.planification import (
    direction_vers,
    plus_court_chemin,
    voisins,
)

# Grille de l'annexe B.3 : depart (1, 1), cible (1, 4), chemin de 7 pas.
GRILLE_B3 = [
    "######",
    "#..#.#",
    "#.#..#",
    "#...##",
    "######",
]


def traversable_dans(grille):
    """Fabrique une fonction est_traversable pour une grille ecrite a la main."""
    def est_traversable(case):
        l, c = case
        if not (0 <= l < len(grille) and 0 <= c < len(grille[0])):
            return False
        return grille[l][c] != "#"
    return est_traversable


class TestVoisins(unittest.TestCase):

    def test_quatre_voisins(self):
        self.assertEqual(
            voisins((3, 5)),
            [("N", (2, 5)), ("S", (4, 5)), ("E", (3, 6)), ("O", (3, 4))],
        )


class TestDirection(unittest.TestCase):

    def test_quatre_directions(self):
        self.assertEqual(direction_vers((3, 5), (2, 5)), "N")
        self.assertEqual(direction_vers((3, 5), (4, 5)), "S")
        self.assertEqual(direction_vers((3, 5), (3, 6)), "E")
        self.assertEqual(direction_vers((3, 5), (3, 4)), "O")

    def test_cases_non_adjacentes(self):
        with self.assertRaises(ValueError):
            direction_vers((3, 5), (3, 7))
        with self.assertRaises(ValueError):
            direction_vers((3, 5), (4, 6))      # diagonale interdite


class TestPlusCourtChemin(unittest.TestCase):

    def setUp(self):
        self.ok = traversable_dans(GRILLE_B3)

    def verifier_chemin_valide(self, chemin):
        """Chaque pas relie deux cases adjacentes et traversables."""
        for a, b in zip(chemin, chemin[1:]):
            direction_vers(a, b)                 # leve si non adjacentes
            self.assertTrue(self.ok(b), f"{b} n'est pas traversable")

    def test_exemple_annexe_b3(self):
        chemin = plus_court_chemin((1, 1), {(1, 4)}, self.ok)
        self.assertEqual(len(chemin) - 1, 7)
        self.assertEqual(chemin[0], (1, 1))
        self.assertEqual(chemin[-1], (1, 4))
        self.verifier_chemin_valide(chemin)

    def test_ne_passe_pas_par_le_cul_de_sac(self):
        # (1, 2) est a 1 pas mais bloque par le mur (1, 3) : le plus
        # court chemin passe par le bas.
        chemin = plus_court_chemin((1, 1), {(1, 4)}, self.ok)
        self.assertNotIn((1, 2), chemin)

    def test_depart_deja_arrive(self):
        self.assertEqual(plus_court_chemin((1, 1), {(1, 1)}, self.ok), [(1, 1)])

    def test_aucun_chemin(self):
        # On bloque (2, 4) : (1, 4) n'a plus aucun voisin traversable.
        bloque = lambda case: self.ok(case) and case != (2, 4)
        self.assertIsNone(plus_court_chemin((1, 1), {(1, 4)}, bloque))

    def test_arrivees_vide(self):
        self.assertIsNone(plus_court_chemin((1, 1), set(), self.ok))

    def test_plusieurs_arrivees_prend_la_plus_proche(self):
        # (3, 1) est a 2 pas, (1, 4) a 7 pas.
        chemin = plus_court_chemin((1, 1), {(1, 4), (3, 1)}, self.ok)
        self.assertEqual(chemin[-1], (3, 1))
        self.assertEqual(len(chemin) - 1, 2)

    def test_arrivee_non_traversable_inatteignable(self):
        # Une arrivee qui est un mur ne peut jamais etre atteinte.
        self.assertIsNone(plus_court_chemin((1, 1), {(0, 0)}, self.ok))


if __name__ == "__main__":
    unittest.main()
