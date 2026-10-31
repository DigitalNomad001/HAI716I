#!/usr/bin/env python3
"""
Robot de reconfort -- programme principal.

    python3 agent.py <carte.json> <scenario.json> <dossier_donnees> <trace.json>

Pour chaque demande du scenario, le robot :
  1. va a cote du dictionnaire, CONSULTER (lit l'emotion du message) ;
  2. va a cote de l'armoire, CHERCHER ... puis PRENDRE ;
  3. va a cote du resident, DONNER.
Chaque action est ecrite dans la trace AVANT d'etre executee
(position, casier et perception sont ceux d'avant l'action, section 5.5).

En cas de fichier invalide : message sur stderr, code de sortie 1,
et AUCUNE trace n'est ecrite (section 5.6).
"""

import sys
import time
from pathlib import Path

from reconfort import reconfort_io as rio
from reconfort import validation
from reconfort.fouille_armoire import chercher_objet
from reconfort.lecture_emotion import lire_emotion
from reconfort.memoire import CarteMentale
from reconfort.monde import Monde
from reconfort.navigation import aller_vers

# A completer avec vos deux noms.
EQUIPE = ["FALCON Albane", "NOM Binome"]


# ---------------------------------------------------------------------------
# Chargement : lecture (reconfort_io) puis validation du contenu (validation.py)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Le robot
# ---------------------------------------------------------------------------

class Robot:
    """Relie le monde (simulateur), la memoire et la trace."""

    def __init__(self, carte, scenario, dictionnaire, armoire, pause=None):
        self.pause = pause                  # None : pas d'affichage ; sinon secondes entre deux pas
        self.etape = ""                     # pour l'affichage : ce que fait le robot
        self.en_tete = ""
        self.objet_porte = None
        self.nb_murs = 0
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
        if self.pause is not None:
            self.afficher(action, argument, devant_armoire)

    # -- affichage dans le terminal (video) ----------------------------------

    def afficher(self, action, argument, devant_armoire):
        murs = sum(1 for etat in self.memoire.cases.values() if etat == "mur")
        nouveau_mur = murs > self.nb_murs
        self.nb_murs = murs

        print("\033[2J\033[H", end="")            # efface l'ecran
        print(self.en_tete)
        print(f"Etape : {self.etape}\n")
        print(self.memoire.dessiner(robot=self.monde.position))
        print("\n? = jamais vu   # = mur connu   R = robot   A = armoire   D = dictionnaire   P = resident\n")
        print(f"pas {len(self.trace.pas) - 1:3d}   position {list(self.monde.position)}   "
              f"action : {action} {argument if argument is not None else ''}")
        ligne = f"selecteur {list(self.monde.selecteur)}"
        if devant_armoire:
            contenu = self.monde.contenu_courant()
            ligne += f"   casier : {contenu if contenu is not None else 'vide'}"
        print(ligne)
        print(f"objet porte : {self.objet_porte or '-'}")
        if nouveau_mur and action == "AVANCER":
            print("\n>>> mur decouvert : la carte mentale change, le chemin est recalcule")
        time.sleep(self.pause)

    def annoncer(self, texte):
        if self.pause is not None:
            print(f"\n=== {texte} ===")
            time.sleep(max(1.5, 8 * self.pause))

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
        self.en_tete = f"Demande {numero} -- {resident} : \"{demande['message']}\""

        def echec(motif):
            self.trace.ajouter_livraison(numero, resident, emotion, intensite,
                                         casier, repli, objet, False, motif)
            self.annoncer(f"demande {numero} : ECHEC ({motif})")

        # 1. Dictionnaire
        self.etape = "vers le dictionnaire"
        if not self.aller(numero, self.pos_dictionnaire):
            return echec("dictionnaire inaccessible")
        self.etape = "consultation du dictionnaire"
        self.noter(numero, "CONSULTER")
        lu = lire_emotion(demande["message"], self.dictionnaire)
        if lu is None:
            return echec("emotion indeterminee")
        emotion, intensite = lu
        self.en_tete += f"\nEmotion lue : {emotion} / {intensite}"

        # 2. Armoire : on calcule la fouille, puis on l'execute pas a pas.
        self.etape = "vers l'armoire"
        if not self.aller(numero, self.pos_armoire):
            return echec("armoire inaccessible")
        objet, casier, repli, _, actions = chercher_objet(
            emotion, intensite, self.monde.selecteur, self.armoire,
            self.vus, self.monde.contenu_casier)
        self.etape = "fouille de l'armoire"
        for action, argument in actions:
            self.noter(numero, action, argument)
            if action == "CHERCHER":
                self.monde.chercher(argument)
            elif action == "PRENDRE":
                self.monde.prendre(*self.monde.selecteur)
                self.objet_porte = argument
        if objet is None:
            return echec("armoire vide")

        # 3. Resident
        self.etape = f"vers le resident {resident} (casier {list(casier)}, repli : {repli})"
        if not self.aller(numero, self.residents[resident]):
            return echec("resident inaccessible")
        self.etape = f"remise de l'objet a {resident}"
        self.noter(numero, "DONNER", objet)
        self.objet_porte = None
        self.trace.ajouter_livraison(numero, resident, emotion, intensite,
                                     casier, repli, objet, True)
        self.annoncer(f"demande {numero} : {objet} remis a {resident}")


# ---------------------------------------------------------------------------

def main(argv):
    # Options facultatives (pour la video) : --afficher [--pause 0.15]
    args = list(argv[1:])
    pause = None
    if "--afficher" in args:
        args.remove("--afficher")
        pause = 0.15
    if "--pause" in args:
        i = args.index("--pause")
        pause = float(args[i + 1])
        del args[i:i + 2]
    if len(args) != 4:
        print("usage : python3 agent.py <carte.json> <scenario.json> "
              "<dossier_donnees> <trace.json> [--afficher] [--pause 0.15]", file=sys.stderr)
        return 1
    try:
        carte, scenario, dictionnaire, armoire = charger_tout(args[0], args[1], args[2])
    except rio.ErreurFichier as err:
        print(f"erreur : {err}", file=sys.stderr)
        return 1                                   # aucune trace ecrite

    robot = Robot(carte, scenario, dictionnaire, armoire, pause)
    for demande in scenario["demandes"]:
        robot.traiter(demande["numero"], demande)

    chemin = robot.trace.ecrire(args[3])
    resume = robot.trace.en_dictionnaire()["resume"]
    print(f"trace ecrite : {chemin} ({resume['reussies']}/{resume['demandes']} "
          f"reussies, {resume['pas_total']} pas)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))