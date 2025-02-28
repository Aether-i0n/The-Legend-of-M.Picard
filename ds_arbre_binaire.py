class Noeud:
    def __init__(self, etiquette, gauche, droit):
        self.etiquette = etiquette
        self.gauche = gauche
        self.droit = droit

def creer_vide(): return None
def est_vide(a): return a is None
def etiquette(a): return a.etiquette
def etiquette_str(a): return "•" if est_vide(a) else str(etiquette(a))
def gauche(a): return a.gauche
def droit(a): return a.droit
def Arbre(e, a1, a2): return Noeud(e, a1, a2)

#Ajout de fonction fait en TP

def nb_niveaux(a):
    """ Noeud -> int
    Renvoie le nombre de niveaux de l'arbre """
    if est_vide(a):
        return 0
    else:
        return 1 + max(nb_niveaux(gauche(a)), nb_niveaux(droit(a)))
    
#Ajout d'une fonction (j'ai pas retrouvé celle faite en TP)

def afficher_arbre(a, decalement=0):
    if est_vide(a):
        return
    print("---"*(decalement-1),end="")
    print("-- "+etiquette_str(a))
    afficher_arbre(gauche(a),decalement+1)
    afficher_arbre(droit(a),decalement+1)

def recupérer_niveau(a, niveau):
    """ Noeud -> [int]
    Renvoie tous les noeux à un certain `niveau`"""
    if est_vide(a):
        return []
    elif niveau==1: #car le niveau commence à 1 (la profondeur à 0)
        return [etiquette(a)]
    return recupérer_niveau(gauche(a), niveau-1) + recupérer_niveau(droit(a), niveau-1)

def récuperer_toute_les_valeurs(a):
    """ Noeud -> [int]
    Renvoie tous les noeux"""
    if est_vide(a):
        return []
    return [etiquette(a)] + récuperer_toute_les_valeurs(gauche(a)) + récuperer_toute_les_valeurs(droit(a))

def recupérer_niveau_tuple(a, niveau):
    l = recupérer_niveau(a, niveau)
    r = []
    for i in range(0,len(l),2):
        r.append((l[i],l[i+1]))
    return r

import random

def inverser_arbre(a):
    if est_vide(gauche(a)):
        return
    g = gauche(a)
    d = droit(a)
    if random.randint(0,1)==1:
        a.gauche = d
        a.droit = g
    inverser_arbre(gauche(a))
    inverser_arbre(droit(a))

def liste_possibilité(a):
    if est_vide(a):
        return []
    l = liste_possibilité(gauche(a)) + liste_possibilité(droit(a)) + [etiquette(a)]
    if etiquette(a) in [71, 72]:
        l += liste_possibilité(gauche(a.teleport)) + liste_possibilité(droit(a.teleport))
    return l
