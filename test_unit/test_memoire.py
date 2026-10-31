"""Tests de la carte mentale (memoire.py)."""

import unittest

from reconfort.memoire import CarteMentale


# Appartement imaginaire de 7 lignes et 9 colonnes.
# On ne donne au robot QUE ce qu'il a le droit de connaitre au depart
# (section 3.2) : pas de grille.
#
#        c=0 1 2 3 4 5 6 7 8
#   l=0    # # # # # # # # #      le bord est connu comme mur
#   l=1    # ? ? ? A ? ? ? #      A = armoire (1, 4)
#   l=2    # ? ? ? ? ? ? ? #
#   l=3    # R ? ? ? ? ? P #      R = depart (3, 1), P = resident (3, 7)
#   l=4    # ? ? ? ? ? ? ? #
#   l=5    # ? ? ? D ? ? ? #      D = dictionnaire (5, 4)
#   l=6    # # # # # # # # #

HAUTEUR = 7
LARGEUR = 9
DEPART = (3, 1)
ARMOIRE = (1, 4)
DICTIONNAIRE = (5, 4)
RESIDENT = (3, 7)


class TestEtatInitial(unittest.TestCase):
    """Ce que la carte mentale contient juste apres sa creation."""

    def setUp(self):
        # Execute avant CHAQUE test : chaque test a sa propre carte neuve.
        self.carte = CarteMentale(HAUTEUR, LARGEUR, DEPART, ARMOIRE,
                                  DICTIONNAIRE, [RESIDENT])

    def test_case_interieure_inconnue(self):
        self.assertEqual(self.carte.etat((3, 4)), "inconnu")

    def test_case_inconnue_traversable(self):
        # Hypothese optimiste : ce qu'on n'a jamais vu est suppose libre.
        self.assertTrue(self.carte.est_traversable((3, 4)))

    def test_positions_connues_au_depart(self):
        self.assertEqual(self.carte.etat(DEPART), "libre")
        self.assertEqual(self.carte.etat(ARMOIRE), "armoire")
        self.assertEqual(self.carte.etat(DICTIONNAIRE), "dictionnaire")
        self.assertEqual(self.carte.etat(RESIDENT), "resident")

    def test_meubles_et_resident_non_traversables(self):
        self.assertFalse(self.carte.est_traversable(ARMOIRE))
        self.assertFalse(self.carte.est_traversable(DICTIONNAIRE))
        self.assertFalse(self.carte.est_traversable(RESIDENT))

    def test_bord_est_un_mur(self):
        self.assertEqual(self.carte.etat((0, 5)), "mur")   # bord du haut
        self.assertEqual(self.carte.etat((6, 5)), "mur")   # bord du bas
        self.assertEqual(self.carte.etat((3, 0)), "mur")   # bord gauche
        self.assertEqual(self.carte.etat((3, 8)), "mur")   # bord droit

    def test_hors_grille_non_traversable(self):
        self.assertFalse(self.carte.est_traversable((-1, 3)))   # au-dessus
        self.assertFalse(self.carte.est_traversable((7, 3)))    # en dessous
        self.assertFalse(self.carte.est_traversable((3, -1)))   # a gauche
        self.assertFalse(self.carte.est_traversable((3, 9)))    # a droite


class TestBordNonSuppose(unittest.TestCase):
    """Avec bord_connu=False, le robot ne suppose rien sur le bord."""

    def test_bord_inconnu(self):
        carte = CarteMentale(HAUTEUR, LARGEUR, DEPART, ARMOIRE,
                             DICTIONNAIRE, [RESIDENT], bord_connu=False)
        self.assertEqual(carte.etat((0, 5)), "inconnu")


class TestMiseAJour(unittest.TestCase):
    """Ce que change une perception."""

    def setUp(self):
        self.carte = CarteMentale(HAUTEUR, LARGEUR, DEPART, ARMOIRE,
                                  DICTIONNAIRE, [RESIDENT])

    def test_mur_percu_devient_non_traversable(self):
        # Le robot est en (3, 3) et voit un mur au nord, c'est-a-dire en (2, 3).
        self.assertTrue(self.carte.est_traversable((2, 3)))       # avant
        self.carte.mettre_a_jour((3, 3), {"N": "mur", "S": "libre",
                                          "E": "libre", "O": "libre"})
        self.assertEqual(self.carte.etat((2, 3)), "mur")
        self.assertFalse(self.carte.est_traversable((2, 3)))      # apres

    def test_voisines_libres_et_case_du_robot(self):
        self.carte.mettre_a_jour((3, 3), {"N": "mur", "S": "libre",
                                          "E": "libre", "O": "libre"})
        self.assertEqual(self.carte.etat((4, 3)), "libre")   # sud
        self.assertEqual(self.carte.etat((3, 4)), "libre")   # est
        self.assertEqual(self.carte.etat((3, 2)), "libre")   # ouest
        self.assertEqual(self.carte.etat((3, 3)), "libre")   # la case du robot

    def test_perception_invalide_refusee(self):
        # "porte" n'est pas une valeur autorisee par la section 5.5.
        with self.assertRaises(ValueError):
            self.carte.mettre_a_jour((3, 3), {"N": "porte", "S": "libre",
                                              "E": "libre", "O": "libre"})


class TestArriveesAutour(unittest.TestCase):
    """Les cases ou le robot peut se placer a cote d'une cible."""

    def setUp(self):
        self.carte = CarteMentale(HAUTEUR, LARGEUR, DEPART, ARMOIRE,
                                  DICTIONNAIRE, [RESIDENT])

    def test_voisines_du_resident_au_depart(self):
        # Voisines de (3, 7) : (2, 7) N, (4, 7) S, (3, 8) E, (3, 6) O.
        # (3, 8) est sur le bord, donc un mur connu : exclue.
        resultat = sorted(self.carte.arrivees_autour(RESIDENT))
        self.assertEqual(resultat, [(2, 7), (3, 6), (4, 7)])

    def test_voisine_decouverte_mur_exclue(self):
        # Le robot, en (2, 6), voit un mur a l'est : c'est (2, 7).
        self.carte.mettre_a_jour((2, 6), {"N": "mur", "S": "libre",
                                          "E": "mur", "O": "libre"})
        resultat = sorted(self.carte.arrivees_autour(RESIDENT))
        self.assertEqual(resultat, [(3, 6), (4, 7)])


if __name__ == "__main__":
    unittest.main()
