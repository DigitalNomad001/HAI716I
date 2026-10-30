"""
Tests d'intégration de lecture_emotion.py
Rien n'est remplacé par des mocks ici, on teste avec le vrai dictionnaire et la vraie fonction de normalisation

Pour lancer les tests, dans la racine du projet, taper :
    python3 -m unittest test_integration.test_lecture_emotion_reel -v
"""

import unittest
import reconfort.reconfort_io as rio
from reconfort.lecture_emotion import lire_emotion

class TestLectureEmotionReel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dico = rio.charger_dictionnaire("donnees/dictionnaire.json")
 
    def lire(self, message):
        return lire_emotion(message, self.dico)
 
    # ---------------------------------------------------------------------------
    # un message par émotion
    # ---------------------------------------------------------------------------
 
    def test_joie(self):
        self.assertEqual(self.lire("Ma fille a appelé, je suis vraiment heureux."), ("joie", "moyenne"))
 
    def test_confiance(self):
        self.assertEqual(self.lire("Je te fais confiance, tu sauras quoi faire."), ("confiance", "moyenne"))
 
    def test_peur(self):
        self.assertEqual(self.lire("Je suis TERRIFIÉE, il y a quelqu'un dehors !"), ("peur", "forte"))
 
    def test_surprise(self):
        self.assertEqual(self.lire("Je suis perplexe, cette porte était fermée."), ("surprise", "faible"))
 
    def test_tristesse(self):
        self.assertEqual(self.lire("Je me sens tellement seule ce soir."), ("tristesse", "moyenne"))
 
    def test_degout(self):
        self.assertEqual(self.lire("Cette odeur me dégoûte."), ("degout", "moyenne"))
 
    def test_colere(self):
        self.assertEqual(self.lire("Ce bouton est cassé, ça m'agace depuis hier."), ("colere", "faible"))
 
    def test_anticipation(self):
        self.assertEqual(self.lire("Je reste vigilante, j'entends du bruit."), ("anticipation", "forte"))
 
    # ---------------------------------------------------------------------------
    # deux mots connus dans le message : le premier gagne
    # ---------------------------------------------------------------------------
 
    def test_premier_mot_gagne(self):
        # "sidere" (surprise) arrive avant "seule" (tristesse).
        self.assertEqual(
            self.lire("Je suis sidéré, la télévision s'est allumée toute seule."), ("surprise", "forte"))
 
    def test_premier_mot_gagne_ordre_inverse(self):
        # Memes mots dans l'autre ordre : c'est "seule" qui gagne.
        self.assertEqual(self.lire("Toute seule, je suis sidérée."), ("tristesse", "moyenne"))
 
    # ---------------------------------------------------------------------------
    # aucun mot reconnu
    # ---------------------------------------------------------------------------
 
    def test_aucun_mot_reconnu(self):
        # Doit donner l'echec "emotion indeterminee".
        self.assertIsNone(self.lire("Bonjour, il fait beau aujourd'hui."))
 
 
if __name__ == "__main__":
    unittest.main()
