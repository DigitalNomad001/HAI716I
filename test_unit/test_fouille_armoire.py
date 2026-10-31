"""
Tests unitaires de fouille_armoire.py

Pour lancer les tests, dans la racine du projet, taper :
    python3 -m unittest test_unit.test_fouille_armoire -v
"""

import unittest
from unittest.mock import patch

import reconfort.reconfort_io as rio
import reconfort.fouille_armoire as fouille
from reconfort.fouille_armoire import regarder_casier, liste_candidats, aller_au_casier, chercher_objet

EMOTIONS = ["joie", "confiance", "peur", "surprise", "tristesse", "degout", "colere", "anticipation"]
INTENSITES = ["faible", "moyenne", "forte"]

def creer_armoire_test(objets):
    casier = []
    for l in range(3):
        for c in range(8):
            casier.append({"ligne": l, "colonne": c, "objet": objets.get((l, c))})
    return {"emotions": EMOTIONS, "intensites": INTENSITES, "casiers": casier}

def directions(actions):
    return [arg for actions, arg in actions if actions == "CHERCHER"]

# ---------------------------------------------------------------------------
# regarder_casier
# ---------------------------------------------------------------------------

class TestRegarderCasier(unittest.TestCase):
    
    def setUp(self):
        self.armoire = creer_armoire_test({(1, 4): "couverture"})

    def test_casier_garni(self):
        self.assertEqual(regarder_casier(self.armoire, 1, 4), "couverture")

    def test_casier_vide(self):
        self.assertIsNone(regarder_casier(self.armoire, 0, 4))

    def test_casier_inexistant(self):
        self.assertIsNone(regarder_casier(self.armoire, 5, 9))


# ---------------------------------------------------------------------------
# liste_candidats
# ---------------------------------------------------------------------------

class TestListeCandidats(unittest.TestCase):

    def casiers(self, ligne, colonne):
        return [[l, c] for ordre, l, c, repli in liste_candidats(ligne, colonne)]

    def replis(self, ligne, colonne):
        return [repli for ordre, l, c, repli in liste_candidats(ligne, colonne)]
 
    def test_quinze_candidats_differents(self):
        casiers = self.casiers(1, 4)
        self.assertEqual(len(casiers), 15)
        self.assertEqual(len(set(map(tuple, casiers))), 15)
 
    def test_casier_exact_en_premier(self):
        self.assertEqual(self.casiers(1, 4)[0], [1, 4])
        self.assertEqual(self.replis(1, 4)[0], "aucun")
 
    def test_puis_meme_emotion_intensite_faible_avant_forte(self):
        # On vise "moyenne" : faible et forte sont a egalite (ecart 1), c'est la plus faible qui passe en premier
        self.assertEqual(self.casiers(1, 4)[1:3], [[0, 4], [2, 4]])
        self.assertEqual(self.replis(1, 4)[1:3], ["intensite", "intensite"])
 
    def test_intensite_la_plus_proche_d_abord(self):
        # On vise "faible" : moyenne (ecart 1) avant forte (ecart 2)
        self.assertEqual(self.casiers(0, 4)[1:3], [[1, 4], [2, 4]])
 
    def test_voisine_horaire_avant_antihoraire(self):
        # Apres la colonne visee : meme intensite a droite (+1), puis a gauche (-1)
        self.assertEqual(self.casiers(1, 4)[3:5], [[1, 5], [1, 3]])
 
    def test_ordre_des_replis(self):
        self.assertEqual(self.replis(1, 4), ["aucun"] + ["intensite"] * 2 + ["voisine_1"] * 6 + ["voisine_2"] * 6)
 
    def test_les_colonnes_bouclent_a_droite(self):
        # Colonne 7 (anticipation) : ses voisines sont 5, 6, 0 et 1.
        colonnes = {c for l, c in self.casiers(1, 7)}
        self.assertEqual(colonnes, {5, 6, 7, 0, 1})
 
    def test_les_colonnes_bouclent_a_gauche(self):
        # Colonne 0 (joie) : ses voisines sont 6, 7, 1 et 2.
        colonnes = {c for l, c in self.casiers(1, 0)}
        self.assertEqual(colonnes, {6, 7, 0, 1, 2})

# ---------------------------------------------------------------------------
# aller_au_casier
# ---------------------------------------------------------------------------

class TestAllerAuCasier(unittest.TestCase):
 
    def setUp(self):
        self.armoire = creer_armoire_test({(1, 1): "plaid", (1, 2): "radio"})
        self.vus = {}
        self.actions = []
 
    def aller(self, depart, arrivee):
        return aller_au_casier(depart, arrivee[0], arrivee[1], self.armoire, self.vus, self.actions)
 
    def test_deja_sur_place(self):
        self.assertEqual(self.aller([1, 3], [1, 3]), [1, 3])
        self.assertEqual(self.actions, [])
 
    def test_descendre(self):
        self.assertEqual(self.aller([0, 3], [2, 3]), [2, 3])
        self.assertEqual(directions(self.actions), ["S", "S"])
 
    def test_monter(self):
        self.aller([2, 3], [0, 3])
        self.assertEqual(directions(self.actions), ["N", "N"])
 
    def test_aller_a_droite(self):
        self.aller([1, 0], [1, 3])
        self.assertEqual(directions(self.actions), ["E", "E", "E"])
 
    def test_chemin_le_plus_court_en_bouclant(self):
        # De 1 a 7 : 6 pas a droite ou 2 a gauche (1 -> 0 -> 7)
        self.aller([1, 1], [1, 7])
        self.assertEqual(directions(self.actions), ["O", "O"])

    def test_bouclage_de_7_vers_0(self):
        # Colonne 7 -> colonne 0 : un seul pas vers la droite (E).
        self.assertEqual(self.aller([1, 7], [1, 0]), [1, 0])
        self.assertEqual(directions(self.actions), ["E"])
 
    def test_bouclage_de_0_vers_7(self):
        # Colonne 0 -> colonne 7 : un seul pas vers la gauche (O).
        self.assertEqual(self.aller([1, 0], [1, 7]), [1, 7])
        self.assertEqual(directions(self.actions), ["O"])

 
    def test_egalite_on_va_a_droite(self):
        # De 0 a 4 : 4 pas dans les deux sens, on va a droite
        self.aller([1, 0], [1, 4])
        self.assertEqual(directions(self.actions), ["E"] * 4)
 
    def test_ligne_puis_colonne(self):
        self.aller([0, 0], [2, 1])
        self.assertEqual(directions(self.actions), ["S", "S", "E"])
 
    def test_note_les_casiers_traverses(self):
        # En passant de [1, 0] a [1, 3], le robot voit [1, 1], [1, 2] et [1, 3]
        self.aller([1, 0], [1, 3])
        self.assertEqual(self.vus, {(1, 1): "plaid", (1, 2): "radio", (1, 3): None})
 
 
# ---------------------------------------------------------------------------
# chercher_objet
# ---------------------------------------------------------------------------
 
class TestChercherObjet(unittest.TestCase):
 
    def chercher(self, objets, emotion, intensite, selecteur=[1, 0], vus=None):
        if vus is None:
            vus = {}
        return chercher_objet(emotion, intensite, list(selecteur), creer_armoire_test(objets), vus)
 
    def test_casier_exact_garni(self):
        objet, casier, repli, selecteur, actions = self.chercher(
            {(1, 4): "couverture"}, "tristesse", "moyenne")
        self.assertEqual((objet, casier, repli), ("couverture", [1, 4], "aucun"))
        self.assertEqual(selecteur, [1, 4])
        self.assertEqual(actions[-1], ("PRENDRE", "couverture"))
 
    def test_repli_intensite(self):
        objet, casier, repli, _, _ = self.chercher(
            {(2, 4): "album"}, "tristesse", "moyenne")
        self.assertEqual((objet, casier, repli), ("album", [2, 4], "intensite"))
 
    def test_repli_voisine_1(self):
        # Colonne 4 vide, objet dans la colonne 3 (a gauche).
        objet, casier, repli, _, _ = self.chercher(
            {(1, 3): "boite"}, "tristesse", "moyenne")
        self.assertEqual((objet, casier, repli), ("boite", [1, 3], "voisine_1"))
 
    def test_repli_voisine_2(self):
        objet, casier, repli, _, _ = self.chercher(
            {(1, 6): "balle"}, "tristesse", "moyenne")
        self.assertEqual((objet, casier, repli), ("balle", [1, 6], "voisine_2"))
 
    def test_prend_le_meilleur_candidat(self):
        # Deux objets possibles : celui de la bonne emotion passe avant la voisine
        objet, _, repli, _, _ = self.chercher(
            {(1, 5): "voisin", (0, 4): "bon"}, "tristesse", "moyenne")
        self.assertEqual((objet, repli), ("bon", "intensite"))
 
    def test_trop_loin_armoire_vide(self):
        # Colonne 0 : a 4 crans de la colonne 4, hors des candidats
        objet, casier, repli, _, actions = self.chercher(
            {(1, 0): "loin"}, "tristesse", "moyenne")
        self.assertEqual((objet, casier, repli), (None, None, None))
        self.assertNotIn("PRENDRE", [action for action, arg in actions])
 
    def test_armoire_completement_vide(self):
        objet, _, _, _, actions = self.chercher({}, "tristesse", "moyenne")
        self.assertIsNone(objet)
        self.assertTrue(len(actions) > 0)   # le robot a quand meme cherche
 
    def test_memoire_casiers_deja_vus_vides(self):
        # Le robot sait deja que [1, 4] et [0, 4] sont vides : il va directement a [2, 4] (S + 4 E = 5 mouvements au lieu de 7)
        vus = {(1, 4): None, (0, 4): None}
        objet, _, _, _, actions = self.chercher(
            {(2, 4): "album"}, "tristesse", "moyenne", vus=vus)
        self.assertEqual(objet, "album")
        self.assertEqual(len(directions(actions)), 5)
 
    def test_vus_est_mis_a_jour(self):
        vus = {}
        self.chercher({(1, 2): "radio"}, "peur", "moyenne", vus=vus)
        # Le casier de depart et les casiers traverses sont memorises
        self.assertEqual(vus, {(1, 0): None, (1, 1): None, (1, 2): "radio"})
 
    @patch("reconfort.fouille_armoire.regarder_casier", wraps=fouille.regarder_casier)
    def test_ne_regarde_que_sous_le_selecteur(self, espion):
        # Mock "espion" : la vraie fonction est appelee, mais on note chaque appel. Le robot ne doit regarder que le casier de depart, 
        # puis chaque casier voisin ou il vient de deplacer le selecteur
        self.chercher({(2, 4): "album"}, "surprise", "forte")
        positions = [(appel.args[1], appel.args[2]) for appel in espion.call_args_list]
 
        self.assertEqual(positions[0], (1, 0))          # le casier de depart
        for (l1, c1), (l2, c2) in zip(positions, positions[1:]):
            un_pas_vertical = abs(l2 - l1) == 1 and c1 == c2
            un_pas_horizontal = l1 == l2 and (c2 - c1) % 8 in (1, 7)
            self.assertTrue(un_pas_vertical or un_pas_horizontal, f"saut de {(l1, c1)} a {(l2, c2)}")

if __name__ == "__main__":
    unittest.main()