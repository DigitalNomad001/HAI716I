from collections import deque
from typing import Dict,Tuple,Callable,Optional,Iterable

Case=Tuple[int,int]

Directions:Dict[str,Case]={
    "N":(-1,0),
    "S":(1,0),
    "E":(0,1),
    "O":(0,-1)}

#on retourne l'ensemble de coordonnées des voisins, case ici est la coordonnée actuelle de robot 
def voisins(case:Case) -> List[Tuple[str, Case]]:
    ligne,colonne=case
    return [(sens,(ligne+x,colonne+y)) for sens,(x,y) in Directions.items()]


#on peut retourner le sens vers l'une de direction de voisins avec une destination donnée
def direction_vers(depart:Case,destination:Case):
    x_decalage=destination[0]-depart[0]
    y_decalge=destination[1]-depart[1]
    decalage=(x_decalage,y_decalge)

    for direction,coordonnee in Directions.items():
        if decalage==coordonnee:
            return direction
    raise ValueError(f"{depart} et {destination} ne sont pas des voisins")

# maintenant on essaie de construire la BFS

def plus_court_chemin(depart:Case,arrive:Iterable[Case],est_traversable:Callable[[Case],bool])-> Optional[list[Case]]:
    arrive=set(arrive)
    if depart in arrive:
        return [depart]
    if not arrive:
        return None

    predecesseur:Dict[Case,Optional[Case]]={depart:None}
    file=deque([depart])

    while file:
        courant=file.popleft()
        for _,voisin in voisins(courant):
            if  voisin in predecesseur:
                continue
            if not est_traversable(voisin):
                continue
            predecesseur[voisin]=courant
            if voisin in arrive:
                return reconstuire(predecesseur,voisin)
            file.append(voisin)
    return None


#on reconstruire un chemin de bas à bas 
def reconstuire(pred:Dict[Case,Optional[Case]],voisin:Case)-> Optional[list[Case]]:
    chemin=[voisin] #chemin est une list
    while pred[chemin[-1]] is not None:
        chemin.append(pred[chemin[-1]])
    chemin.reverse()
    return chemin



    

