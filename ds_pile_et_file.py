class Maillon:
    def __init__(self, v, n):
        self.valeur = v
        self.suivant = n
    
    def __repr__(self):
        """ Maillon -> str
        Construit la chaîne de caractère représentant le Maillon `self`. """

        return f"-{self.valeur}-"

class Pile:
    """Une pile d'entiers"""
    def __init__(self):
        """ Pile -> Nonetype """
        self.sommet = None

    def est_vide(self):
        """ Pile -> bool
        Détermine si la pile est vide """
        return self.sommet is None
#         if self.sommet == None:
#             return True
#         return False
    
    def empiler(self, v):
        """ Pile, int -> None
        Empile la valeur v au sommet de la pile self """
        m = Maillon(v, self.sommet)
        self.sommet = m
    
    def depiler(self):
        """ Pile -> int
        Renvoie l'élément présent au sommet de la pile self, en le supprimant de la pile """
        if self.est_vide():
            # gérer l'erreur
            raise AttributeError("Impossible de dépiler : la pile est vide)")
        v = self.sommet.valeur
        self.sommet = self.sommet.suivant
        return v
    
    def __str__(self):
        """ Pile -> str
        Construit la chaîne de caractère représentant la pile self """
        # avec une boucle while et un maillon courant
        ch = '[Sommet] '
        maillon_courant = self.sommet
        while maillon_courant is not None:
            ch = ch + ' ' + str(maillon_courant.valeur) 
            maillon_courant = maillon_courant.suivant
        return ch   

class File:
    """Une file d'entiers"""
    def __init__(self):
        """File -> Nonetype"""
        self.debut = None
        self.fin = None

    def est_vide(self):
        """ File -> bool
        Détermine si la file self est vide """
        return self.debut is None and self.fin is None
#         if self.debut == None and self.fin == None :
#             return True
#         return False
    
    def enfiler(self, v):
        """ File, int -> None
        Ajoute l'élément v à la file self """
        if self.est_vide() :
            m = Maillon(v,None)
            self.debut = m
            self.fin = m
        else:
            m = Maillon(v,None)
            self.fin.suivant = m
            self.fin = m 
    
    def defiler(self):
        """ File -> int
        Renvoie le premier élément de la file en le supprimant de celle-ci """
        if self.est_vide():
            # gérer l'erreur
            raise AttributeError("Impossible de défiler : la file est vide)")
        else:
            b = self.debut.valeur
            self.debut = self.debut.suivant
            if self.debut is None:
                self.fin = None
            return b
    
    def longueur(self):
        """ File -> int
        Renvoie la longueur de la File `self`. """

        longueur = 0
        maillon_courant = self.debut
        while maillon_courant is not None:
            longueur += 1
            maillon_courant = maillon_courant.suivant
        return longueur
    
    def tete(self):
        """ File -> int
        Renvoie la valeur du premier élément de la File `self` sans la modifier. """

        if self.est_vide():
            raise AttributeError("Impossible de récupérer la tête : la file est vide")
        return self.debut.valeur

    def __str__(self):
        """ self -> str
        Construit la chaîne de caractères représentant la file self """
        ch = '[Debut] '
        maillon_courant = self.debut
        while maillon_courant is not None:
            ch = ch + ' ' + str(maillon_courant.valeur) 
            maillon_courant = maillon_courant.suivant
        return ch + '  [fin]'

class PileBornee:
    def __init__(self, maxi):
        self.pile = Pile()
        self.capacite = maxi
        self.taille = 0
        
    def est_vide(self):
        return self.pile.est_vide()
        
    def est_pleine(self):
        """ PileBornee -> bool """
        return self.capacite == self.taille
    
    def empiler(self, v):
        """ PileBornee, int -> bool """
        if self.est_pleine():
            raise IndexError('la pile est pleine')
        else:
            self.pile.empiler(v)
            self.taille += 1
    
    def depiler(self):
        """ PileBornee -> int """
        if self.est_vide():
            raise IndexError('On ne peut pas depiler')
        else:
            # valeur = self.pile.sommet.valeur
            self.taille -= 1
            return self.pile.depiler()
    
    def __str__(self):
        return self.pile.__str__()