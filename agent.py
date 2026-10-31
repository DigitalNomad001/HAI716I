#!/usr/bin/env python3
"""
Robot :programme principal.

python3 agent.py <carte.json> <scenario.json> <dossier_donnees> <trace.json>

Pour chaque demande du scenario, le robot :
  1. va a cote du dictionnaire, CONSULTER (lit l'emotion du message) ;
  2. va a cote de l'armoire, CHERCHER ... puis PRENDRE ;
  3. va a cote du resident, DONNER.
Chaque action est ecrite dans la trace AVANT d'etre executee
(position, casier et perception sont ceux d'avant l'action, section 5.5).

En cas de fichier invalide : message sur stderr, code de sortie 1,
et AUCUNE trace n'est ecrite.
"""

import sys
from pathlib import Path

from reconfort import reconfort_io as rio
from reconfort import validation
from reconfort.fouille_armoire import chercher_objet
from reconfort.lecture_emotion import lire_emotion
from reconfort.memoire import CarteMentale
from reconfort.monde import Monde
from reconfort.navigation import aller_vers


EQUIPE = ["LI Hao", "TAGA Aoto"]



# Chargement : lecture (reconfort_io) puis validation du contenu (validation.py)


def charger_tout(chemin_carte, chemin_scenario, dossier):
    """Charge et valide les quatre fichiers. Leve ErreurFichier au premier probleme."""
    dossier = Path(dossier)

    carte = rio.charger_carte(chemin_carte)
    validation.valider_carte(carte, chemin_carte)

    scenario = rio.charger_scenario(chemin_scenario)
    validation.valider_scenario(scenario, chemin_scenario)

    chemin_dictionnaire = dossier / "dictionnaire.json"
    dictionnaire = rio.charger_dictionnaire(chemin_dictionnaire)
    validation.valider_dictionnaire(dictionnaire, chemin_dictionnaire)

    # le nom de l'armoire vient du scenario (deja valide : c'est bien un str)
    chemin_armoire = dossier / f"{scenario['armoire']}.json"
    armoire = rio.charger_armoire(chemin_armoire)
    validation.valider_armoire(armoire, chemin_armoire)

    validation.verifier_coherence(carte, scenario, dictionnaire, armoire)
    return carte, scenario, dictionnaire, armoire


# Le robot


class Robot:
    """Relie le monde (simulateur), la memoire et la trace."""

    def __init__(self, carte, scenario, dictionnaire, armoire):
        self.dictionnaire = dictionnaire
        self.armoire = armoire
        self.monde = Monde(carte, armoire)                 # la realite
        self.pos_armoire = tuple(carte["armoire"]["position"])
        self.pos_dictionnaire = tuple(carte["dictionnaire"]["position"])
        self.residents = {r["id"]: tuple(r["position"]) for r in carte["residents"]}

        # La memoire : uniquement ce que la section 3.2 autorise.
        self.memoire = CarteMentale(
            hauteur=carte["dimensions"]["hauteur"],
            largeur=carte["dimensions"]["largeur"],
            depart=tuple(carte["depart_robot"]),
            armoire=self.pos_armoire,
            dictionnaire=self.pos_dictionnaire,
            residents=self.residents.values(),
        )
        self.vus = {}                       # casiers deja vus : (l, c) -> objet ou None
        self.trace = rio.Trace(carte["nom"], scenario["nom"], EQUIPE)

    # -- ecriture d'un pas, AVANT l'action ---------------------------------

    def noter(self, demande, action, argument=None, perception=None):
        if perception is None:
            perception = self.monde.percevoir()
        devant_armoire = self.monde.est_adjacent(self.pos_armoire)
        self.trace.ajouter_pas(
            demande=demande,
            position=self.monde.position,
            casier=self.monde.selecteur,
            action=action,
            argument=argument,
            perception=perception.voisins,
            contenu_casier=self.monde.contenu_courant() if devant_armoire else None,
        )

    def aller(self, demande, cible):
        """Marche jusqu'a cote de la cible ; chaque pas AVANCER est note."""
        def observateur(perception, direction):
            self.noter(demande, "AVANCER", direction, perception)
        return aller_vers(self.monde, self.memoire, cible, observateur).arrive

    # -- une demande --------------------------------------------------------

    def traiter(self, numero, demande):
        resident = demande["resident"]
        emotion = intensite = casier = objet = None
        repli = "aucun"

        def echec(motif):
            self.trace.ajouter_livraison(numero, resident, emotion, intensite,
                                         casier, repli, objet, False, motif)

        # 1. Dictionnaire
        if not self.aller(numero, self.pos_dictionnaire):
            return echec("dictionnaire inaccessible")
        self.noter(numero, "CONSULTER")
        lu = lire_emotion(demande["message"], self.dictionnaire)
        if lu is None:
            return echec("emotion indeterminee")
        emotion, intensite = lu

        # 2. Armoire : on calcule la fouille, puis on l'execute pas a pas.
        if not self.aller(numero, self.pos_armoire):
            return echec("armoire inaccessible")
        objet, casier, repli, _, actions = chercher_objet(
            emotion, intensite, self.monde.selecteur, self.armoire,
            self.vus, self.monde.contenu_casier)
        for action, argument in actions:
            self.noter(numero, action, argument)
            if action == "CHERCHER":
                self.monde.chercher(argument)
            elif action == "PRENDRE":
                self.monde.prendre(*self.monde.selecteur)
        if objet is None:
            return echec("armoire vide")

        # 3. Resident
        if not self.aller(numero, self.residents[resident]):
            return echec("resident inaccessible")
        self.noter(numero, "DONNER", objet)
        self.trace.ajouter_livraison(numero, resident, emotion, intensite,
                                     casier, repli, objet, True)


# ---------------------------------------------------------------------------

def main(argv):
    if len(argv) != 5:
        print("usage : python3 agent.py <carte.json> <scenario.json> "
              "<dossier_donnees> <trace.json>", file=sys.stderr)
        return 1
    try:
        carte, scenario, dictionnaire, armoire = charger_tout(argv[1], argv[2], argv[3])
    except rio.ErreurFichier as err:
        print(f"erreur : {err}", file=sys.stderr)
        return 1                                   # aucune trace ecrite

    robot = Robot(carte, scenario, dictionnaire, armoire)
    for demande in scenario["demandes"]:
        robot.traiter(demande["numero"], demande)

    chemin = robot.trace.ecrire(argv[4])
    resume = robot.trace.en_dictionnaire()["resume"]
    print(f"trace ecrite : {chemin} ({resume['reussies']}/{resume['demandes']} "
          f"reussies, {resume['pas_total']} pas)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
