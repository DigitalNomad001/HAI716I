import json
import tempfile
import unittest
from pathlib import Path
 
import reconfort.reconfort_io as rio
from reconfort.fouille_armoire import aller_au_casier, chercher_objet
 
CHEMIN_ARMOIRE = "donnees/armoire_standard.json"
 
 
def directions(actions):
    """Garde seulement les directions des actions CHERCHER, ex. ["E", "E", "N"]."""
    return [arg for action, arg in actions if action == "CHERCHER"]
 
 
class TestFouilleArmoireReelle(unittest.TestCase):
 
    @classmethod
    def setUpClass(cls):
        cls.armoire = rio.charger_armoire(CHEMIN_ARMOIRE)
 
    def chercher(self, emotion, intensite, selecteur=None, vus=None):
        #Lance une fouille. Par defaut : selecteur au casier de depart de l'armoire ([1, 0]) et memoire vide
        if selecteur is None:
            selecteur = list(self.armoire["casier_depart"])
        if vus is None:
            vus = {}
        return chercher_objet(emotion, intensite, selecteur, self.armoire, vus)
 
    # ---------------------------------------------------------------------------
    # Déplacement du selecteur, bouclage 7 <-> 0
    # ---------------------------------------------------------------------------
 
    def test_selecteur_bouclage_de_0_vers_7(self):
        # Depart en colonne 0, on vise anticipation (colonne 7) : un seul pas vers la gauche, de 0 a 7
        objet, casier, _, selecteur, actions = self.chercher("anticipation", "moyenne")
        self.assertEqual(directions(actions), ["O"])
        self.assertEqual((objet, casier, selecteur), ("calendrier", [1, 7], [1, 7]))
 
    def test_selecteur_bouclage_de_7_vers_0(self):
        # Depart en colonne 7, on vise joie (colonne 0) : un seul pas vers la droite, de 7 a 0
        objet, casier, _, _, actions = self.chercher("joie", "moyenne", selecteur=[1, 7])
        self.assertEqual(directions(actions), ["E"])
        self.assertEqual((objet, casier), ("photo de famille", [1, 0]))
 
    def test_selecteur_voit_les_casiers_en_traversant_la_boucle(self):
        # De [1, 7] a [1, 1] en passant par la colonne 0 : le robot note le vrai contenu de chaque casier traverse
        vus, actions = {}, []
        selecteur = aller_au_casier([1, 7], 1, 1, self.armoire, vus, actions)
        self.assertEqual(selecteur, [1, 1])
        self.assertEqual(directions(actions), ["E", "E"])
        self.assertEqual(vus, {(1, 0): "photo de famille", (1, 1): "plaid"})
 
    def test_exemple_annexe_c5(self):
        # La fouille deroulee de l'annexe C.5 : surprise forte depuis [1, 0]
        objet, casier, repli, _, actions = self.chercher("surprise", "forte")
        self.assertEqual((objet, casier, repli), ("telephone", [2, 4], "voisine_1"))
        self.assertEqual(len(directions(actions)), 9)
 
    # ---------------------------------------------------------------------------
    # Règle de repli
    # ---------------------------------------------------------------------------
 
    def test_repli_casier_exact_garni(self):
        objet, casier, repli, _, actions = self.chercher("tristesse", "moyenne")
        self.assertEqual((objet, casier, repli), ("couverture", [1, 4], "aucun"))
        self.assertEqual(actions[-1], ("PRENDRE", "couverture"))
 
    def test_repli_intensite(self):
        # Le casier [2, 7] (anticipation forte) est vide : on prend la meme emotion avec l'intensite la plus proche
        objet, casier, repli, _, _ = self.chercher("anticipation", "forte")
        self.assertEqual((objet, casier, repli), ("calendrier", [1, 7], "intensite"))
 
    def test_repli_colonne_entiere_vide_voisine(self):
        # La colonne 3 (surprise) est entierement vide : on passe a la voisine dans le sens horaire, la colonne 4 (tristesse)
        objet, casier, repli, _, _ = self.chercher("surprise", "moyenne")
        self.assertEqual((objet, casier, repli), ("couverture", [1, 4], "voisine_1"))
 
    def test_repli_aucun_casier_garni_a_distance_2(self):
        # L'armoire standard n'a pas ce cas : on en fabrique une copie dans un dossier temporaire, 
        # où les colonnes 1 a 5 (surprise = 3 et ses voisines a 1 et 2 crans) sont videes, puis on la recharge avec le vrai charger_armoire
        with open(CHEMIN_ARMOIRE, encoding="utf-8") as f:
            donnees = json.load(f)
        for casier in donnees["casiers"]:
            if 1 <= casier["colonne"] <= 5:
                casier["objet"] = None
 
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "armoire_trouee.json"
            chemin.write_text(json.dumps(donnees), encoding="utf-8")
            armoire = rio.charger_armoire(chemin)
 
        objet, casier, repli, _, actions = chercher_objet(
            "surprise", "moyenne", [1, 0], armoire, {})
        self.assertEqual((objet, casier, repli), (None, None, None))
        self.assertNotIn("PRENDRE", [action for action, arg in actions])
 
    # ---------------------------------------------------------------------------
    # Plusieurs demandes a la suite (etat garde entre les demandes)
    # ---------------------------------------------------------------------------
 
    def test_plusieurs_demandes_a_la_suite(self):
        # Le selecteur et la memoire "vus" sont gardes d'une demande a l'autre
        selecteur, vus = list(self.armoire["casier_depart"]), {}
        resultats = []
        for emotion, intensite in [("tristesse", "moyenne"), ("surprise", "forte"), ("anticipation", "forte")]:
            objet, _, repli, selecteur, _ = chercher_objet(emotion, intensite, selecteur, self.armoire, vus)
            resultats.append((objet, repli))
 
        self.assertEqual(resultats, [("couverture", "aucun"), ("telephone", "voisine_1"), ("calendrier", "intensite")])
 
 
if __name__ == "__main__":
    unittest.main()
