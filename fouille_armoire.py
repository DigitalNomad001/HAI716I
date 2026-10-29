import reconfort.reconfort_io as rio

NB_COLONNES = 8
NB_LIGNES = 3

def regarder_casier(armoire, ligne, colonne):
    for casier in armoire["casiers"]:
        if casier["ligne"] == ligne and casier["colonne"] == colonne:
            return casier["objet"]
    return None

def liste_candidats(ligne, colonne):
    candidats = []
    for decalage in [-2, -1, 0, 1, 2]:
        c = (colonne + decalage) % NB_COLONNES
        for l in [0, 1, 2]:
            if decalage == 0 and l == ligne:
                repli = "aucun"
            elif decalage == 0:
                repli = "intensite"
            elif abs(decalage) == 1:
                repli = "voisine_1"
            else:
                repli = "voisine_2"

            sens = 0 if decalage >= 0 else 1
            ordre = (abs(decalage), abs(l - ligne), l, sens)
            candidats.append((ordre, l, c, repli))

    candidats.sort()
    return candidats

def aller_au_casier(selecteur, l_cible, c_cible, armoire, vus, actions):
    l, c = selecteur

    while l != l_cible:
        if l < l_cible:
            l, direction = l + 1, "S"
        else:
            l, direction = l - 1, "N"
        vus[(l, c)] = regarder_casier(armoire, l, c)
        actions.append(("CHERCHER", direction))

    while c != c_cible:
        if (c_cible - c) % NB_COLONNES <= NB_COLONNES // 2:
            c, direction = (c + 1) % NB_COLONNES, "E"
        else:
            c, direction = (c - 1) % NB_COLONNES, "O"
        vus[(l, c)] = regarder_casier(armoire, l, c)
        actions.append(("CHERCHER", direction))

    return [l, c]

def chercher_objet(emotion, intensite, selecteur, armoire, vus):
    ligne = armoire["intensites"].index(intensite)
    colonne = armoire["emotions"].index(emotion)
    actions = []

    vus[tuple(selecteur)] = regarder_casier(armoire, selecteur[0], selecteur[1])

    for ordre, l, c, repli in liste_candidats(ligne, colonne):
        if (l, c) in vus and vus[(l, c)] is None:
            continue

        selecteur = aller_au_casier(selecteur, l, c, armoire, vus, actions)
        objet = vus[(l, c)]
        if objet is not None:
            actions.append(("PRENDRE", objet))
            return objet, [l, c], repli, selecteur, actions

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