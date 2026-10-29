import reconfort.reconfort_io as rio

def lire_emotion(message, dictionnaire):
    mots = rio.normaliser(message)
    print("mots normalises :", mots)
    for mot in mots:
        for entree in dictionnaire["entrees"]:
            if mot in entree["formes"]:
                return entree["emotion"], entree["intensite"]
    return None


# Test avec un exemple

dictionnaire = rio.charger_dictionnaire("donnees/dictionnaire.json")

messages = ["Je me sens tellement seule ce soir, personne n'est passé.",
            "Je suis un peu inquiet, j'entends du bruit dans le couloir.",
            "Ce bouton est cassé, ça m'agace depuis hier.",
            "Ma fille a appelé, je suis vraiment heureux."]

for message in messages:
    res = lire_emotion(message, dictionnaire)
    if res is None:
        print(message, "-> emotion indeterminee")
    else:
        emotion, intensite = res
        print(message, "->", emotion, intensite)