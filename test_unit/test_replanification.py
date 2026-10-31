"""Tests de la replanification (section 8, point 2) :
un mur decouvert en route change le trajet."""

import unittest

from reconfort.decision import choisir_pas
from reconfort.memoire import CarteMentale
from reconfort.monde import Monde
from reconfort.navigation import aller_vers
from reconfort.planification import plus_court_chemin


class TestReplanificationCarteMentale(unittest.TestCase):
    """Sans simulateur : seulement le BFS et la carte mentale.

    Grille REELLE de l'annexe B.3 (le robot ne la connait pas) :

             c=0 1 2 3 4 5
       l=0     # # # # # #
       l=1     # R . # T #      R = depart (1, 1), T = cible (1, 4)
       l=2     # . # . . #
       l=3     # . . . # #
       l=4     # # # # # #
    """

    def setUp(self):
        # Armoire et dictionnaire poses sur des murs, pour ne pas gener.
        self.carte = CarteMentale(5, 6, (1, 1), (2, 2), (3, 4), [])

    def test_mur_decouvert_change_le_trajet(self):
        # 1) Rien de connu : le plan optimiste va tout droit vers l'est.
        plan1 = plus_court_chemin((1, 1), {(1, 4)}, self.carte.est_traversable)
        self.assertEqual(plan1, [(1, 1), (1, 2), (1, 3), (1, 4)])

        # 2) Le robot avance en (1, 2) et voit un mur a l'est : (1, 3).
        self.carte.mettre_a_jour((1, 2), {"N": "mur", "S": "mur",
                                          "E": "mur", "O": "libre"})

        # 3) Nouveau plan : il evite (1, 3), passe par le bas, et il est plus long.
        plan2 = plus_court_chemin((1, 2), {(1, 4)}, self.carte.est_traversable)
        self.assertIsNotNone(plan2)
        self.assertNotIn((1, 3), plan2)
        self.assertEqual(plan2[-1], (1, 4))
        self.assertGreater(len(plan2), len(plan1))

    def test_la_decision_change_de_direction(self):
        # Meme chose vu par choisir_pas : le premier pas change.
        cible = (1, 4)
        # cible ici = une case libre ; on veut se placer a cote d'elle.
        # Avant : aller vers l'est.
        self.assertEqual(choisir_pas(self.carte, (1, 2), cible), ("AVANCER", "E"))
        # Le robot voit le mur en (1, 3) :
        self.carte.mettre_a_jour((1, 2), {"N": "mur", "S": "mur",
                                          "E": "mur", "O": "libre"})
        # Apres : il doit faire demi-tour vers l'ouest.
        self.assertEqual(choisir_pas(self.carte, (1, 2), cible), ("AVANCER", "O"))


class TestReplanificationEnSituation(unittest.TestCase):
    """Avec le simulateur, sur appartement_01 (annexe D).

             c=0 1 2 3 4 5 6 7 8 9 10 11 12
       l=0     # # # # # # # # # # #  #  #
       l=1     # . . . . . . # . . .  .  #
       l=2     # . . . . . . . . . .  .  #
       l=3     # . . P . . . # . . .  .  #
       l=4     # . # # # # # # # # #  .  #      seul passage vers la droite : (4, 11)
       l=5     # . . . . . . # . . .  .  #
       l=6     # R . . A . . # . . .  P  #      R1 = (6, 11)
       l=7     # . . . . . D # . . .  .  #
       l=8     # # # # # # # # # # #  #  #
    """

    GRILLE = [
        "#############",
        "#......#....#",
        "#...........#",
        "#..P...#....#",
        "#.#########.#",
        "#......#....#",
        "#R..A..#...P#",
        "#.....D#....#",
        "#############",
    ]

    def test_contourne_les_murs_pour_rejoindre_r1(self):
        carte = {"dimensions": {"hauteur": 9, "largeur": 13},
                 "grille": self.GRILLE, "depart_robot": [6, 1]}
        monde = Monde(carte)
        memoire = CarteMentale(9, 13, (6, 1), (6, 4), (7, 6), [(6, 11), (3, 3)])

        resultat = aller_vers(monde, memoire, (6, 11))

        self.assertTrue(resultat.arrive)
        # Il a decouvert au moins un mur de la colonne 7 en chemin...
        self.assertTrue(any(memoire.etat((l, 7)) == "mur" for l in range(1, 8)))
        # ... et il est passe par (4, 11), le seul passage.
        positions = [p.position for p, _ in resultat.pas] + [monde.position]
        self.assertIn((4, 11), positions)
        # Le plan optimiste initial faisait 9 pas ; le trajet reel est plus long.
        self.assertGreater(len(resultat.pas), 9)


if __name__ == "__main__":
    unittest.main()