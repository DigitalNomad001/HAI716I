"""
Tests unitaires de lectur_emotion.py

Pour lancer les tests, dans la racine du projet, taper :
    python3 -m unittest test_unit.test_lecture_emotion -v
"""


import unittest
from unittest.mock import patch

import reconfort.reconfort_io as rio
from reconfort.lecture_emotion import lire_emotion

DICO_TEST = {
    "entrees": [
        {"formes": ["triste", "tristesse"], "emotion": "tristesse", "intensite": "moyenne"},
        {"formes": ["content", "contente"], "emotion": "joie", "intensite": "faible"},
        {"formes": ["furieux"], "emotion": "colere", "intensite": "forte"},
    ]
}

@patch("reconfort.lecture_emotion.rio.normaliser")
class TestLectureEmotion(unittest.TestCase):
    
    def test_mot_reconnu(self, mock_normaliser):
        mock_normaliser.return_value = ["je", "suis", "triste"]
        self.assertEqual(lire_emotion("...", DICO_TEST), ("tristesse", "moyenne"))

    def test_autre_forme_reconnue(self, mock_normaliser):
        mock_normaliser.return_value = ["je", "suis", "contente"]
        self.assertEqual(lire_emotion("...", DICO_TEST), ("joie", "faible"))

    def test_aucun_mot_reconnu(self, mock_normaliser):
        mock_normaliser.return_value = ["il", "fait", "beau"]
        self.assertIsNone(lire_emotion("...", DICO_TEST))

    def test_premier_mot_gagne(self, mock_normaliser):
        mock_normaliser.return_value = ["triste", "mais", "content"]
        self.assertEqual(lire_emotion("...", DICO_TEST), ("tristesse", "moyenne"))

    def test_ordre_inverse(self, mock_normaliser):
        mock_normaliser.return_value = ["content", "mais", "triste"]
        self.assertEqual(lire_emotion("...", DICO_TEST), ("joie", "faible"))

    def test_aucun_mot(self, mock_normaliser):
        mock_normaliser.return_value = []
        self.assertIsNone(lire_emotion("...", DICO_TEST))

    def test_mot_partiel_non_reconnu(self, mock_normaliser):
        mock_normaliser.return_value = ["je", "suis", "tristounet"]
        self.assertIsNone(lire_emotion("...", DICO_TEST))

    def test_dictionnaire_vide(self, mock_normaliser):
        mock_normaliser.return_value = ["je", "suis", "triste"]
        self.assertIsNone(lire_emotion("...", {"entrees": []}))