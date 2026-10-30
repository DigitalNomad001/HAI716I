import reconfort.reconfort_io as rio

NB_COLONNES = 8 # une colonne par émotion, elle boucle (1 -> 2 -> ... -> 7 -> 0 -> 1 ...)
NB_LIGNES = 3 # une ligne par intensité

# reçoit l'armoire, la ligne et la colonne, renvoie l'objet dans le casier correspondant ou None si le casier est vide
def regarder_casier(armoire, ligne, colonne):
    for casier in armoire["casiers"]:
        if casier["ligne"] == ligne and casier["colonne"] == colonne:
            return casier["objet"]
    return None

# reçoit la ligne et la colonne, renvoie la liste des candidats dans l'ordre de priorité
# ligne et collonne : le casier cible (intensité  et émotion lues)
def liste_candidats(ligne, colonne):
    candidats = []

    # On regarde 5 colonnes : l'émotion visée (décalage 0) et ses voisines
    # négatif = sens antihaoraire
    for decalage in [-2, -1, 0, 1, 2]:
        c = (colonne + decalage) % NB_COLONNES
        for l in [0, 1, 2]:
            if decalage == 0 and l == ligne:
                repli = "aucun"             # le casier exactement visé
            elif decalage == 0:
                repli = "intensite"         # bonne émotion mais d'une intensité différente
            elif abs(decalage) == 1:
                repli = "voisine_1"         # émotion voisine
            else:
                repli = "voisine_2"         # émotion à 2 crans

            sens = 0 if decalage >= 0 else 1
            ordre = (abs(decalage), abs(l - ligne), l, sens)
            candidats.append((ordre, l, c, repli))

    candidats.sort()
    return candidats

# reçoit le selecteur, la ligne cible et la colonne cible, l'armoire, les objets vus et les actions, renvoie la nouvelle position du selecteur
# À chaque case traversée, on regarde le casier et note dans "vus"
# Chque déplacement est ajouté à "actions" pour la trace
def aller_au_casier(selecteur, l_cible, c_cible, armoire, vus, actions):
    l, c = selecteur

    # On de déplace sur la bonne ligne
    while l != l_cible:
        if l < l_cible:
            l, direction = l + 1, "S"
        else:
            l, direction = l - 1, "N"
        vus[(l, c)] = regarder_casier(armoire, l, c)
        actions.append(("CHERCHER", direction))

    # On se déplace sur la bonne colonne
    # On choisit le sens le plus court car les colonnes bouclent
    while c != c_cible:
        if (c_cible - c) % NB_COLONNES <= NB_COLONNES // 2:
            c, direction = (c + 1) % NB_COLONNES, "E"
        else:
            c, direction = (c - 1) % NB_COLONNES, "O"
        vus[(l, c)] = regarder_casier(armoire, l, c)
        actions.append(("CHERCHER", direction))

    return [l, c]

# reçoit l'émotion, l'intensité, le selecteur, l'armoire et les objets vus
# renvoie l'objet trouvé (ou None), le casier correspondant, le type de repli, le nouveau selecteur et la liste des actions effectuées
def chercher_objet(emotion, intensite, selecteur, armoire, vus):
    ligne = armoire["intensites"].index(intensite)
    colonne = armoire["emotions"].index(emotion)
    actions = []

    # on voit le casier devant lequel on se trouve avant de se déplacer
    vus[tuple(selecteur)] = regarder_casier(armoire, selecteur[0], selecteur[1])

    # on essaie les 15 candidats dans l'ordre de priorité
    for ordre, l, c, repli in liste_candidats(ligne, colonne):
        # si on sait que le casier est vide (on l'a vu pendant cette demande ou une précédente), on ne va pas le regarder
        if (l, c) in vus and vus[(l, c)] is None:
            continue

        selecteur = aller_au_casier(selecteur, l, c, armoire, vus, actions)
        # on regarde le casier, si on y trouve un objet, on le prend et on arrête la recherche
        objet = vus[(l, c)]
        if objet is not None:
            actions.append(("PRENDRE", objet))
            return objet, [l, c], repli, selecteur, actions

        # si le casier est vide, on continue la recherche

    # les 15 candidats vides : echec avec motif "armoire vide"
    return None, None, None, selecteur, actions


# Test avec un exemple

armoire = rio.charger_armoire("donnees/armoire_standard.json")
selecteur = armoire["casier_depart"]
vus = {}

demandes = [("tristesse", "moyenne"), ("surprise", "forte"), ("anticipation", "forte")]

for emotion, intensite in demandes:
    print("Demande : ", emotion, intensite, "- selecteur en ", selecteur)
    objet, casier, repli, selecteur, actions = chercher_objet(emotion, intensite, selecteur, armoire, vus)

    for action, arg in actions:
        print("  ", action, arg)
    if objet is None:
        print("  -> armoire vide")
    else:
        print("  ->", objet, " dans le casier ", casier, "- repli : ", repli)
    print()