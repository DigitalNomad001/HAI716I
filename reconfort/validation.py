"""
Validation du contenu des fichiers d'entrée

Utilisation juste après chaque chargement de fichier

"""

from reconfort.reconfort_io import ErreurFichier

# Vérifie que objet[nom] existe et a le type attendu. Renvoie la valeur si ok, lève ErreurFichier sinon
# objet (dict) : dictionnaire à vérifier (ex. la carte)
# nom (str) : nom du champ (ex. "hauteur")
# type_attendu (type) : type attendu pour le champ (ex. int, str)
# nom_fichier (str) : nom du fichier pour les messages d'erreur
def verifier_champ(objet, nom, type_attendu, nom_fichier):
    if nom not in objet:
        raise ErreurFichier(f"{nom_fichier} : champ obligatoire '{nom}' est absent")
    val = objet[nom]
    if type(val) != type_attendu:
        raise ErreurFichier(f"{nom_fichier} : champ '{nom}' doit être de type {type_attendu.__name__}, pas {type(val).__name__}")

    return val

# Vérifie qu'une position est une liste de deux entiers [ligne, colonne]. Renvoie la position si ok, lève ErreurFichier sinon
# val : valeur lue dans le fichier (ex. [2, 3])
# nom (str) : nom du champ (ex. "position")
# nom_fichier (str) : nom du fichier pour les messages d'erreur
def verifier_position(val, nom, nom_fichier):
    if type(val) != list or len(val) != 2:
        raise ErreurFichier(f"{nom_fichier} : '{nom}' doit être [ligne, colonne], pas {val}")
    for nb in val:
        if type(nb) != int:
            raise ErreurFichier(f"{nom_fichier} : '{nom}' doit être [ligne, colonne] avec des entiers, pas {val}")
    return val


# Vérifie que objet[nom] est une liste non vide de str sans doublon. Renvoie la liste de str si ok, lève ErreurFichier sinon
# objet (dict) : objet JSON à vérifier (ex. le dictionnaire)
#  nom (str) : nom du champ (ex. "emotions")
# nom_fichier (str) : nom du fichier pour les messages d'erreur
def verifier_liste_textes(objet, nom, nom_fichier):
    liste = verifier_champ(objet, nom, list, nom_fichier)
    if len(liste) == 0:
        raise ErreurFichier(f"{nom_fichier} : liste '{nom}' ne doit pas être vide")
    for elem in liste:
        if type(elem) != str:
            raise ErreurFichier(f"{nom_fichier} : liste '{nom}' doit contenir des chaînes de caractères, pas {elem}")
    if len(set(liste)) != len(liste):
        raise ErreurFichier(f"{nom_fichier} : liste '{nom}' contient un doublon")
    return liste

# Vérifie qu'une position est dans la grille et sur le bon symbole
# grille (liste de str) : grille de la carte
# position (list de 2 int) : position à vérifier [ligne, colonne]
# symbole (str) : symbole attendu à cette position
# nom_elem (str) : nom de l'élément qui est censé être à cette position pour les messages d'erreur (ex. "l'armoire", "le resident R1")
# nom_fichier (str) : nom du fichier pour les messages d'erreur
def verifier_case(grille, position, symbole, nom_elem, nom_fichier):
    ligne, colonne = position
    hauteur, largeur = len(grille), len(grille[0])
    if ligne < 0 or ligne >= hauteur or colonne < 0 or colonne >= largeur:
        raise ErreurFichier(f"{nom_fichier} : {nom_elem} en position '{position}' hors de la grille")
    if grille[ligne][colonne] != symbole:
        raise ErreurFichier(f"{nom_fichier} : {nom_elem} en position '{position}' doit être sur le symbole '{symbole}', pas '{grille[ligne][colonne]}'")

# Valide le contenu d'une carte. Lève ErreurFichier si le contenu est invalide
# carte (dict) : la carte à valider
# chemin_fichier (str ou path) : chemin du fichier pour les messages d'erreur
def valider_carte(carte, chemin_fichier):
    chemin = str(chemin_fichier)
    
    verifier_champ(carte, "nom", str, chemin)
    dimensions = verifier_champ(carte, "dimensions", dict, chemin)
    hauteur = verifier_champ(dimensions, "hauteur", int, chemin)
    largeur = verifier_champ(dimensions, "largeur", int, chemin)
    grille = verifier_champ(carte, "grille", list, chemin)
    depart = verifier_position(verifier_champ(carte, "depart_robot", list, chemin), "depart_robot", chemin)
    armoire = verifier_champ(carte, "armoire", dict, chemin)
    position_armoire = verifier_position(verifier_champ(armoire, "position", list, chemin), "armoire.position", chemin)
    dictionnaire = verifier_champ(carte, "dictionnaire", dict, chemin)
    position_dictionnaire = verifier_position(verifier_champ(dictionnaire, "position", list, chemin), "dictionnaire.position", chemin)
    residents = verifier_champ(carte, "residents", list, chemin)

    if len(grille) == 0:
        raise ErreurFichier(f"{chemin} : la grille ne doit pas être vide")
    for ligne in grille:
        if type(ligne) != str:
            raise ErreurFichier(f"{chemin} : chaque ligne de la grille doit être une chaîne de caractères, pas {ligne}")
        if len(ligne) != len(grille[0]):
            raise ErreurFichier(f"{chemin} : grille non rectangulaire)")

    if len(grille) != hauteur or len(grille[0]) != largeur:
        raise ErreurFichier(f"{chemin} : dimensions annoncées {hauteur}x{largeur} ne correspondent pas à la taille réelle de la grille {len(grille)}x{len(grille[0])}")

    verifier_case(grille, depart, "R", "le depart du robot", chemin)
    verifier_case(grille, position_armoire, "A", "l'armoire", chemin)
    verifier_case(grille, position_dictionnaire, "D", "le dictionnaire", chemin)

    identifiants = []
    for resident in residents:
        if type(resident) != dict:
            raise ErreurFichier(f"{chemin} : chaque resident doit être un dict")
        id = verifier_champ(resident, "id", str, chemin)
        verifier_champ(resident, "nom", str, chemin)
        position = verifier_position(verifier_champ(resident, "position", list, chemin), "position", chemin)
        verifier_case(grille, position, "P", f"le resident {id}", chemin)
        if id in identifiants:
            raise ErreurFichier(f"{chemin} : identifiant de resident '{id}' en double")
        identifiants.append(id)

# Valide le contenu d'un dictionnaire. Lève ErreurFichier si le contenu est invalide
# dictionnaire (dict) : le dictionnaire à valider
# chemin_fichier (str ou path) : chemin du fichier pour les messages d'erreur
def valider_dictionnaire(dictionnaire, chemin_fichier):
    chemin = str(chemin_fichier)
    
    verifier_champ(dictionnaire, "nom", str, chemin)
    emotions = verifier_liste_textes(dictionnaire, "emotions", chemin)
    intensites = verifier_liste_textes(dictionnaire, "intensites", chemin)
    entrees = verifier_champ(dictionnaire, "entrees", list, chemin)

    mots_vus = []
    for entree in entrees:
        if type(entree) != dict:
            raise ErreurFichier(f"{chemin} : chaque entree doit être un dict")
        formes = verifier_liste_textes(entree, "formes", chemin)
        emotion = verifier_champ(entree, "emotion", str, chemin)
        intensite = verifier_champ(entree, "intensite", str, chemin)

        if emotion not in emotions:
            raise ErreurFichier(f"{chemin} : emotion '{emotion}' inconnue")
        if intensite not in intensites:
            raise ErreurFichier(f"{chemin} : intensite '{intensite}' inconnue")

        for forme in formes:
            if forme in mots_vus:
                raise ErreurFichier(f"{chemin} : le mot '{forme}' en double")
            mots_vus.append(forme)

# Valide le contenu d'une armoire. Lève ErreurFichier si le contenu est invalide
# armoire (dict) : l'armoire à valider
# chemin_fichier (str ou path) : chemin du fichier pour les messages d'erreur
def valider_armoire(armoire, chemin_fichier):
    chemin = str(chemin_fichier)

    emotions = verifier_liste_textes(armoire, "emotions", chemin)
    intensites = verifier_liste_textes(armoire, "intensites", chemin)
    nb_ligne = len(intensites)
    nb_colonne = len(emotions)

    depart = verifier_position(verifier_champ(armoire, "casier_depart", list, chemin), "casier_depart", chemin)
    if not (0 <= depart[0] < nb_ligne and 0 <= depart[1] < nb_colonne):
        raise ErreurFichier(f"{chemin} : casier_depart {depart} hors de l'armoire")

    casiers_vus = []
    for casier in verifier_champ(armoire, "casiers", list, chemin):
        if type(casier) != dict:
            raise ErreurFichier(f"{chemin} : chaque casier doit être un dict")
        ligne = verifier_champ(casier, "ligne", int, chemin)
        colonne = verifier_champ(casier, "colonne", int, chemin)
        emotion = verifier_champ(casier, "emotion", str, chemin)
        intensite = verifier_champ(casier, "intensite", str, chemin)

        if "objet" not in casier:
            raise ErreurFichier(f"{chemin} : casier [{ligne}, {colonne}] n'a pas d'objet")
        if casier["objet"] is not None and type(casier["objet"]) != str:
            raise ErreurFichier(f"{chemin} : casier [{ligne}, {colonne}] : 'objet' doit être un str ou null")

        if not (0 <= ligne < nb_ligne and 0 <= colonne < nb_colonne):
            raise ErreurFichier(f"{chemin} : casier [{ligne}, {colonne}] hors de l'armoire")
        if [ligne, colonne] in casiers_vus:
            raise ErreurFichier(f"{chemin} : casier [{ligne}, {colonne}] en double")
        if emotion != emotions[colonne] or intensite != intensites[ligne]:
            raise ErreurFichier(f"{chemin} : casier [{ligne}, {colonne}] : etiquette {emotion}/{intensite} au lieu de {emotions[colonne]}/{intensites[ligne]}")

# Valide le contenu d'un scénario. Lève ErreurFichier si le contenu est invalide
# scenario (dict) : le scénario à valider
# chemin_fichier (str ou path) : chemin du fichier pour les messages d'erreur
def valider_scenario(scenario, chemin_fichier):
    chemin = str(chemin_fichier)

    verifier_champ(scenario, "nom", str, chemin)
    verifier_champ(scenario, "carte", str, chemin)
    verifier_champ(scenario, "armoire", str, chemin)
    for demande in verifier_champ(scenario, "demandes", list, chemin):
        if type(demande) != dict:
            raise ErreurFichier(f"{chemin} : chaque demande doit être un dict")
        verifier_champ(demande, "numero", int, chemin)
        verifier_champ(demande, "resident", str, chemin)
        verifier_champ(demande, "message", str, chemin)

# Vérifie que quatre fichiers vont ensemble. Lève ErreurFichier si ce n'est pas le cas.
# À appeler après avoir chargé et validé les quatre fichiers.
# carte (dict) : la carte
# scenario (dict) : le scénario
# dictionnaire (dict) : le dictionnaire
# armoire (dict) : l'armoire
def verifier_coherence(carte, scenario, dictionnaire, armoire):
    if scenario["carte"] != carte["nom"]:
        raise ErreurFichier(f"Le scénario est prévu pour la carte '{scenario['carte']}, pas pour la carte '{carte['nom']}'")

    identifiants = [resident["id"] for resident in carte["residents"]]
    for demande in scenario["demandes"]:
        if demande["resident"] not in identifiants:
            raise ErreurFichier(f"La demande {demande['numero']} vise le resident '{demande['resident']} qui est absent sur la carte")

    if sorted(dictionnaire["emotions"]) != sorted(armoire["emotions"]):
        raise ErreurFichier(f"Le dictionnaire et l'armoire n'ont pas les mêmes émotions")
    if sorted(dictionnaire["intensites"]) != sorted(armoire["intensites"]):
        raise ErreurFichier(f"Le dictionnaire et l'armoire n'ont pas les mêmes intensités")