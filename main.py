import pygame, sqlite3, math, random, time, os, sys, json
from ds_pile_et_file import *
from ds_arbre_binaire import *

def fenêtre_fermée(événement: pygame.event.Event):
    """ Event -> bool
    Détermine si l'utilisateur a tenté de fermer la fenêtre. """

    return événement.type == pygame.QUIT

def souris_est_pressée(événement: pygame.event.Event):
    """ Event -> bool
    Détermine si l'utilisateur a pressé le clic gauche de sa souris. """

    return événement.type == pygame.MOUSEBUTTONDOWN and événement.button == 1

def souris_est_relachée(événement: pygame.event.Event):
    """ Event -> bool
    Détermine si l'utilisateur a relaché le clic gauche de sa souris. """

    return événement.type == pygame.MOUSEBUTTONUP and événement.button == 1

def souris_déplacée(événement: pygame.event.Event):
    """ Event -> bool
    Détermine si l'utilisateur a déplacé sa souris. """

    return événement.type == pygame.MOUSEMOTION

def touche_pressée(événement: pygame.event.Event, touches: list[int]):
    """ Event, [int] -> bool
    Détermine si l'utilisateur a pressé la `touche` donnée. """

    return événement.type == pygame.KEYDOWN and événement.key in touches

def quitter():
    """ () -> None
    Quitte le jeu sans faire d'erreur. """

    pygame.quit()
    sys.exit()

def taille_écran(rapport: float):
    """ float -> (int, int)
    Renvoie la taille de l'écran en fonction du `rapport` donné.
    Le rapport est un coefficient qui multiplie la vraie taille de l'écran.
    On admet que info.current_w ≥ info.current_h. """

    info = pygame.display.Info()
    return int(info.current_w * rapport), int(info.current_h * rapport)

def coordonnées_réelles(x: int, y: int, produit: float = 1.):
    """ int, int -> (int, int)
    Renvoie les coordonnées réelles de la fenêtre en fonction des coordonnées d'affichage.
    Le `produit` est un paramètre optionnel qui multiplie la taille de la zone visible.
    Par exemple, un `produit` de 1,5 augmentera de 50% la zone prise en compte. """

    return ((x - (taille_fenêtre / 2)) / (caméra.zoom / produit) + caméra.x,
            (y - (taille_fenêtre / 2)) / (caméra.zoom / produit) + caméra.y)

def est_visible(rectangle: pygame.Rect, produit: float = 1.):
    """ Rect -> bool
    Détermine si le `rectangle` est visible, au moins en un point, sur l'écran.
    Le `produit` est un paramètre optionnel qui multiplie la taille de la zone visible.
    Par exemple, un `produit` de 1,5 augmentera de 50% la zone prise en compte. """

    gauche, haut = coordonnées_réelles(0, 0, produit=produit)
    taille = taille_fenêtre / caméra.zoom * produit

    fenêtre_visible = pygame.Rect(gauche, haut, taille, taille + taille_case)

    return fenêtre_visible.colliderect(rectangle)

def afficher(source: pygame.Surface, dest: tuple[int, int]):
    """ Surface, (int, int) -> None
    Affiche la `source` en `dest` sur la fenêtre en prenant en compte la marge. """

    dest_x, dest_y = dest
    dest_x += marge
    
    fenêtre.blit(source, (dest_x, dest_y))

def coordonnées_en_jeu(x: float, y: float):
    """ (float, float) -> (float, float)
    Renvoie les coordonnées prenant en compte la caméra. """

    x -= caméra.x
    y -= caméra.y

    x *= caméra.zoom
    y *= caméra.zoom

    x += taille_fenêtre // 2
    y += taille_fenêtre // 2

    return x, y

def afficher_en_jeu(source: pygame.Surface, dest: tuple[float, float]):
    """ Surface, (float, float) -> None
    Affiche la `source` en `dest` sur la fenêtre en prenant en compte la caméra. """

    dest_x, dest_y = dest

    dest_x, dest_y = coordonnées_en_jeu(dest_x, dest_y)

    afficher(pygame.transform.scale(source, (math.ceil(source.get_width() * caméra.zoom) + 1, math.ceil(source.get_height() * caméra.zoom) + 1)), (math.ceil(dest_x), math.ceil(dest_y)))

def exécuter_sql(commande: str):
    """ str -> [(Any, Any, Any, ...)]
    Exécute la `commande` sql et renvoie son contenu représenté par une liste de tuples d'un nombre indeterminé d'élément (selon la commande). """

    global curseur
    résultat = curseur.execute(commande)
    return résultat.fetchall()

def compression(élément: int, mini: int, maxi: int):
    """ int, int, int -> int
    Compresse l'`élément` pour qu'il tienne entre `mini` et `maxi`. """

    return max(min(élément, maxi), mini)

def flou_gaussien(surface: pygame.Surface, puissance: float):
    """ Surface, float -> Surface
    Renvoie une copie plus ou moins floutée de la `surface` donnée selon la `puissance` donnée.
    Fonction trouvée sur Stack Overflow à https://stackoverflow.com/questions/30723253/blurring-in-pygame puis adaptée pour le programme. """

    largeur = surface.get_width()
    hauteur = surface.get_height()

    surface_floutée = pygame.transform.smoothscale(surface, (largeur // puissance, hauteur // puissance))
    surface_floutée = pygame.transform.smoothscale(surface_floutée, (largeur, hauteur))

    return surface_floutée

def flouter(puissance: float):
    """ float -> None
    Applique un effet de flou à la fenêtre globale selon la `puissance` donnée. """

    fenêtre_floutée = flou_gaussien(fenêtre, puissance)
    fenêtre.blit(fenêtre_floutée, (0, 0))

def initialiser_QCM(dico: dict):
    """ {str: Any} -> None
    Initialiser le type QCM """

    resultat = object.__new__(QCM)
    resultat.args = dico
    return resultat

def distance(coordonnées_a: tuple[int, int], coordonnées_b: tuple[int, int]):
    """ (int, int), (int, int) -> float
    Renvoie la distance qui sépare les points de coordonnées `coordonnées_a` et de coordonnées `coordonnées_b`. """

    return math.hypot(abs(coordonnées_b[0] - coordonnées_a[0]), abs(coordonnées_b[1] - coordonnées_a[1]))

def debug_class(cls):
    """https://stackoverflow.com/questions/9058305/getting-attributes-of-a-class
    Sert pour le debugage. """

    return [i for i in cls.__dict__.keys() if i[:1] != '_']

def charger_image(chemin: str, largeur: float = None, hauteur: float = None, changement_taille: bool = True, chemin_secours=None):
    """ str, float, float, bool -> Surface
    Renvoie une image selon le `chemin` donné. """

    if not changement_taille:
        return pygame.image.load(f"Ressources/Images/{chemin}.png")

    if largeur is None:
        largeur = taille_case

    if hauteur is None:
        hauteur = taille_case

    if chemin_secours is not None:
        try :
            return pygame.transform.scale(pygame.image.load(f"Ressources/Images/{chemin}.png"), (largeur, hauteur))
        except FileNotFoundError:
            return pygame.transform.scale(pygame.image.load(f"Ressources/Images/{chemin_secours}.png"), (largeur, hauteur))
    return pygame.transform.scale(pygame.image.load(f"Ressources/Images/{chemin}.png"), (largeur, hauteur))

def ajouter_cadre(image: pygame.Surface = None):
    """ Surface -> Surface
    Ajoute un cadre derrière l'`image` donnée. """

    contour = pygame.Surface((int(2*taille_fenêtre / 25 + taille_fenêtre // 60), int(2*taille_fenêtre / 25 + taille_fenêtre // 60)))
    contour.fill((255, 255, 255))

    fond = pygame.Surface((int(2*taille_fenêtre / 25), int(2*taille_fenêtre / 25)))
    fond.fill((127, 127, 127))

    contour.blit(fond, (taille_fenêtre // 120, taille_fenêtre // 120))

    if image is not None:
        rectangle = image.get_rect(center=(contour.get_rect().center))

        contour.blit(image, rectangle.topleft)

    return contour

def afficher_curseur_souris():
    """ () -> None
    Affiche le curseur de la souris. """

    fenêtre.blit(surface_curseur_souris, surface_curseur_souris.get_rect(center=position_souris))

def texte_traduit(texte: str):
    """ str -> str
    Renvoie le `texte` donné traduit à partir de la classe Langue.
    Le texte à ne pas traduire est entre `§`. """

    texte_final = ""

    parties = texte.split("§")
    à_traduire = True

    for partie in parties:
        if à_traduire:
            texte_final += Langue(partie).valeur
        else:
            texte_final += partie
        
        à_traduire = not à_traduire

    return texte_final

def récupérer_dialogue(nom: str):
    """ str -> str
    Renvoie un dialogue aléatoire parmi ceux du PNJ de `nom` donné. """

    with open("Ressources/Données Textuel/Listes Dialogues.json", 'r', encoding='utf-8') as fichier:
        donnée: dict[str, list[str]] = json.load(fichier)

    dialogues = donnée[nom]
    return random.choice(dialogues).replace('«', '"').replace('»', '"')

def taille_arme(nom: str):
    """ str -> (float, float, float, float)
    Renvoie la taille de l'arme de `nom` donné ainsi que de son centre. """

    centre: tuple[int, int] = exécuter_sql(f"""SELECT centre_x, centre_y FROM Arme WHERE nom = '{nom}';""")[0]
    centre_x, centre_y = centre
    coordonnées: list[tuple[int, int]] = exécuter_sql(f"""SELECT x, y FROM CasesViseesArme WHERE arme = '{nom}';""")

    xs = [centre_x]
    ys = [centre_y]

    for x, y in coordonnées:
        xs.append(x)
        ys.append(y)
    
    min_x = min(xs)
    max_x = max(xs) + 1

    max_y = max(ys) + 1
    min_y = min(ys)

    largeur = max_x - min_x
    hauteur = max_y - min_y

    nouveau_centre_x = largeur - (centre_x - min_x) - 1/2
    nouveau_centre_y = hauteur - (centre_y - min_y) - 1/2

    return largeur * taille_case, hauteur * taille_case, nouveau_centre_x * taille_case, nouveau_centre_y * taille_case

def intéraction(attaques: list[str], défenses: list[str]):
    """ [str], [str], -> float
    Renvoie la valeur de l'intéraction entre les mondes d'`attaque` et les mondes de `défense`. """

    valeur = 1.

    for attaque in attaques:
        for défense in défenses:
            sql = exécuter_sql(f"""SELECT valeur FROM Interaction WHERE depart = '{attaque}' AND arrivee = '{défense}';""")
            if len(sql):
                valeur *= float(sql[0][0])

    return valeur

def jouer_musique(nom: str = None, volume: float = 1.0):
    """ str, float -> None
    Joue la musique de `nom` donné avec le `volume` donné.
    Si c'est None, continue la même musique. """

    global musique

    if nom == "":
        pygame.mixer.music.pause()

        musique = ""

        return

    pygame.mixer.music.set_volume(volume * liste_paramètres.recupérer_paramètre("audio_musique") * liste_paramètres.recupérer_paramètre("audio_global") / 10000)

    if nom is not None and nom != musique:
        pygame.mixer.music.load(f"Ressources/Audio/Musiques/{nom}.mp3")
        pygame.mixer.music.play(-1)

        musique = nom

def jouer_son(nom: str):
    """ str -> None
    Joue le son de `nom` donné. """

    global sons, volumes

    sons[nom].set_volume(volumes[nom] * liste_paramètres.recupérer_paramètre("audio_son") * liste_paramètres.recupérer_paramètre("audio_global") / 10000)
    sons[nom].play()

def copier_class(obj):

    retour = object.__new__(type(obj))
    for k,v in obj.__dict__.items():
        setattr(retour, k, v)
    return retour

class Bouton:
    """ Représente un Bouton """

    def __init__(self, style: str, text: str, image: pygame.Surface = None, color: tuple[int, int, int] = (255, 255, 255), background: tuple[int, int, int, int] = None, superposition: bool = True, animation: float = 0., fond_sélection: tuple[int, int, int, int] = None, durées_états: list[float] = [0., float("inf")], en_pause: bool = False, défilement: bool = False, largeur: int = None, hauteur: int = None, alignement_x: str = "milieu", alignement_y: str = "milieu", **coordonnées: tuple[int, int]):
        """ Bouton, str, str, Surface, (int, int, int), (int, int, int, int), bool, float, (int, int, int, int), [float], bool, bool, int, int, str, str, (int, int) -> None
        Les types et nom des paramètres ont été copiés depuis les fichiers du module pygame.
        Le dernier paramètre nécessite le nom d'un endroit puis des coordonnées.
        Exemples : center=(self.fenêtre_x//2, self.fenêtre_y//2)
                   topleft=(0, 0)
                   ... """

        self.style = style

        self.texte_original = text
        traduction = texte_traduit(self.texte_original)
        self.texte = self.découper(traduction)

        self.image = image

        self.couleur = color
        self.fond = background

        self.largeur = largeur
        self.hauteur = hauteur

        self.alignement_x = alignement_x
        self.alignement_y = alignement_y

        self.coordonnées = coordonnées

        self.surface = self.définir_surface(self.texte, self.image, self.couleur, self.fond, self.largeur, self.hauteur, self.alignement_x, self.alignement_y)
        self.rectangle = self.définir_rectangle(**coordonnées)

        self.superposition = superposition
        self.animation = animation

        self.fond_sélection = fond_sélection
        if self.fond_sélection is not None:
            self.surface_sélection = self.définir_surface(self.texte, self.image, self.couleur, self.fond_sélection, self.largeur, self.hauteur, self.alignement_x, self.alignement_y)
        
        self.état = 0
        self.en_pause = en_pause
        self.début = chronomètre.temps_écoulé(en_pause=self.en_pause)
        self.durées_états = durées_états

        self.défilement = défilement

        while len(self.durées_états) < 4: # apparition + en marche + disparition + disparu
            self.durées_états.append(float("inf"))

    def découper(self, texte: str):
        """ Bouton, str -> str
        Découpe le `texte` donné en plusieurs lignes pour qu'il ne sorte pas de la fenêtre.
        Le caractère ` ~ ` force un retour à la ligne. """

        mots = texte.split()
        
        if mots == []:
            return ""
        
        mot = mots[0]

        surface = polices_écritures[self.style].render(mot, True, (0, 0, 0))
        largeur_mot = surface.get_width()
        
        lignes = [mot]
        largeur_ligne = largeur_mot

        espace = polices_écritures[self.style].render(" ", True, (0, 0, 0)).get_width()

        for mot in mots[1:]:
            if mot == "~":
                lignes.append("")
                largeur_ligne = 0
                continue

            surface = polices_écritures[self.style].render(mot, True, (0, 0, 0))
            largeur_mot = surface.get_width()

            if largeur_ligne + 2*espace + largeur_mot >= taille_fenêtre:
                lignes.append(mot)
                largeur_ligne = largeur_mot
            
            else:
                lignes[-1] += " " + mot
                largeur_ligne += espace + largeur_mot

        return "\n".join(lignes)

    def définir_surface(self, text: str, image: pygame.Surface = None, color: tuple[int, int, int] = (255, 255, 255), background: tuple[int, int, int, int] = None, largeur: int = None, hauteur: int = None, alignement_x: str = "milieu", alignement_y: str = "milieu"):
        """ Bouton, str, Surface, (int, int, int), (int, int, int, int), int, int, str, str -> Surface
        Renvoie une surface créée selon le texte `text`, la couleur `color` et le fond `background` donnés. """

        if image is not None:
            largeur = largeur if largeur is not None else image.get_width()
            hauteur = hauteur if hauteur is not None else image.get_height()
            surface = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
            surface.blit(image, ((largeur - image.get_width()) // 2, (hauteur - image.get_height()) // 2))
        else:
            lignes = text.split("\n")
            surfaces = [polices_écritures[self.style].render(ligne, True, color) for ligne in lignes]
            largeur_texte = max(surface.get_width() for surface in surfaces)
            hauteur_texte = sum(surface.get_height() for surface in surfaces)

            largeur = largeur if largeur is not None else largeur_texte
            hauteur = hauteur if hauteur is not None else hauteur_texte

            surface = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)

            if alignement_y == "haut":
                y = 0
            elif alignement_y == "milieu":
                y = (hauteur - hauteur_texte) // 2
            elif alignement_y == "bas":
                y = hauteur - hauteur_texte

            for ligne_surface in surfaces:
                if alignement_x == "gauche":
                    x = Disposition.décalage_bouton()
                elif alignement_x == "milieu":
                    x = (largeur - ligne_surface.get_width()) // 2
                elif alignement_x == "droite":
                    x = largeur - ligne_surface.get_width()
                
                surface.blit(ligne_surface, (x, y))
                y += ligne_surface.get_height()

        if background is not None:
            fond = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            fond.fill(background)
            fond.blit(surface, (0, 0))
            return fond

        return surface

    def définir_rectangle(self, **coordonnées: tuple[int, int]):
        """ Bouton, (int, int) -> Rect
        Renvoie un rectangle créé selon les `coordonnées` données. """

        x, y = list(coordonnées.values())[0]
        return self.surface.get_rect(**{list(coordonnées.keys())[0]: (x, y)})

    def afficher(self, sélectionné: bool = False, superposition_forcée: bool = False):
        """ Bouton, bool, bool -> None
        Affiche le Bouton sur la fenêtre. """

        self.modifier_état()

        transparence = self.transparence()

        x, y = self.rectangle.topleft
        if self.défilement:
            y += défilement
        y += self.animation_vague()

        if self.fond_sélection is not None and sélectionné:
            surface = self.surface_sélection.copy()
        else:
            surface = self.surface.copy()

        surface.set_alpha(transparence)
        afficher(surface, (x, y))
        
        if self.superposition and (self.bouton_touché() or superposition_forcée):
            self.afficher_superposition()

    def modifier_état(self):
        """ Bouton -> None
        Modifie l'état du Bouton. """
        
        if chronomètre.temps_écoulé(en_pause=self.en_pause) - self.début >= self.durées_états[self.état]:
            self.état += 1
            self.début = chronomètre.temps_écoulé(en_pause=self.en_pause)

    def transparence(self):
        """ Bouton -> int
        Renvoie la transparence du Bouton. """

        if self.état == 0: # apparition
            return int(255 * (chronomètre.temps_écoulé(en_pause=self.en_pause) - self.début) / self.durées_états[self.état])
        
        if self.état == 1:
            return 255 # en marche
        
        if self.état == 2:
            return int(255 - 255 * (chronomètre.temps_écoulé(en_pause=self.en_pause) - self.début) / self.durées_états[self.état]) # disparition
        
        return 0 # disparu

    def animation_vague(self):
        """ Botuton -> int
        Renvoie la différence de hauteur que doit avoir le Bouton pour l'animation de vague. """

        return int(self.animation * math.sin(chronomètre.temps_écoulé(en_pause=self.en_pause)) * taille_fenêtre/100)

    def afficher_superposition(self):
        """ Bouton -> None
        Affiche la superposition du Bouton sur la fenêtre. """

        transparence = self.transparence()

        x, y = self.rectangle.topleft
        if self.défilement:
            y += défilement

        superposition = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
        superposition.fill((255, 255, 255, 96))

        superposition.set_alpha(transparence)

        afficher(superposition, (x, y))

    def bouton_touché(self):
        """ Bouton -> bool
        Détermine si le Bouton `self` est en contact avec la souris de position de la souris. """

        souris_x, souris_y = position_souris
        souris_x -= marge
        if self.défilement:
            souris_y -= défilement

        return self.rectangle.collidepoint((souris_x, souris_y))
    
    def modifier_texte(self, texte: str):
        """ Bouton, str -> None
        Modifie le texte du Bouton `self` par un un nouveau `texte` donné. """

        traduction = texte_traduit(texte)
        self.texte = self.découper(traduction)

        self.surface = self.définir_surface(self.texte, self.image, self.couleur, self.fond, self.largeur, self.hauteur, self.alignement_x, self.alignement_y)
        self.rectangle = self.définir_rectangle(**self.coordonnées)

        if self.fond_sélection is not None:
            self.surface_sélection = self.définir_surface(self.texte, self.image, self.couleur, self.fond_sélection, self.largeur, self.hauteur, self.alignement_x, self.alignement_y)
    
    def mise_à_jour_interface(self):
        """ Bouton -> None
        Mets à jour le Bouton `self` tel sorte que les différentes surfaces correspondes au changement de coordonnées 
        `/!\\` à utlisé après le changement de `coordonées`"""

        self.surface = self.définir_surface(self.texte, self.image, self.couleur, self.fond, self.largeur, self.hauteur, self.alignement_x, self.alignement_y)
        self.rectangle = self.définir_rectangle(**self.coordonnées)

        self.fond_sélection = self.fond_sélection
        if self.fond_sélection is not None:
            self.surface_sélection = self.définir_surface(self.texte, self.image, self.couleur, self.fond_sélection, self.largeur, self.hauteur, self.alignement_x, self.alignement_y)

    def changer_langue(self):
        """ Bouton -> None
        Modifie le texte en fonction de la langue sélectionnée. """

        self.modifier_texte(self.texte_original)

class Jeu:
    """ Gère tout le jeu """

    def __init__(self):
        """ Jeu -> None """

        self.initialiser_sql()
        self.exécuter_fichier_sql()

        global liste_paramètres
        liste_paramètres = Données_Paramètres()

        self.initialiser_pygame()

        global position_souris
        position_souris = pygame.mouse.get_pos()

        global polices_écritures
        chemin_police_écriture = "Ressources/Polices d'écriture/DungeonFont.pfb"

        polices_écritures = {
            "Titre": pygame.font.Font(chemin_police_écriture, int(taille_fenêtre / 7.5)),
            "Gros": pygame.font.Font(chemin_police_écriture, int(taille_fenêtre / 10)),
            "Moyen": pygame.font.Font(chemin_police_écriture, int(taille_fenêtre / 20)),
            "Mini": pygame.font.Font(chemin_police_écriture, int(taille_fenêtre / 30))
        }

        global taille_pixel
        taille_pixel = taille_fenêtre / (16 * 15)

        global taille_case
        taille_case = taille_pixel * 16

        self.bordure = pygame.Surface((marge, taille_fenêtre))

        global musique
        musique = ""

        global sons
        sons = dict[str, pygame.mixer.Sound]({
            "Clique": pygame.mixer.Sound("Ressources/Audio/Sons/Clique.wav"),
            "Défiler": pygame.mixer.Sound("Ressources/Audio/Sons/Défiler.wav"),
            "Dégât": pygame.mixer.Sound("Ressources/Audio/Sons/Dégât.wav"),
            "Mort": pygame.mixer.Sound("Ressources/Audio/Sons/Mort.wav"),
            "Ouvrir": pygame.mixer.Sound("Ressources/Audio/Sons/Ouvrir.wav"),
            "Sélection": pygame.mixer.Sound("Ressources/Audio/Sons/Sélection.wav"),
            "Retour": pygame.mixer.Sound("Ressources/Audio/Sons/Retour.wav"),
            "Destruction": pygame.mixer.Sound("Ressources/Audio/Sons/Destruction.wav"),
            "Attaque": pygame.mixer.Sound("Ressources/Audio/Sons/Attaque.wav"),
            "Effet": pygame.mixer.Sound("Ressources/Audio/Sons/Effet.wav"),
            "Totem": pygame.mixer.Sound("Ressources/Audio/Sons/Totem.wav")
        })

        global volumes
        volumes = dict[str, float]({
            "Clique": .75,
            "Défiler": 1.,
            "Dégât": .5,
            "Mort": 1.,
            "Ouvrir": 1.,
            "Sélection": .5,
            "Retour": .5,
            "Destruction": .125,
            "Attaque": .75,
            "Effet": .25,
            "Totem" : .7
        })

        global effets
        effets = dict[str, tuple[int, int, int]]({
            "Liaison": (103, 141, 212),
            "Echange": (255, 0, 0),
            "Invocation": (150, 0, 150),
            "Obscurite": (110.8, 110.8, 167.4),
            "Intoxication": (0, 150, 0),
            "Bloque": (255, 255, 255),
            "Gravite": (0, 150, 150),
            "Feu": (150, 0, 0),
            "Recul": (150, 0, 0),
            "Froid": (103, 212, 212)
        })

        global scènes
        scènes = dict[str, Scène]({
            "ChoixLangue": ChoixLangue(),
            "Intro": Cinématique("Intro"),
            "Menu": Menu(),
            "SélectionPersonnage": SélectionPersonnage(),
            "Partie": Partie(),
            "Niveau": Niveau(),
            "Pause": Pause(),
            "Inventaire": Inventaire(),
            "Récompense": Récompense(),
            "Dialogue": Dialogue(),
            "Paramètres": Paramètres_v2(),
            "Mort": Mort(),
            "Monologue": Cinématique("Monologue"),
            "Fin": Fin(),
            "Arbre_Amélioration":Arbre_Amélioration()
        })

        global scène
        if première_fois:
            scène = "ChoixLangue"
        else:
            scène = "Menu"

        global données_scène_suivante
        données_scène_suivante = dict[str]()

        global chronomètre
        chronomètre = Chronomètre()

        global debug
        debug = True

        global défilement
        défilement = 0

        global affichage_dégat
        affichage_dégat = []

        global écran_luminosité
        écran_luminosité = pygame.Surface((taille_fenêtre + 2*marge, taille_fenêtre), pygame.SRCALPHA)
        écran_luminosité.fill((0, 0, 0, 0))

        image = pygame.image.load("Ressources/Images/Interface Utilisateur/Noir.png").convert_alpha()
        image.set_alpha(128)
        self.effet_sombre = pygame.transform.scale(image, (taille_fenêtre, taille_fenêtre))

        self.obscurité = pygame.Surface((taille_fenêtre, taille_fenêtre), pygame.SRCALPHA)
        # self.obscurité.fill((110.8, 110.8, 167.4, 255))
        self.obscurité.fill((0, 0, 0, 255))

    def initialiser_sql(self):
        """ Jeu -> None
        Initialise l'utilisation du SQL. """

        chemin_bibliothèque = "Ressources/Bases de Données/bibliothèque.db"
        if os.path.exists(chemin_bibliothèque):
            os.remove(chemin_bibliothèque)
        self.connexion = sqlite3.connect(chemin_bibliothèque)

        global curseur
        curseur = self.connexion.cursor()

    def exécuter_fichier_sql(self):
        """ Jeu -> None
        Exécute le fichier SQL. """

        with open("Ressources/Bases de Données/instructions.sql", "r") as fichier:
            instructions = fichier.read()
        for instruction in instructions.split(";"):
            curseur.execute(instruction)

    def initialiser_pygame(self):
        """ Jeu -> None
        Initialise la bibliothèque pygame. """

        pygame.init()
        pygame.mixer.init()

        fenêtre_x, fenêtre_y = taille_écran(1. if liste_paramètres.recupérer_paramètre("fullscreen") else .5)

        global marge
        marge = (fenêtre_x - fenêtre_y) // 2

        global taille_fenêtre
        taille_fenêtre = fenêtre_y

        global fenêtre
        fenêtre = pygame.display.set_mode((fenêtre_x, fenêtre_y))

        pygame.display.set_caption("The Legend of M.Picard")
        pygame.display.set_icon(pygame.image.load("Ressources/Images/Interface Utilisateur/Logo.png"))

        global surface_curseur_souris
        surface_curseur_souris = pygame.image.load("Ressources/Images/Interface Utilisateur/Curseur.png").convert_alpha()

        pygame.mouse.set_visible(False)

        global horloge
        horloge = pygame.time.Clock()
    
    def jouer(self):
        """ Jeu -> None
        Joue le jeu. """

        scène_actuelle = ""

        global actualiser_nouvelle_scène
        actualiser_nouvelle_scène = True

        global dernière_scène
        dernière_scène = ""

        global sous_scène
        sous_scène = False

        while True:
            if scène_actuelle != scène:
                if not sous_scène:
                    dernière_scène = scène_actuelle
                sous_scène = False
                if actualiser_nouvelle_scène:
                    scènes[scène].initialiser()
                    données_scène_suivante: dict[str] = {}
                scène_actuelle = scène
                actualiser_nouvelle_scène = True
            if sous_scène:
                scènes[dernière_scène].afficher()
            scènes[scène].action()
            if scène == "Niveau" and joueur.effets.contient("Obscurite"):
                effet = joueur.effets.récupérer("Obscurite")
                coefficient = max(effet.temps_restant / effet.durée, 0.)
                self.obscurité.fill((194.8 * coefficient**2 - 385.8 * coefficient + 255, 194.8 * coefficient**2 - 385.8 * coefficient + 255, -31.6 * coefficient**2 - 159.4 * coefficient + 255, 255 * coefficient))
                if not possède_amélioration(joueur.enchantements,6): fenêtre.blit(self.obscurité, (marge, 0), special_flags=pygame.BLEND_MULT)

                self.effet_sombre.set_alpha(128 + 128 * coefficient)
            else:
                self.effet_sombre.set_alpha(128)
            afficher(self.effet_sombre, (0, 0))
            afficher_curseur_souris()
            fenêtre.blit(self.bordure, (0, 0))
            fenêtre.blit(self.bordure, (marge + taille_fenêtre, 0))
            écran_luminosité.fill((0, 0, 0, int((100 - getattr(liste_paramètres, "lighting")) * 2.55)))
            fenêtre.blit(écran_luminosité, (0, 0))
            pygame.display.flip()
            horloge.tick()

class Grille:
    """ Représente une grille. """

    def __init__(self):
        """ Grille -> None """

        self.contenu: list[list] = []

    def dans_la_grille(self, x: int, y: int):
        """ Grille, int, int -> bool
        Détermine si les coordonnées (`x`; `y`) sont dans la grille `self`. """

        return self.hauteur() > 0 and 0 <= x < self.longueur() and 0 <= y < self.hauteur()

    def récupérer(self, x: int, y: int):
        """ Grille, int, int -> Any
        Récupère l'élément de coordonnées (`x`; `y`) dans la grille `self`. """

        if not self.dans_la_grille(x, y):
            raise IndexError("Coordonnées hors de la grille.")
        return self.contenu[y][x]

    def placer(self, x: int, y: int, élément):
        """ Grille, int, int, Any -> None 
        Place l'`élément` dans la grille `self` aux coordonnées (`x`; `y`). """

        if not self.dans_la_grille(x, y):
            raise IndexError("Coordonnées hors de la grille.")
        self.contenu[y][x] = élément
    
    def ajouter_ligne(self, ligne: list):
        """ Grille, [Any] -> None
        Ajoute une `ligne` à la grille `self`. """

        if len(self.contenu) > 0 and len(ligne) != len(self.contenu[0]):
            raise ValueError(f"La ligne n'a pas la même longueur que les autres ({len(self.contenu[0])}).")
        self.contenu.append(ligne)
    
    def ajouter_colonne(self, colonne: list):
        """ Grille, [Any] -> None
        Ajoute une `colonne` à la grille `self`. """

        if len(self.contenu) > 0 and len(colonne) != len(self.contenu):
            raise ValueError("La colonne n'a pas la même longueur que les autres.")
        for i, élément in enumerate(colonne):
            self.contenu[i].append(élément)

    def longueur(self):
        """ Grille -> int
        Renvoie la longueur de la grille. """

        return len(self.contenu[0])

    def hauteur(self):
        """ Grille -> int
        Renvoie la hauteur de la grille. """

        return len(self.contenu)
    
    def __repr__(self):
        """ Grille -> str
        Renvoie une représentation de la grille. """

        return "\n".join([str(ligne) for ligne in self.contenu])

class Composition:
    """ Représente la composition d'une salle.
    Ces attributs sont 4 bolléens qui représente la présence d'une ouverture dans les 4 directions. """

    def __init__(self, haut: bool = False, droite: bool = False, bas: bool = False, gauche: bool = False, bordure: bool = False):
        """ Composition, bool, bool, bool, bool -> None """

        self.haut = haut
        self.droite = droite
        self.bas = bas
        self.gauche = gauche

        self.bordure = bordure
    
    def ouverture_existe(self, dx: int, dy: int):
        """ Composition, int, int -> bool
        Détermine si la salle est ouvert dans la direction (`dx`; `dy`). """

        if (dx, dy) == (0, 0):
            return True
        
        if abs(dx) + abs(dy) > 1:
            return False
        
        return {(0, -1): self.haut, (1, 0): self.droite, (0, 1): self.bas, (-1, 0): self.gauche}[(dx, dy)]

    def créer_ouvertures(self, grille: Grille, x: int, y: int, isolé: bool):
        """ Composition, Grille, int, int, bool -> None
        Renvoie une composition de salle aléatoire en (`x`; `y`) basée sur la composition `self` en respectant les règles de génération :
        - une salle ne peut pas générer une ouverture en bordure de donjon (vérifié avec `taille`)
        - une salle ne peut pas générer une ouverture vers une salle déjà créée (vérifié avec `grille.récupérer`). """

        if not self.haut and y > 0:
            salle = grille.récupérer(x, y - 1)
            if isolé:
                if type(salle) is Salle:
                    self.haut = True
                    composition = salle.composition
                    composition.bas = True
                    grille.placer(x, y - 1, Salle(composition))
                    isolé = False
            elif salle is None and random.randint(0, 2):
                self.haut = True
        
        if not self.droite and x < taille_donjon - 1:
            salle = grille.récupérer(x + 1, y)
            if isolé:
                if type(salle) is Salle:
                    self.droite = True
                    composition = salle.composition
                    composition.gauche = True
                    grille.placer(x + 1, y, Salle(composition))
                    isolé = False
            elif salle is None and random.randint(0, 2):
                self.droite = True
        
        if not self.bas and y < taille_donjon - 1:
            salle = grille.récupérer(x, y + 1)
            if isolé:
                if type(salle) is Salle:
                    self.bas = True
                    composition = salle.composition
                    composition.haut = True
                    grille.placer(x, y + 1, Salle(composition))
                    isolé = False
            elif salle is None and random.randint(0, 2):
                self.bas = True
        
        if not self.gauche and x > 0:
            salle = grille.récupérer(x - 1, y)
            if isolé:
                if type(salle) is Salle:
                    self.gauche = True
                    composition = salle.composition
                    composition.droite = True
                    grille.placer(x - 1, y, Salle(composition))
                    isolé = False
            elif salle is None and random.randint(0, 2):
                self.gauche = True
        
        return isolé

    def coordonnées_prochaines_salles(self, grille: Grille, x: int, y: int):
        """ Composition, Grille, int, int -> [(int, int)]
        Renvoie la liste des "enfants" de la salle en (`x`; `y`), c'est-à-dire des autres salles que cette salle va créer, dans un ordre aléatoire. """

        coordonnées_prochaines_salles: list[tuple[int, int]] = []

        if self.haut and grille.récupérer(x, y - 1) is None:
            coordonnées_prochaines_salles.append((x, y - 1))
        
        if self.droite and grille.récupérer(x + 1, y) is None:
            coordonnées_prochaines_salles.append((x + 1, y))
        
        if self.bas and grille.récupérer(x, y + 1) is None:
            coordonnées_prochaines_salles.append((x, y + 1))
        
        if self.gauche and grille.récupérer(x - 1, y) is None:
            coordonnées_prochaines_salles.append((x - 1, y))
        
        random.shuffle(coordonnées_prochaines_salles)

        return coordonnées_prochaines_salles

    def fermer_ouverture(self, x: int, y: int, prochain_x: int, prochain_y: int):
        """ Composition, int, int, int, int -> None
        Modifie la composition `self` de la salle en (`x`; `y`) dans le cas où une nouvelle salle s'est générée là où cette salle devait généré une salle "enfant". """

        if prochain_y - y == -1:
            self.haut = False
        if prochain_x - x == 1:
            self.droite = False
        if prochain_y - y == 1:
            self.bas = False
        if prochain_x - x == -1:
            self.gauche = False

def générer_labyrinthe():
    """ () -> Grille
    Génère un nouveau labyrinthe et le renvoie. """

    grille = Grille()
    for _ in range(taille_donjon):
        grille.ajouter_ligne([None for _ in range(taille_donjon)])
    longueur = 0
    isolé = False

    while longueur < taille_donjon ** 2:
        départ_x, départ_y = coordonnées_salle_vide(grille)
        composition = Composition(False, False, False, False)
        grille, longueur = générer_salle(grille, départ_x, départ_y, composition, longueur, isolé)
        isolé = True

    return grille

def coordonnées_salle_vide(grille: Grille):
    """ Grille -> int, int
    Détermine puis renvoie des coordonnées de salle où il n'y a pas de salle encore créée. """

    x = random.randint(0, taille_donjon - 1)
    y = random.randint(0, taille_donjon - 1)

    while grille.récupérer(x, y) is not None:
        x = random.randint(0, taille_donjon - 1)
        y = random.randint(0, taille_donjon - 1)
    
    return x, y

def générer_salle(grille: Grille, x: int, y: int, composition: Composition, longueur: int, isolé: bool) -> tuple[Grille, int]:
    """ Grille, int, int, Composition, int, bool -> Grille, int
    Génère récurssivement une nouvelle salle de labyrinthe dans la `grille` et la renvoie. """

    isolé = composition.créer_ouvertures(grille, x, y, isolé)
    grille.placer(x, y, Salle(composition))
    longueur += 1
    afficher_chargement()

    prochaines_salles = composition.coordonnées_prochaines_salles(grille, x, y)

    for prochaine_salle in prochaines_salles:
        prochain_x, prochain_y = prochaine_salle
        if grille.récupérer(prochain_x, prochain_y) is None:
            prochaine_composition = composition_prochaine_salle(x, y, prochain_x, prochain_y)
            grille, longueur = générer_salle(grille, prochain_x, prochain_y, prochaine_composition, longueur, isolé)
        else:
            composition.fermer_ouverture(x, y, prochain_x, prochain_y)
            grille.placer(x, y, Salle(composition))
    return grille, longueur

def composition_prochaine_salle(x: int, y: int, prochain_x: int, prochain_y: int):
    """ int, int, int, int -> Composition
    Renvoie la composition de la prochaine salle avec l'ouverture appropriée pour qu'on puisse passer de la salle en (`x`; `y`) à la salle en (`prochain_x`, `prochain_y`) sans problème. """

    return Composition(prochain_y - y == 1, prochain_x - x == -1, prochain_y - y == -1, prochain_x - x == 1)

class Case:
    """ Représente une Case. """

    def __init__(self, type: str):
        """ Case, str -> None """

        self.type = type

        collision, hauteur, sortie, ouvrable = exécuter_sql(f"""SELECT collision, hauteur, sortie, ouvrable FROM "Case" WHERE type = '{self.type}';""")[0]
        self.collision = bool(collision)
        self.hauteur = hauteur
        self.sortie = bool(sortie)
        self.ouvrable = bool(ouvrable)
        
        self.numéro = self.numéro_case()
        
        self.initialiser_image()

    def numéro_case(self):
        sql = exécuter_sql(f"""SELECT nombre FROM VariationCase WHERE type = '{self.type}';""")
        if len(sql) == 0:
            return 1
        return random.randint(1, sql[0][0])

    def initialiser_image(self):
        """ Case -> None
        Initialise l'image de la Case `self`. """

        image = pygame.image.load(f"Ressources/Images/Cases/{self.type}{'' if self.numéro == 1 else self.numéro}.png")
        self.image = pygame.transform.scale(image, (taille_case, image.get_height() / image.get_width() * taille_case))

        # self.image = charger_image(f"Cases/{self.type}{'' if self.numéro == 1 else self.numéro}", taille_case, image.get_height() / image.get_width() * taille_case)

    def afficher(self, x: int, y: int, salle: type["Salle"] = None):
        """ Case, int, int, Salle -> None
        Affiche l'image de la case `self` sur la fenêtre au point de coordonnées (`x`; `y`) dans la grille. """

        affichage_x = x * taille_case
        affichage_y = y * taille_case

        if monde == "NSI" and self.type == "AND" and x % taille_salle > 0 and x % taille_salle < taille_salle - 1 and y % taille_salle > 0 and y % taille_salle < taille_salle - 1:
            gauche = salle.récupérer(x % taille_salle - 1, y % taille_salle)
            droite = salle.récupérer(x % taille_salle + 1, y % taille_salle)
            haut = salle.récupérer(x % taille_salle, y % taille_salle - 1)
            bas = salle.récupérer(x % taille_salle, y % taille_salle + 1)

            horizontal = gauche.numéro == 2 and droite.numéro == 2
            vertical = haut.numéro == 2 and bas.numéro == 2
            
            condition = horizontal ^ vertical

            numéro = condition + 1

            if self.numéro != numéro:
                self.numéro = numéro
                self.initialiser_image()

        affichage_y -= self.image.get_height() - taille_case

        case = pygame.Rect(affichage_x, affichage_y, taille_case, self.image.get_height())
        if not est_visible(case):
            return

        coordonnées = (affichage_x, affichage_y)
        afficher_en_jeu(self.image, coordonnées)

        if not liste_paramètres.recupérer_paramètre("visionIR") and not salle.est_visible(x // taille_salle, y // taille_salle):
            sombre = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            sombre.fill((0, 0, 0, compression(distance(coordonnées, joueur.coordonnées_affichage())**2 / 1000 - 150, 0, 255)))
            afficher_en_jeu(sombre, coordonnées)

        position_souris_en_jeu = coordonnées_réelles(position_souris[0] - marge, position_souris[1])
        
        if position_souris_en_jeu[0] // taille_case == x and position_souris_en_jeu[1] // taille_case == y:
            image = pygame.Surface((taille_case, self.image.get_height()), pygame.SRCALPHA)
            image.fill((255, 255, 255, 64))
            afficher_en_jeu(image, coordonnées)
    
    def __repr__(self):
        """ Case -> str
        Renvoie une représentation de la case. """

        return f"[{self.type}{'' if self.numéro == 1 else self.numéro}]"

    def ouvrir(self, difficulté: int):
        """ Case, int -> None
        Ouvre la case `self` comme si c'était un coffre. """

        self.numéro += 1
        self.ouvrable = False
        self.initialiser_image()

        if self.type == "Fontaine":
            partie = joueur.statistiques.vie.maximum / joueur.statistiques.vie.division
            joueur.statistiques.vie.valeur = min((joueur.statistiques.vie.valeur - 1.02) // partie * partie + 2 * partie, joueur.statistiques.vie.maximum)

        else:
            global scène
            données_scène_suivante["récompense"] = self.type
            scène = "Récompense"

def ligne_haut_salle(mur_par_défaut: str, ouverture: bool):
    """ str, bool -> [Case]
    Crée une ligne pour le haut avec ou sans ouverture. """

    taille_ouverture = 3 - taille_salle % 2
    taille_côté = (taille_salle - taille_ouverture) // 2

    if monde == "Parcoursup":

        mur_côté = []
        for _ in range(taille_côté):
            mur_côté.append(Case(random.choice(exécuter_sql(f"""SELECT mur_par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};"""))[0]))

        mur_ouverture = []
        for _ in range(taille_ouverture):
            mur_ouverture.append(None if ouverture else Case(random.choice(exécuter_sql(f"""SELECT mur_par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};"""))[0]))

        return [Case(random.choice(exécuter_sql(f"""SELECT mur_par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};"""))[0])] + mur_côté + mur_ouverture + mur_côté

    mur_côté = [Case(mur_par_défaut) for _ in range(taille_côté)]
    mur_ouverture = [None if ouverture else Case(mur_par_défaut) for _ in range(taille_ouverture)]

    return [Case(mur_par_défaut)] + mur_côté + mur_ouverture + mur_côté

def ligne_intermédiaire_salle(mur_par_défaut: str):
    """ mur_par_défaut -> [Case]
    Crée une ligne sans ouverture. """

    if monde == "Parcoursup":

        return [Case(random.choice(exécuter_sql(f"""SELECT mur_par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};"""))[0])] + [None for _ in range(taille_salle - 1)]
        
    return [Case(mur_par_défaut)] + [None for _ in range(taille_salle - 1)]

def ligne_centrale_salle(mur_par_défaut: str, ouverture: bool):
    """ str, bool -> [Case]
    Crée une ligne centrale avec ou sans ouvertures à gauche. """

    mur_centre = [None for _ in range(taille_salle - 1)]

    if monde == "Parcoursup":

        return [None if ouverture else Case(random.choice(exécuter_sql(f"""SELECT mur_par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};"""))[0])] + mur_centre

    mur_ouverture = [None if ouverture else Case(mur_par_défaut)]

    return mur_ouverture + mur_centre
    
def créer_grille_salle(composition: Composition, mur_par_défaut: str):
    """ Composition, str -> Grille
    Crée la grille de la salle en fonction de la `composition`. """

    grille = Grille()

    taille_ouverture = 3 - taille_salle % 2
    taille_côté = (taille_salle - taille_ouverture) // 2
    
    grille.ajouter_ligne(ligne_haut_salle(mur_par_défaut, composition.haut))

    for _ in range(taille_côté):
        grille.ajouter_ligne(ligne_intermédiaire_salle(mur_par_défaut))

    for _ in range(taille_ouverture):
        grille.ajouter_ligne(ligne_centrale_salle(mur_par_défaut, composition.gauche))

    for _ in range(taille_côté):
        grille.ajouter_ligne(ligne_intermédiaire_salle(mur_par_défaut))
    
    return grille

def ligne_haut_ou_bas_bordure(mur_par_défaut: str, haut_ou_bas: bool, gauche: bool, droite: bool):
    """ str, bool, bool -> [Case]
    Crée une ligne pour le haut ou le bas. """

    if haut_ou_bas:
        return [Case(mur_par_défaut) for _ in range(taille_salle)]
    return ligne_intermédiaire_bordure(mur_par_défaut, gauche, droite)

def ligne_intermédiaire_bordure(mur_par_défaut: str, gauche: bool, droite: bool):
    """ str, bool, bool -> [Case]
    Crée une ligne intermédiaire. """

    return [Case(mur_par_défaut) if gauche else None] + [None] * (taille_salle - 2) + [Case(mur_par_défaut) if droite else None]

def créer_grille_bordure(composition: Composition, mur_par_défaut: str):
    """ Composition, str -> Grille
    Crée la grille de la bordure en fonction de la `composition`. """

    grille = Grille()

    grille.ajouter_ligne(ligne_haut_ou_bas_bordure(mur_par_défaut, composition.haut, composition.gauche, composition.droite))

    for _ in range(taille_salle - 2):
        grille.ajouter_ligne(ligne_intermédiaire_bordure(mur_par_défaut, composition.gauche, composition.droite))
    
    grille.ajouter_ligne(ligne_haut_ou_bas_bordure(mur_par_défaut, composition.bas, composition.gauche, composition.droite))

    return grille

class Salle:
    """ Représente une Salle du Donjon, constitué d'une Grille faite de Cases. """

    def __init__(self, composition: Composition):
        """ Salle, Composition -> None """

        self.composition = composition

        if self.composition.bordure:
            self.initialiser_bordure(composition)
        else:
            self.initialiser_salle(composition)
        
        self.difficulté: int = None
        self.nombre_monstres: int = None
        self.libérée = False
        self.boss = False
        self.combat_boss = False

        self.monstres: list[Monstre|PNJ] = []
    
    def initialiser_bordure(self, composition: Composition):
        """ Salle, Composition -> None
        Initialise les grilles pour la bordure. """

        self.grille_sol = Grille()
        for _ in range(taille_salle):
            self.grille_sol.ajouter_ligne([None] * taille_salle)

        mur_par_défaut: str = exécuter_sql(f"""SELECT mur_par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};""")[0][0]
        
        self.grille_mur = créer_grille_bordure(composition, mur_par_défaut)
    
    def initialiser_salle(self, composition: Composition):
        """ Salle, Composition -> None
        Initialise les grilles pour la bordure. """
        
        self.grille_sol = Grille()

        if monde == "Parcoursup":
            
            for _ in range(taille_salle):
                ligne = []

                for _ in range(taille_salle):
                    ligne.append(Case(random.choice(exécuter_sql(f"""SELECT sol_par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};"""))[0]))
                
                self.grille_sol.ajouter_ligne(ligne)

        else:

            sol_par_défaut: str = exécuter_sql(f"""SELECT sol_par_defaut FROM Monde WHERE nom = '{monde}';""")[0][0]

            for _ in range(taille_salle):
                self.grille_sol.ajouter_ligne([Case(sol_par_défaut) for _ in range(taille_salle)])

        mur_par_défaut: str = exécuter_sql(f"""SELECT mur_par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};""")[0][0]
        
        self.grille_mur = créer_grille_salle(composition, mur_par_défaut)

    def ajouter_motif(self):
        """ Salle -> None
        Ajoute un motif à la salle. """

        if random.randint(0, 2):
            identifiant = random.randint(1, exécuter_sql(f"""SELECT COUNT(DISTINCT salle) FROM MotifSalle;""")[0][0])
            sql: list[tuple[int, int, int]] = exécuter_sql(f"""SELECT "case", x, y FROM MotifSalle WHERE salle = {identifiant};""")
            for case, x, y in sql:
                nom_case: str = random.choice(exécuter_sql(f"""SELECT mur_{"supplementaire_" if case == 2 else ""}par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};"""))[0]
                hauteur: int = exécuter_sql(f"""SELECT hauteur FROM "Case" WHERE type = '{nom_case}';""")[0][0]
                self.placer(x + 1, y + 1, Case(nom_case), hauteur=hauteur)

    def afficher(self, hauteur: int, x: int, y: int):
        """ Salle, int, int, int -> None
        Affiche la salle sur la fenêtre. """

        salle = pygame.Rect(x * taille_salle * taille_case, y * taille_salle * taille_case, taille_case * taille_salle, taille_case * taille_salle)
        if not est_visible(salle):
            return

        if hauteur == 0:
            self.affiche_grille(x, y, self.grille_sol)
        else:
            self.affiche_grille(x, y, self.grille_mur)
    
    def affiche_grille(self, x: int, y: int, grille: Grille):
        """ Salle, int, int, Grille -> None
        Affiche la grille sur la fenêtre. """

        for dy in range(taille_salle):
            for dx in range(taille_salle):
                case: Case = grille.récupérer(dx, dy)
                if case is not None:
                    case.afficher(x * taille_salle + dx, y * taille_salle + dy, salle=self)
    
    def récupérer(self, x: int, y: int) -> Case:
        """ Salle, int, int -> Case
        Récupère la Case de coordonnées (`x`; `y`) dans la salle `self`. """

        case_mur: Case = self.grille_mur.récupérer(x, y)
        if case_mur is None:
            case_sol: Case = self.grille_sol.récupérer(x, y)
            return case_sol
        return case_mur
    
    def placer(self, x: int, y: int, case: Case, hauteur: int = 1):
        """ Salle, int, int, Case -> None
        Place la `case` dans la salle `self` aux coordonnées (`x`; `y`). """

        if hauteur == 0:
            self.grille_sol.placer(x, y, case)
        else:
            self.grille_mur.placer(x, y, case)
        
    def __repr__(self):
        """ Salle -> str
        Renvoie une représentation compacte de la salle basée sur sa composition. """

        return f"Salle({int(self.composition.haut)}{int(self.composition.droite)}{int(self.composition.bas)}{int(self.composition.gauche)})"

    def est_dangereuse(self):
        """ Salle -> bool
        Détermine si la salle `self` a été créée avec au moins un Monstre dedans. """

        return not self.libérée and self.difficulté > 0
    
    def est_libérée(self):
        """ Salle -> bool
        Détermine si la salle `self` a été libérée de tous les Monstres initialements apparus dedans. """

        return len([monstre for monstre in self.monstres if isinstance(monstre, Monstre)]) == 0
    
    def est_visible(self, x: int, y: int):
        """ Salle, int, int -> bool
        Détermine si la salle `self` de coordonnées (`x`; `y`) est visible depuis le joueur (salle où est le joueur + salles adjacentes). """

        return self.composition.ouverture_existe(joueur.x // taille_salle - x, joueur.y // taille_salle - y)

    def fermer(self, haut: bool = False, gauche: bool = False):
        """ Salle, bool, bool -> None
        Ferme toutes les ouvertures de la Salle `self`. """

        mur_supplémentaire_par_défaut: str = exécuter_sql(f"""SELECT mur_supplementaire_par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};""")[0][0]
        
        if haut:
            for x in range(taille_salle):
                if self.grille_mur.récupérer(x, 0) is None:
                    self.grille_mur.placer(x, 0, Case(mur_supplémentaire_par_défaut))
        
        if gauche:
            for y in range(taille_salle):
                if self.grille_mur.récupérer(0, y) is None:
                    self.grille_mur.placer(0, y, Case(mur_supplémentaire_par_défaut))

    def ouvrir(self, haut: bool = False, gauche: bool = False):
        """ Salle, bool, bool -> None
        Ouvre toutes les ouvertures fermées de la Salle `self`. """

        mur_supplémentaire_par_défaut: str = exécuter_sql(f"""SELECT mur_supplementaire_par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};""")[0][0]
        
        if haut:
            for x in range(taille_salle):
                case: Case = self.grille_mur.récupérer(x, 0)
                if case is not None and case.type == mur_supplémentaire_par_défaut:
                    self.grille_mur.placer(x, 0, None)
        
        if gauche:
            for y in range(taille_salle):
                case: Case = self.grille_mur.récupérer(0, y)
                if case is not None and case.type == mur_supplémentaire_par_défaut:
                    self.grille_mur.placer(0, y, None)

class Donjon:
    """ Représente un Donjon, constitué d'une Grille faite de Salles. """

    def __init__(self):
        """ Donjon -> None """

        self.grille = générer_labyrinthe()

        while self.salles_inaccessibles():
            self.grille = générer_labyrinthe()

            self.récursion_difficulté(taille_donjon // 2, taille_donjon // 2, 0)
        
        self.ajouter_motifs()

        self.choisir_salle_boss()

        composition = Composition(gauche=True, bordure=True)
        self.grille.ajouter_colonne([Salle(composition) for _ in range(taille_donjon)])

        composition = Composition(haut=True, bordure=True)
        self.grille.ajouter_ligne([Salle(composition) for _ in range(taille_donjon + 1)])

    def salles_inaccessibles(self):
        """ Donjon -> bool
        Détermine s'il y a des salles inaccessibles. """

        for x in range(taille_donjon):
            for y in range(taille_donjon):
                salle = self.récupérer(x, y)
                if salle.difficulté is None:
                    return True
        return False

    def récursion_difficulté(self, x: int, y: int, difficulté: int):
        """ Donjon, int, int, int -> None
        Attribue récursivement à chaque salle du donjon `self` une difficulté basée sur sa distance au centre. """

        salle = self.récupérer(x, y)

        if salle.difficulté is not None and salle.difficulté <= difficulté:
            return
        
        salle.difficulté = difficulté
        salle.nombre_monstres = difficulté

        if salle.composition.haut:
            self.récursion_difficulté(x, y - 1, difficulté + 1)
        
        if salle.composition.droite:
            self.récursion_difficulté(x + 1, y, difficulté + 1)
        
        if salle.composition.bas:
            self.récursion_difficulté(x, y + 1, difficulté + 1)
        
        if salle.composition.gauche:
            self.récursion_difficulté(x - 1, y, difficulté + 1)

    def ajouter_motifs(self):
        """ Donjon -> None
        Ajoute des motifs aux Salles du Donjon `self`. """

        for x in range(taille_donjon):
            for y in range(taille_donjon):
                salle = self.récupérer(x, y)
                if salle.difficulté > 0 and not salle.boss:
                    salle.ajouter_motif()

    def choisir_salle_boss(self):
        """ Donjon -> None
        Choisit la Salle "Boss" du Donjon `self`. """
        
        maximum_x = 0
        maximum_y = 0
        
        maximum = 0

        for x in range(taille_donjon):
            for y in range(taille_donjon):
                salle = self.récupérer(x, y)
                if salle.difficulté > maximum:
                    maximum = salle.difficulté
                    maximum_x = x
                    maximum_y = y
        
        salle = self.récupérer(maximum_x, maximum_y)
        salle.boss = True

    def afficher(self, hauteur: int):
        """ Donjon, int -> None
        Affiche le donjon sur la fenêtre. """
        
        for y in range(self.grille.hauteur()):
            for x in range(self.grille.longueur()):
                salle = self.récupérer(x, y)
                if salle is not None:
                    if liste_paramètres.recupérer_paramètre("visionIR") or hauteur > 0 or salle.est_visible(x, y):
                        salle.afficher(hauteur, x, y)
    
    def récupérer(self, x: int, y: int) -> Salle:
        """ Donjon, int, int -> Salle
        Récupère la salle de coordonnées (`x`; `y`) dans le donjon `self`. """

        return self.grille.récupérer(x, y)
    
    def placer(self, x: int, y: int, salle: Salle):
        """ Donjon, int, int, Salle -> None
        Place la `salle` dans le donjon `self` aux coordonnées (`x`; `y`). """

        self.grille.placer(x, y, salle)
    
    def longueur(self):
        """ Donjon -> int
        Renvoie la longueur d'un côté du donjon `self`. """

        return self.grille.longueur()
    
    def hauteur(self):
        """ Donjon -> int
        Renvoie la hauteur d'un côté du donjon `self`. """

        return self.grille.hauteur()
    
    def rajouter_monstre(self):
        """ Donjon -> None
        Fait rapparaître les monstres des salles non libérées qui ne sont pas celle du joueur. """

        for y in range(taille_donjon):
            for x in range(taille_donjon):
                salle = self.récupérer(x, y)
                if salle.boss or salle.combat_boss:
                    continue
                if salle is not None and not salle.libérée and salle is not joueur.salle:
                    if len(salle.monstres) < salle.nombre_monstres:
                        entités.ajouter_monstre(x, y, salle)

class Caméra:
    """ Représente une caméra """

    def __init__(self, coordonnées: tuple[int, int], zoom: float):
        """ Caméra, (int, int), float -> None """

        self.x, self.y = coordonnées
        self.zoom = zoom

        self.objectif_x, self.objectif_y = coordonnées
        self.objectif_zoom = zoom

        self.vitesse_déplacement = 1.
        self.vitesse_zoom = 1.
    
    def déplacer(self):
        """ Caméra -> None
        Déplace la caméra `self` vers son objectif de déplacement et de zoom. """

        self.x += (self.objectif_x - self.x) * self.vitesse_déplacement
        self.y += (self.objectif_y - self.y) * self.vitesse_déplacement

        self.zoom += (self.objectif_zoom - self.zoom) * self.vitesse_zoom
    
    def mettre_objectif_déplacement(self, coordonnées: tuple[int, int], vitesse: float):
        """ Caméra, (int, int), float -> None
        Défini le point en `coordonnées` que la caméra devra suivre et à quelle `vitesse` elle devra le rejoindre. """

        self.objectif_x, self.objectif_y = coordonnées
        self.objectif_x = compression(self.objectif_x, (taille_fenêtre / self.zoom)//2, (taille_donjon * taille_salle + 1) * taille_case - (taille_fenêtre / self.zoom)//2)
        self.objectif_y = compression(self.objectif_y, (taille_fenêtre / self.zoom)//2, (taille_donjon * taille_salle + 1) * taille_case - (taille_fenêtre / self.zoom)//2)
        self.vitesse_déplacement = vitesse
    
    def mettre_objectif_zoom(self, zoom: float, vitesse: float):
        """ Caméra, (int, int), float -> None
        Défini le `zoom` que la caméra devra suivre et à quelle `vitesse` elle devra le rejoindre. """

        self.objectif_zoom = zoom
        self.vitesse_zoom = vitesse
    
    def __repr__(self):
        """ Caméra -> str
        Renvoie une représentation de la caméra. """

        return f"Caméra : ({self.x}; {self.y}) x{self.zoom}"

class Entité: # pour le typage de la classe GestionnaireStatistiques
    nom: str

class GestionnaireEnchantement:

    def __init__(self):
        """ GestionnaireEnchantement -> None"""

        self.liste_enchantements = [] 
    
    def ajouter_enchantement(self, ench_id):
        """ GestionnaireEnchantement, int -> None
        Ajoute un enchantement"""
        
        self.liste_enchantements.append(ench_id)
    
    def possède_enchant(self, ench_id):
        """ GestionnaireEnchantement, int -> bool
        Regarde si un enchantement appartient au Gestionnaire d'enchantement"""

        for enchant in self.liste_enchantements:
            if enchant == ench_id:
                return True
        return False
        
class GestionnaireStatistiques:
    """ Gère les Statistiques d'une Entité. """

    def __init__(self, entité: Entité):
        """ GestionnaireStatistiques, Entité -> None """

        if type(entité) is PNJ:
            self.vie = Statistique(1000, division=4, régénération=3)
            self.puissance_physique = Statistique(1000)
            self.vitesse_physique = Statistique(1000)
            self.vitesse_déplacement = Statistique(1000)
        
        else:
            self.vie = self.initialiser_statistique(entité, "vie")
            self.puissance_physique = self.initialiser_statistique(entité, "puissance_physique")
            self.vitesse_physique = self.initialiser_statistique(entité, "vitesse_physique")
            self.vitesse_déplacement = self.initialiser_statistique(entité, "vitesse_deplacement")
    
    def initialiser_statistique(self, entité: Entité, catégorie: str):
        """ GestionnaireStatistiques, Entité, str -> None
        Initialise la Statistique de `catégorie` donnée. """
        
        maximum = None
        division = None
        régénération = None
        valeur_départ = None

        if type(entité) is Monstre:
            minuscule = "monstre"
            majuscule = "Monstre"
        else:
            minuscule = "personnage"
            majuscule = "Personnage"

        for sous_catégorie in ['maximum', 'division', 'regeneration', 'valeur_depart']:
            sql: list[tuple[int]] = exécuter_sql(f"""SELECT valeur FROM Statistique{majuscule} JOIN {majuscule} ON {majuscule}.nom = Statistique{majuscule}.{minuscule} WHERE {majuscule}.nom = '{"Yann" if (type(entité) is Joueur or type(entité) is Boss) else entité.nom}' AND categorie == '{catégorie}' AND sous_categorie == '{sous_catégorie}';""")

            if len(sql):
                valeur = sql[0][0]

                if sous_catégorie == 'maximum':
                    maximum = round(valeur * 1.1**(difficulté_monde/6))
                    if type(entité) is Boss and catégorie == "vie":
                        maximum *= 10
                
                elif sous_catégorie == 'division':
                    division = valeur
                
                elif sous_catégorie == 'regeneration':
                    régénération = valeur
                    if type(entité) is Boss and catégorie == "vie":
                        régénération = 0
                
                elif sous_catégorie == 'valeur_depart':
                    valeur_départ = valeur
        
        return Statistique(maximum, division=division if division is not None else 1, régénération=régénération if régénération is not None else 0, valeur_départ=valeur_départ)

    def actualiser(self, entité: Entité):
        """ GestionnaireStatistiques, Entité -> None
        Actualise chaque Statistique de l'Entité donnée. """

        for nom_statistique in self.__dict__:
            statistique: Statistique = getattr(self, nom_statistique)

            partie = statistique.maximum / statistique.division

            modulo = statistique.valeur % partie

            if modulo > 1.01:
                modulo = compression(modulo + statistique.régénération - (5 if entité.effets.contient("Intoxication") else 0) - (2 if entité.effets.contient("Feu") else 0), 1.02, partie)
                if entité.salle is not joueur.salle:
                    modulo += 15
                if entité.effets.contient("Intoxication") and modulo == 1.02:
                    entité.effets.retirer("Intoxication")
                statistique.valeur = min(statistique.valeur // partie * partie + modulo, statistique.maximum)

class Statistique:
    """ Représente une Statistique d'une entité. """

    def __init__(self, maximum: int, division: int = 1, régénération: int = 0, valeur_départ: int = None):
        """ Statistique, int, int, int, int -> None """

        self.maximum = maximum
        self.division = division
        self.régénération = régénération

        if valeur_départ is not None:
            self.valeur = valeur_départ
        else:
            self.valeur = maximum

    def __repr__(self):
        """ Statistique -> str
        Renvoie une représentation de la statistique. """

        return f"{self.valeur}/{self.maximum} +{self.régénération}"

class Entité:
    """ Représente une entité quelquonque. """

    def __init__(self, nom: str, x: int, y: int, salle: Salle):
        """ Entité, str, int, int, Salle -> None """

        self.nom = nom

        self.x = x
        self.y = y

        self.salle = salle

        self.dx = 0
        self.dy = 0

        self.déplacement = False
        self.début_déplacement = 0.

        self.début_attaque = chronomètre.temps_écoulé()

        self.statistiques = GestionnaireStatistiques(self)
        self.enchantements = GestionnaireEnchantement()

        self.arme: Arme
        self.image: pygame.Surface

        if nom != "":
            self.initialiser_monde()
            self.initialiser_arme()

            if type(self) != PNJ:
                self.inventaire = FileInventaire(self.armes)
                self.arme: Arme = self.inventaire.tete()
            
            self.initialiser_image()
            self.initialiser_image_effets()

        self.effets = GestionnaireEffets()
    
    def initialiser_arme(self):
        """ Entité -> None
        Initialise l'arme de l'Entité `self`. """
        pass
    
    def initialiser_monde(self):
        """ Entité -> None
        Initialise le monde de l'Entité `self`. """
        pass

    def initialiser_image(self):
        """ Entité -> None
        Initialise l'image de l'Entité `self`. """
        pass

    def initialiser_image_effets(self):
        """ Entité -> None
        Initialise l'image des Effets de l'Entité `self`. """

        self.image_effets: dict[str, pygame.Surface] = {}

        for effet in effets:

            couleur = effets[effet]
        
            image_effet = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            image_effet.fill((couleur[0], couleur[1], couleur[2], 100))

            cache = pygame.mask.from_surface(self.image)
            surface_cache = cache.to_surface(setcolor=(couleur[0], couleur[1], couleur[2], 0), unsetcolor=(0, 0, 0, 0))

            image_effet.blit(surface_cache, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            self.image_effets[effet] = image_effet

    def afficher(self):
        """ Entité -> None
        Affiche l'Entité `self`. """

        if not est_visible(pygame.Rect(self.x * taille_case, self.y * taille_case, taille_case, taille_case)):
            return

        coordonnées = self.coordonnées_affichage()
        afficher_en_jeu(self.image, coordonnées)

        for effet in self.effets.contenu:
            autre_image = self.image.copy()
            autre_image.blit(self.image_effets[effet.nom], (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            
            afficher_en_jeu(autre_image, coordonnées)

    def afficher_barre_de_vie(self):
        """ Entité -> None
        Affiche la barre de vie de l'entité `self`. """

        progression = self.statistiques.vie.valeur / self.statistiques.vie.maximum

        if progression == 1:
            return
        
        barre_de_vie = pygame.Surface((taille_case * progression, taille_case / 6))
        if progression > 0.5:
            barre_de_vie.fill((255 - 255 * (progression - 0.5) * 2, 255, 0))
        else:
            barre_de_vie.fill((255, 255 * progression * 2, 0))

        x, y = self.coordonnées_affichage()

        afficher_en_jeu(barre_de_vie, (x, y - taille_case / 4))
    
    def déplacer(self):
        """ Entité -> None
        Déplace l'entité `self`. """

        if self.déplacement:
            if chronomètre.temps_écoulé() - self.début_déplacement >= 200 / self.statistiques.vitesse_déplacement.valeur:
                self.x += self.dx
                self.y += self.dy

                if type(self) is Joueur:
                    salle = donjon.récupérer(self.x // taille_salle, self.y // taille_salle)
                    self.salle = salle

                    global path
                    path = pathfinding()

                self.modification_case()
                self.changement_case()

                self.déplacement = False

                if self.effets.contient("Invocation"):
                    if random.randint(1, 7) == 1:
                        entités.ajouter_monstre(self.x // taille_salle, self.y // taille_salle, self.salle)

    def mettre_direction(self, dx: int, dy: int):
        """ Entité, int, int -> None
        Définit une direction pour l'Entité `self` à partir des directions `dx` et `dy`. """

        if not self.déplacement and chronomètre.temps_écoulé() - self.début_déplacement >= 200 / self.statistiques.vitesse_déplacement.valeur / (1.25 if self.effets.contient("Obscurite") else 1) / (1.25 if self.effets.contient("Feu") else 1) * (1.25 if self.effets.contient("Froid") else 1):

            if self.effets.contient("Liaison"):
                effet = self.effets.récupérer("Liaison")
                if distance((effet.attaquant.x, effet.attaquant.y), (self.x + dx, self.y + dy)) > 5:
                    return
            
            if self.effets.contient("Bloque"):
                return
            
            salle = donjon.récupérer((self.x + dx) // taille_salle, (self.y + dy) // taille_salle)

            if isinstance(self, Monstre) and salle != self.salle:
                return
            
            case = salle.récupérer((self.x + dx) % taille_salle, (self.y + dy) % taille_salle)

            if case is None or not case.collision or (liste_paramètres.recupérer_paramètre("noclip") and type(self) is Joueur):
                
                if not (liste_paramètres.recupérer_paramètre("noclip") and type(self) is Joueur) and entités.collision(self, dx, dy):
                    return

                self.dx = dx
                self.dy = dy

                self.déplacement = True
                self.début_déplacement = chronomètre.temps_écoulé()

                return
            
            if case is not None and case.ouvrable:
                case.ouvrir(salle.difficulté)
    
    def coordonnées_affichage(self):
        """ Entité -> (int, int)
        Renvoie les coordonnées d'affichage de l'entité `self`. """

        x = self.x
        if self.déplacement:
            x += self.dx * min(1, (chronomètre.temps_écoulé() - self.début_déplacement) * self.statistiques.vitesse_déplacement.valeur / 200)

        y = self.y
        if self.déplacement:
            y += self.dy * min(1, (chronomètre.temps_écoulé() - self.début_déplacement) * self.statistiques.vitesse_déplacement.valeur / 200)

        return (round(x * taille_case), round(y * taille_case))

    def attaquer(self, objectif_x: int, objectif_y: int):
        """ Entité, int, int -> None
        Ajoute une attaque à la liste global `attaques`. """

        centre_x, centre_y = self.arme.centre
        
        départ_x, départ_y = self.coordonnées_affichage()
        
        if self.arme.centrée_joueur:
            direction = math.atan2(objectif_y - départ_y, objectif_x - départ_x)
            dist = min(distance((objectif_x, objectif_y), (départ_x, départ_y)), 6 * taille_case)

            origine_x = départ_x + dist * math.cos(direction)
            origine_y = départ_y + dist * math.sin(direction)
        
        else:
            origine_x, origine_y = départ_x, départ_y
        
        direction_initiale = math.atan2(objectif_y - départ_y, objectif_x - départ_x)
        if self.effets.contient("Obscurite") and type(self) is not Joueur:
            if self.arme.centrée_joueur:
                objectif_x += random.uniform(-5 * taille_case, 5 * taille_case)
                objectif_y += random.uniform(-5 * taille_case, 5 * taille_case)
            else:
                direction_initiale = random.uniform(-math.pi, math.pi)

        sql: list[tuple[str, float]] = exécuter_sql(f"""SELECT EffetsArme.nom, EffetsArme.duree FROM EffetsArme JOIN Arme ON Arme.nom = EffetsArme.arme WHERE Arme.nom = '{self.arme.nom}';""")
        effets = {nom: duree for nom, duree in sql}

        if self.arme.puissance > 0:

            obstacle = False

            if self.arme.centrée_joueur:
                dist = distance((origine_x, origine_y), (départ_x, départ_y))

                for i in range(1, int(dist / taille_case) + 1):
                    x = round(départ_x / taille_case + i * math.cos(direction_initiale))
                    y = round(départ_y / taille_case + i * math.sin(direction_initiale))
                    
                    salle = donjon.récupérer(x // taille_salle, y // taille_salle)
                    case = salle.récupérer(x % taille_salle, y % taille_salle)

                    if case.collision:
                        obstacle = True
                        break

            if not obstacle:
                for case_x, case_y in self.arme.modèle:

                    direction = math.atan2(case_y - centre_y, case_x - centre_x)
                    dist = distance((case_x, case_y), (centre_x, centre_y))

                    for i in range(1, int(dist) + 1):
                        x = round(origine_x / taille_case + i * math.cos(direction_initiale + direction))
                        y = round(origine_y / taille_case + i * math.sin(direction_initiale + direction))

                        salle = donjon.récupérer(x // taille_salle, y // taille_salle)
                        case = salle.récupérer(x % taille_salle, y % taille_salle)

                        if case.collision:
                            break
                    
                    else:
                        x_final = round(origine_x / taille_case + dist * math.cos(direction_initiale + direction)) * taille_case
                        y_final = round(origine_y / taille_case + dist * math.sin(direction_initiale + direction)) * taille_case

                        if possède_améliorations(self.enchantements, [3, 2003, 1003]):
                            effets["Intoxication"] = max(effets.get("Intoxication",0), 2000 * nombre_améliorations(self.enchantements, [3, 2003, 1003]))
                        
                        if possède_améliorations(self.enchantements, [11]):
                            effets["Liaison"] = max(effets.get("Liaison",0), 2000)

                        if possède_améliorations(self.enchantements, [10]):
                            effets["Froid"] = max(effets.get("Froid",0), 2000)
                            
                        cout_critique = 1
                        chiffre = random.uniform(0,1)
                        if chiffre >= 1 - nombre_améliorations(self.enchantements, [1, 2001, 1001]) * 0.2 and type(self) is Joueur and possède_améliorations(self.enchantements, [1, 2001, 1001]):
                            cout_critique = 1.2
                        dégat = cout_critique * self.arme.puissance * self.statistiques.puissance_physique.valeur / 1000 * (1.25 if (isinstance(self, Monstre) and self.effets.contient("Obscurite")) else 1)
                        attaques.ajouter(Attaque(x_final, y_final, dégat, self.arme.durée, self.arme.attente, self.arme.monde, immunisés={type(self)}, effets=effets, attaquant=self))
                        if possède_amélioration(self.enchantements, 14):
                            attaques.ajouter(Attaque(x_final, y_final, dégat, self.arme.durée, self.arme.attente, self.arme.monde, immunisés={type(self)}, effets=effets, attaquant=self))
                        if liste_paramètres.recupérer_paramètre("show_number_damage"):
                            global affichage_dégat
                            dégat = cout_critique * self.arme.puissance * self.statistiques.puissance_physique.valeur / 1000 * (1.25 if (isinstance(self, Monstre) and self.effets.contient("Obscurite")) else 1)
                            affichage_dégat.append(Bouton("Mini",f"§{str(dégat)}§", color=(255*(cout_critique!=1),40**(cout_critique!=1),40**(cout_critique!=1)), center = (x_final, y_final),durées_états=[0.5, 1, 0.3, float("inf")]))

            if self.arme.centrée_joueur:
                direction_initiale = 0.

            particules.ajouter(Particule(int((origine_x + taille_case/2) / taille_case) * taille_case, int((origine_y + taille_case/2) / taille_case) * taille_case, self.arme.particule, self.arme.attente + self.arme.durée, direction=direction_initiale, nom_arme=self.arme.nom))

        for i in range(self.arme.projectiles):
            nom, vitesse = random.choice(exécuter_sql(f"""SELECT nom, vitesse FROM Projectile WHERE arme = '{self.arme.nom}';"""))
            projectiles.ajouter(Projectile(départ_x, départ_y, direction_initiale - math.pi/16 * (self.arme.projectiles - 1) + math.pi/8 * i, vitesse, nom, self.arme.monde, immunisés={type(self)}, attaquant=self))

        while len(self.salle.monstres) < self.arme.invocation:
            entités.ajouter_monstre(self.x // taille_salle, self.y // taille_salle, self.salle)
            
        self.début_attaque = chronomètre.temps_écoulé()
        
        if self.arme.nom != "Sel":
            jouer_son("Attaque")

    def modification_case(self):
        """ Entité -> None
        Modifie la case sur laquelle se trouve l'entité `self` si besoin. """

        case = self.salle.récupérer(self.x % taille_salle, self.y % taille_salle)

        if case is None:
            return

        sql: list[tuple[int, int]] = exécuter_sql(f"""SELECT depart, fin FROM ModificationCase WHERE type = '{case.type}';""")
        modifications = {départ: fin for départ, fin in sql}

        if case.numéro in modifications:
            case.numéro = modifications[case.numéro]
        
        case.initialiser_image()
    
    def changement_case(self):
        """ Entité -> None
        Change la case sur laquelle se trouve l'entité `self` si besoin. """

        case = self.salle.récupérer(self.x % taille_salle, self.y % taille_salle)

        if case is None:
            return

        sql: list[tuple[int]] = exécuter_sql(f"""SELECT fin FROM ChangementCase WHERE depart = '{case.type}';""")
        
        modifications = [fin[0] for fin in sql]

        if len(modifications):
            case.type = random.choice(modifications)
            case.numéro = case.numéro_case()
        
        case.initialiser_image()

    def est_vivant(self):
        """ Entité -> bool
        Détermine si l'entité `self` a une vie strictement positive. """

        return self.statistiques.vie.valeur > 0
    
    def calculer_déplacement(self):
        """ Entité -> None
        Gère le déplacement de l'entité `self`. """
        pass

    def calculer_attaque(self):
        """ Monstre -> None
        Gère l'attaque du Monstre `self`. """
        pass

class GestionnaireEntités:
    """ Gère la liste des Entités """

    def __init__(self):
        """ GestionnaireEntités -> None """

        self.contenu: list[Entité] = []

        for x in range(taille_donjon):
            for y in range(taille_donjon):
                salle = donjon.récupérer(x, y)
                if salle.boss:
                    self.ajouter_monstre(x, y, salle, boss=True)
                elif salle.est_dangereuse():
                    for _ in range(math.ceil(salle.difficulté / 2)):
                        self.ajouter_monstre(x, y, salle)
                else:
                    self.ajouter_joueur(x, y, salle)
                    self.ajouter_pnj(x, y, salle)
        
        self.modification_cases()

    def modification_cases(self):
        """ GestionnaireEntités -> None
        Modifie la case sur laquelle se trouve chaque entité si besoin. """

        for entité in self.contenu:
            entité.modification_case()
            entité.changement_case()
    
    def ajouter_joueur(self, x: int, y: int, salle: Salle):
        """ GestionnaireEntités, int, int, Salle -> None
        Ajoute le joueur global à la liste `self.contenu` en ajustant certains de ses attributs. """

        joueur.x = taille_salle // 2 + x * taille_salle
        joueur.y = taille_salle // 2 + y * taille_salle
        joueur.salle = salle

        self.contenu.append(joueur)
    
    def ajouter_pnj(self, x: int, y: int, salle: Salle):
        """ GestionnaireEntités, int, int, Salle -> None
        Ajoute un PNJ à la liste `self.contenu`. """

        sql = exécuter_sql(f"""SELECT Personnage.nom FROM Personnage JOIN MondePersonnage ON MondePersonnage.personnage = Personnage.nom WHERE MondePersonnage.monde = '{monde}' AND Personnage.nom != '{joueur.nom}';""")

        if not len(sql):
            return

        pnj = PNJ(random.choice(sql)[0], x * taille_salle + 1, y * taille_salle + 1, salle)

        self.contenu.append(pnj)
        salle.monstres.append(pnj)
    
    def ajouter_monstre(self, x: int, y: int, salle: Salle, boss: bool = False):
        """ GestionnaireEntités, int, int, Salle, bool -> None
        Ajoute un monstre à la liste `self.contenu` et à sa salle respective. """

        if boss:
            if monde == "Parcoursup":

                monstre = PNJ("M.Picard", x * taille_salle + taille_salle//2, y * taille_salle + taille_salle//2, salle)
            
            else:

                sql = exécuter_sql(f"""SELECT personnage FROM MondePersonnage WHERE monde = '{monde}';""")

                monstre = Boss(random.choice(sql)[0], x * taille_salle + taille_salle//2, y * taille_salle + taille_salle//2, salle)
        
        else:
            sql = exécuter_sql(f"""SELECT monstre FROM MondeMonstre{f" WHERE monde = '{monde}'" if monde != "Parcoursup" else ""};""")

            if not len(sql):
                return

            monstre = Monstre(random.choice(sql)[0], x * taille_salle + random.randint(1, taille_salle - 2), y * taille_salle + random.randint(1, taille_salle - 2), salle)

        self.contenu.append(monstre)
        salle.monstres.append(monstre)

    def déplacement(self):
        """ GestionnaireEntités -> None
        Gère le déplacement des Entités. """

        for entité in self.contenu:
            if not est_visible(pygame.Rect(entité.x * taille_case, entité.y * taille_case, taille_case, taille_case), produit=1.5):
                continue
            
            entité.calculer_déplacement()
            
            entité.déplacer()

            if type(entité) is Joueur:
                case = entité.salle.récupérer(entité.x % taille_salle, entité.y % taille_salle)

                if case is not None and case.sortie:
                    global actualiser_nouvelle_scène, scène, difficulté_monde

                    partie = joueur.statistiques.vie.maximum / joueur.statistiques.vie.division
                    joueur.statistiques.vie.valeur = min((joueur.statistiques.vie.valeur - 1.02) // partie * partie + 2 * partie, joueur.statistiques.vie.maximum)
                    
                    difficulté_monde += entité.salle.difficulté
                    actualiser_nouvelle_scène, scène = False, "Partie"
                    return

                if entité.salle.boss and not entité.salle.combat_boss:
                    entité.salle.combat_boss = True

                    entité.salle.fermer(haut=True, gauche=True)

                    salle = donjon.récupérer(entité.x // taille_salle + 1, entité.y // taille_salle)
                    if not salle.composition.bordure:
                        salle.fermer(gauche=True)
                    
                    salle = donjon.récupérer(entité.x // taille_salle, entité.y // taille_salle + 1)
                    if not salle.composition.bordure:
                        salle.fermer(haut=True)
                    
                    joueur.x = compression(joueur.x, joueur.x // taille_salle * taille_salle + 1, (joueur.x // taille_salle + 1) * taille_salle - 2)
                    joueur.y = compression(joueur.y, joueur.y // taille_salle * taille_salle + 1, (joueur.y // taille_salle + 1) * taille_salle - 2)
                    
                    if monde == "Parcoursup":
                        jouer_musique("")
                    else:
                        jouer_musique("Boss")
    
    def attaquer(self):
        """ GestionnaireEntités -> None
        Fait attaquer chaque Entité de la liste `self.contenu`. """
        
        import_randoms: list[Arme] = []

        for entité in self.contenu:
            if entité.salle.est_visible(entité.x // taille_salle, entité.y // taille_salle):
                if type(entité) is not PNJ and entité.arme.nom == "import random":
                    entité.arme.nom = random.choice(exécuter_sql(f"""SELECT nom FROM Arme;"""))[0]

                    entité.arme.modèle = exécuter_sql(f"""SELECT CasesViseesArme.x, CasesViseesArme.y FROM CasesViseesArme JOIN Arme ON Arme.nom = CasesViseesArme.arme WHERE Arme.nom = '{entité.arme.nom}';""")

                    centre_x, centre_y, centree_joueur, puissance, duree, attente, vitesse, projectiles, invocation = exécuter_sql(f"""SELECT centre_x, centre_y, centree_joueur, puissance, duree, attente, vitesse, projectiles, invocation FROM Arme WHERE nom = '{entité.arme.nom}';""")[0]
                    
                    entité.arme.centre = centre_x, centre_y
                    entité.arme.centrée_joueur = bool(centree_joueur)
                    entité.arme.puissance = puissance
                    entité.arme.durée = duree
                    entité.arme.attente = attente
                    entité.arme.vitesse = vitesse
                    entité.arme.projectiles = projectiles
                    entité.arme.invocation = invocation

                    import_randoms.append(entité.arme)

                entité.calculer_attaque()
        
        for import_random in import_randoms:
            import_random.nom = "import random"

    def dégâts(self):
        """ GestionnaireEntités -> None
        Gère les dégâts subits par chaque Entité de la liste `self.contenu`. """
        
        for entité in self.contenu:
            if type(entité) is PNJ and entité.nom == "M.Picard":
                continue

            if entité.salle.est_visible(entité.x // taille_salle, entité.y // taille_salle):
                for attaque in attaques.contenu:

                    if attaque.dangereuse():

                        if not (any([isinstance(entité, immunisé) for immunisé in attaque.immunisés]) or (type(entité) is Joueur and liste_paramètres.recupérer_paramètre("godmode"))) and entité.image.get_rect(topleft=entité.coordonnées_affichage()).colliderect(pygame.Rect((attaque.x, attaque.y), (taille_case, taille_case))):
                            
                            global projectiles
                            if possède_amélioration(entité.enchantements, 18):
                                if liste_paramètres.recupérer_paramètre("game_quality")!=2:
                                    for i in range(8):
                                        projectiles.ajouter(Projectile(entité.x * taille_case,entité.y * taille_case,i/8 * 2*math.pi, 25, "Pic", attaque.monde, {type(entité)}, attaquant=entité))
                                else:
                                    for i in range(32):
                                        projectiles.ajouter(Projectile(entité.x * taille_case,entité.y * taille_case,i/32 * 2*math.pi, 25, "Pic2", attaque.monde, {type(entité)}, attaquant=entité))

                            entité.statistiques.vie.valeur -= round(attaque.puissance / horloge.get_fps()) * intéraction(attaque.monde, entité.monde) * (1.25 if (isinstance(self, Monstre) and self.effets.contient("Obscurite")) else 1)

                            if intéraction(attaque.monde, entité.monde) >= 1:
                                for nom in attaque.effets:
                                    entité.effets.ajouter(Effet(nom, attaque.effets[nom], attaquant=attaque.attaquant))

                                    if nom == "Liaison":
                                        attaque.attaquant.effets.ajouter(Effet(nom, attaque.effets[nom], attaquant=entité))
                            
                            if possède_améliorations(attaque.attaquant.enchantements, [2, 1002, 2002]):
                                attaque.attaquant.statistiques.vie.valeur = min(attaque.attaquant.statistiques.vie.maximum, attaque.attaquant.statistiques.vie.valeur + round(attaque.puissance / horloge.get_fps()) * intéraction(attaque.monde, entité.monde) * (1.25 if (isinstance(self, Monstre) and self.effets.contient("Obscurite")) else 1) * 0.07 * nombre_améliorations(attaque.attaquant.enchantements, [2, 1002, 2002]))
                            jouer_son("Dégât")
                
            entité.statistiques.actualiser(entité)

    def effets(self):
        """ GestionnaireEntités -> None
        Gère les effets subits par chaque Entité de la liste `self.contenu`. """
        
        for entité in self.contenu:
            for effet in entité.effets.contenu:
                if effet.nom == "Echange":
                    entité.x, effet.attaquant.x = effet.attaquant.x, entité.x
                    entité.y, effet.attaquant.y = effet.attaquant.y, entité.y

                    entité.dx = 0
                    entité.dy = 0
                    effet.attaquant.dx = 0
                    effet.attaquant.dy = 0

                    entité.salle, effet.attaquant.salle = effet.attaquant.salle, entité.salle
                
                elif effet.nom == "Gravite":
                    direction = math.atan2(effet.attaquant.y - entité.y, effet.attaquant.x - entité.x)

                    entité.x = round(entité.x + math.cos(direction))
                    entité.y = round(entité.y + math.sin(direction))

            entité.effets.supprimer()
    
    def afficher_effets(self):
        """ GestionnaireEntités -> None
        Affiche chaque Effet de chaque Entité de la liste `self.contenu`. """
        
        for entité in self.contenu:
            for effet in entité.effets.contenu:
                effet.afficher(entité)

    def supprimer_entités(self):
        """ GestionnaireEntités -> None
        Supprime les Entités qui n'ont plus de vie, sauf les PNJ. """
        
        self.contenu = []

        for x in range(taille_donjon):
            for y in range(taille_donjon):
                salle = donjon.récupérer(x, y)

                if salle.est_dangereuse():

                    for i, monstre in enumerate(salle.monstres):
                        if monstre.est_vivant():
                            self.contenu.append(monstre)
                        else:
                            if monstre.effets.contient("Liaison"):
                                monstre.effets.récupérer("Liaison").attaquant.effets.retirer("Liaison", attaquant=monstre)
                            
                            if type(monstre) is Boss:
                                salle.boss = False

                                sortie_par_défaut: str = exécuter_sql(f"""SELECT sortie_par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};""")[0][0]
                                salle.placer(taille_salle // 2, taille_salle // 2, Case(sortie_par_défaut), hauteur=0)

                                if monde == "Parcoursup":
                                    jouer_musique("")
                                else:
                                    jouer_musique("Donjon")
                                
                                salle.ouvrir(haut=True, gauche=True)
                                donjon.récupérer(x + 1, y).ouvrir(gauche=True)
                                donjon.récupérer(x, y + 1).ouvrir(haut=True)

                                salle.monstres = []

                                global gold
                                gold += 3+joueur.enchantements.possède_enchant(4)*1
                                break
                            
                            gold += 1+joueur.enchantements.possède_enchant(4)*0.2
                            del salle.monstres[i]

                            jouer_son("Destruction")
                
                else:

                    for i, pnj in enumerate(salle.monstres):
                        if pnj.est_vivant():
                            self.contenu.append(pnj)
                        else:
                            if pnj.effets.contient("Liaison"):
                                pnj.effets.récupérer("Liaison").attaquant.effets.retirer("Liaison", attaquant=pnj)
                            del salle.monstres[i]

        if joueur.est_vivant():
            self.contenu.append(joueur)
        else:
            global surcis
            if not joueur.enchantements.possède_enchant(37) or not surcis:
                while joueur.effets.contient("Liaison"):
                    attaquant = joueur.effets.récupérer("Liaison").attaquant
                    attaquant.effets.retirer("Liaison", joueur)
                    joueur.effets.retirer("Liaison", attaquant)

                global scène
                if scène == "Niveau":
                    scène = "Mort"
            else:
                joueur.statistiques.vie.valeur = joueur.statistiques.vie.maximum
                jouer_son("Totem")
                surcis = False
                while joueur.effets.contient("Liaison"):
                    attaquant = joueur.effets.récupérer("Liaison").attaquant
                    attaquant.effets.retirer("Liaison", joueur)
                    joueur.effets.retirer("Liaison", attaquant)
    
    def ajouter_récompense(self):
        """ GestionnaireEntités -> None
        Ajoute les récompenses dans les salles libérées s'il n'y a pas d'entité qui gêne. """

        for x in range(taille_donjon):
            for y in range(taille_donjon):
                salle = donjon.récupérer(x, y)
                if salle.boss or salle.combat_boss:
                    continue
                if salle.est_dangereuse() and salle.est_libérée():
                    coffre_x = taille_salle//2
                    coffre_y = taille_salle//2

                    if not self.collision(Entité("", coffre_x + x * taille_salle, coffre_y + y * taille_salle, salle), 0, 0):
                        récompenses = ["coffre", "epee_rocher", "fontaine", "enclume"]
                        probas = [5 - joueur.inventaire.longueur(), 4, (joueur.statistiques.vie.maximum - joueur.statistiques.vie.valeur) / (joueur.statistiques.vie.maximum / joueur.statistiques.vie.division) * 4/3 * (1 + joueur.enchantements.possède_enchant(35)), 3 * joueur.enchantements.possède_enchant(34)]

                        récompense = random.choices(récompenses, probas)[0]
                        récompense_par_défaut: str = exécuter_sql(f"""SELECT {récompense}_par_defaut FROM Monde{f" WHERE nom = '{monde}'" if monde != "Parcoursup" else ""};""")[0][0]
                        salle.placer(coffre_x, coffre_y, Case(récompense_par_défaut))

                        salle.libérée = True

    def collision(self, entité: Entité, dx: int, dy: int):
        """ GestionnaireEntités, Entité, int, int -> bool
        Détermine si une autre entité se trouve là où l'`entité` veut aller. """
        
        for i, autre_entité in enumerate(self.contenu):
            if autre_entité is entité:
                continue
            
            if autre_entité.x == entité.x + dx and autre_entité.y == entité.y + dy:
                if type(autre_entité) is PNJ and type(entité) is Joueur:
                    global scène
                    if autre_entité.nom == "M.Picard":

                        del self.contenu[i]

                        monstre = Boss("M.Picard", joueur.x // taille_salle * taille_salle + taille_salle//2, joueur.y // taille_salle * taille_salle + taille_salle//2, joueur.salle)
                        self.contenu.append(monstre)
                        joueur.salle.monstres = [monstre]

                        chronomètre.pause()
                        scène = "Monologue"
                    else:
                        données_scène_suivante["pnj"] = autre_entité.nom
                        scène = "Dialogue"
                return True
            
            if autre_entité.déplacement and autre_entité.x + autre_entité.dx == entité.x + dx and autre_entité.y + autre_entité.dy == entité.y + dy:
                return True
        
        return False
    
    def afficher(self):
        """ GestionnaireEntités -> None
        Affiche chaque Entité de la liste `self.contenu`. """

        for entité in self.contenu:
            if liste_paramètres.recupérer_paramètre("visionIR") or entité.salle.est_visible(entité.x // taille_salle, entité.y // taille_salle):
                entité.afficher()
    
    def afficher_barre_de_vie(self):
        """ GestionnaireEntités -> None
        Affiche la barre de vie de chaque Entités de la liste `self.contenu`. """

        for entité in self.contenu:
            if liste_paramètres.recupérer_paramètre("visionIR") or entité.salle.est_visible(entité.x // taille_salle, entité.y // taille_salle):
                entité.afficher_barre_de_vie()

class Monstre(Entité):
    """Représente un Monstre. """
    
    def initialiser_arme(self):
        """ Monstre -> None
        Initialise l'arme du Monstre `self`. """
        
        sql: list[tuple[str, int]] = exécuter_sql(f"""SELECT arme, coefficient FROM ArmeMonstre JOIN MondeMonstre ON MondeMonstre.monstre = ArmeMonstre.monstre WHERE{f" MondeMonstre.monde = '{monde}' AND" if monde != "Parcoursup" and not joueur.enchantements.possède_enchant(12) else ""} ArmeMonstre.monstre = '{self.nom}';""")
        
        armes = [arme for arme, coefficient in sql]
        coefficients = [coefficient**(1 + 2*joueur.enchantements.possède_enchant(36)) for arme, coefficient in sql]
        self.armes: list[Arme] = []
        while True:
            arme = random.choices(armes, coefficients)[0]
            i = armes.index(arme)

            del armes[i]
            del coefficients[i]

            self.armes.append(Arme(arme))

            if not len(armes) or (random.randint(0, 9) > 0):
                break
    
    def initialiser_monde(self):
        """ Monstre -> None
        Initialise le monde du Monstre `self`. """
        
        self.monde: list[str] = [monde[0] for monde in exécuter_sql(f"""SELECT monde FROM MondeMonstre WHERE monstre = '{self.nom}';""")]

    def initialiser_image(self):
        """ Monstre -> None
        Initialise l'image du monstre. """

        self.image = charger_image(f"Entités/Monstres/{self.nom}", taille_case, taille_case)

    def calculer_déplacement(self):
        """ Entité -> None
        Gère le déplacement du monstre `self`. """

        if not (self.effets.contient("Obscurite") or self.effets.contient("Feu") or self.effets.contient("Recul")) and random.randint(1, 10) <= 8:
            return

        if self.effets.contient("Recul"):
            attaquant = self.effets.récupérer("Recul").attaquant
            direction = round(math.atan2(self.y - attaquant.y, self.x - attaquant.x) / (math.pi/2)) * (math.pi/2)
            dx = round(math.cos(direction))
            dy = round(math.sin(direction))
        
        else:
            if self.salle is joueur.salle:
                direction = path.récupérer(self.x % taille_salle, self.y % taille_salle)
                if direction is not None and random.randint(0, 3 if self.effets.contient("Feu") else 9):
                    dx = direction[0]
                    dy = direction[1]
                    if self.arme.puissance == 0 and distance((joueur.x, joueur.y), (self.x, self.y)) < 5:
                        dx = -dx
                        dy = -dy
                else:
                    dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            else:
                dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        self.mettre_direction(dx, dy)

    def calculer_attaque(self):
        """ Monstre -> None
        Gère l'attaque du Monstre `self`. """

        if type(self) is Boss and joueur.salle != self.salle:
            return

        if chronomètre.temps_écoulé() - self.début_attaque >= 30000 / self.statistiques.vitesse_physique.valeur / self.arme.vitesse / (1.25 if self.effets.contient("Obscurite") else 1) * (1.25 if self.effets.contient("Froid") else 1):

            joueur_x, joueur_y = joueur.coordonnées_affichage()

            if not self.salle.est_visible(self.x // taille_salle, self.y // taille_salle):
                return

            if  (self.effets.contient("Obscurite") or self.arme.nom == "Sel") or ((self.arme.puissance == 0 or self.joueur_à_portée()) and distance(self.coordonnées_affichage(), (joueur_x, joueur_y)) <= 6 * taille_case):
                self.attaquer(joueur_x, joueur_y)
                self.inventaire.enfiler(self.inventaire.defiler())
                self.arme = self.inventaire.tete()
    
    def joueur_à_portée(self):
        """ Monstre -> bool
        Détermine si le joueur global est à portée d'attaque du Monstre `self`. """
        
        if self.arme.centrée_joueur:
            x, y = joueur.coordonnées_affichage()
        else:
            x, y = self.coordonnées_affichage()

        joueur_x, joueur_y = joueur.coordonnées_affichage()

        centre = self.arme.centre

        x_arrondi = round(x / taille_case)
        y_arrondi = round(y / taille_case)
        
        direction_initiale = math.atan2(joueur_y - y, joueur_x - x)

        for case_x, case_y in self.arme.modèle:
            direction = math.atan2(case_y - centre[1], case_x - centre[0])
            dist = distance((case_x, case_y), centre)
            if joueur_x == round((x_arrondi + dist * math.cos(direction_initiale + direction)) * taille_case) and joueur_y == round((y_arrondi + dist * math.sin(direction_initiale + direction)) * taille_case):
                return True
        return False

class Boss(Monstre):
    """Représente un Boss. """

    def initialiser_image(self):
        """ Boss -> None
        Initialise l'image du Boss `self`. """

        self.image = charger_image(f"Entités/Personnages/{self.nom}", taille_case, taille_case)
    
    def initialiser_arme(self):
        """ Boss -> None
        Initialise l'arme du Boss `self`. """

        self.armes: list[Arme] = []

        sql = exécuter_sql(f"""SELECT ArmePersonnage.arme FROM ArmePersonnage JOIN Personnage ON Personnage.nom = ArmePersonnage.personnage WHERE Personnage.nom = '{self.nom}';""")

        if len(sql):
            self.armes.append(Arme(random.choice(sql)[0]))
        
        sql: list[tuple[str, int]] = exécuter_sql(f"""SELECT arme, coefficient FROM ArmeMonstre JOIN MondeMonstre ON MondeMonstre.monstre = ArmeMonstre.monstre{f" WHERE MondeMonstre.monde = '{monde}'" if monde != "Parcoursup" else ""};""")
        armes = [arme for arme, coefficient in sql]
        coefficients = [coefficient for arme, coefficient in sql]
        
        while True:
            arme = random.choices(armes, coefficients)[0]

            self.armes.append(Arme(arme))

            if not len(armes) or (random.randint(0, 3) > 2):
                break
        
        self.armes.append(Arme("InvocationBoss"))

class Joueur(Entité):
    """ Représente un Joueur. """
    
    def initialiser_arme(self):
        """ Joueur -> None
        Initialise l'arme du Joueur `self`. """

        sql = exécuter_sql(f"""SELECT ArmePersonnage.arme FROM ArmePersonnage JOIN Personnage ON Personnage.nom = ArmePersonnage.personnage WHERE Personnage.nom = '{self.nom}';""")

        if len(sql):
            self.armes = [Arme(random.choice(sql)[0])]
        
        else:
            armes: list[tuple[str]] = []

            for monde_personnage in self.monde:
                armes.extend(exécuter_sql(f"""SELECT arme FROM MondeArme WHERE monde = '{monde_personnage}';"""))
            
            arme = Arme(random.choice(armes)[0])
            while exécuter_sql(f"""SELECT COUNT(*) FROM Projectile WHERE nom = '{arme.nom}';""")[0][0] > 0:
                arme = Arme(random.choice(armes)[0])
            
            self.armes = [arme]
        
        # self.armes = [Arme("Explosion")]
    
    def initialiser_monde(self):
        """ Joueur -> None
        Initialise le monde du Joueur `self`. """
        
        self.monde: list[str] = [monde[0] for monde in exécuter_sql(f"""SELECT monde FROM MondePersonnage WHERE personnage = '{self.nom}';""")]

    def initialiser_image(self):
        """ Joueur -> None
        Initialise l'image du joueur. """

        self.image = charger_image(f"Entités/Personnages/{self.nom}", taille_case, taille_case)

        self.contour_barre_de_vie = pygame.Surface((int(taille_fenêtre / 3 + taille_fenêtre // 60), int(taille_fenêtre / 25 + taille_fenêtre // 60)))
        self.contour_barre_de_vie.fill((255, 255, 255))

        fond_barre_de_vie = pygame.Surface((int(taille_fenêtre / 3), int(taille_fenêtre / 25)))
        fond_barre_de_vie.fill((63, 63, 63))

        self.contour_barre_de_vie.blit(fond_barre_de_vie, (taille_fenêtre // 120, taille_fenêtre // 120))

        self.contour = ajouter_cadre()

    def afficher_barre_de_vie(self):
        """ Joueur -> None
        Affiche la barre de vie du joueur `self`. """

        progression = self.statistiques.vie.valeur / self.statistiques.vie.maximum

        barre_de_vie = pygame.Surface((int(taille_fenêtre / 3 * progression), int(taille_fenêtre / 25)))

        if progression > 0.5:
            barre_de_vie.fill((255 - 255 * (progression - 0.5) * 2, 255, 0))
        else:
            barre_de_vie.fill((255, 255 * progression * 2, 0))

        if self.statistiques.vie.valeur % (self.statistiques.vie.maximum / self.statistiques.vie.division) < 0.1:
            progression = 0
        else:
            progression = (self.statistiques.vie.valeur // (self.statistiques.vie.maximum / self.statistiques.vie.division) + 1) / self.statistiques.vie.division

        fond_barre_de_vie = pygame.Surface((int(taille_fenêtre / 3 * progression), int(taille_fenêtre / 25)))
        fond_barre_de_vie.fill((127, 127, 127))

        afficher(self.contour_barre_de_vie, (int(2*(taille_fenêtre / 25 + taille_fenêtre // 60)), int(taille_fenêtre / 50 + taille_fenêtre // 120)))

        afficher(fond_barre_de_vie, (int(2*(taille_fenêtre / 25 + taille_fenêtre // 60)) + taille_fenêtre // 120, int(taille_fenêtre / 50 + taille_fenêtre // 60)))

        afficher(barre_de_vie, (int(2*(taille_fenêtre / 25 + taille_fenêtre // 60)) + taille_fenêtre // 120, int(taille_fenêtre / 50 + taille_fenêtre // 60)))

        afficher(self.contour, (taille_fenêtre // 120, taille_fenêtre // 120))

        afficher(self.arme.icône, (taille_fenêtre // 40, taille_fenêtre // 40))
        
        global gold 
        affichage_gold = f'§{int(gold)}g§'
        if liste_paramètres.recupérer_paramètre("infgold"):
            affichage_gold = f'§{int(gold)}g | inf§'
        b = Bouton("Moyen",affichage_gold, color=(240,200,20), midleft=(taille_fenêtre//8,taille_fenêtre//8.25))
        b.afficher()

    def calculer_déplacement(self):
        """ Entité -> None
        Gère le déplacement du joueur. """

        if self.effets.contient("Recul") or any([liste_paramètres.touché_pressé_clavier("déplacement_devant"), liste_paramètres.touché_pressé_clavier("déplacement_arrière"), liste_paramètres.touché_pressé_clavier("déplacement_gauche"), liste_paramètres.touché_pressé_clavier("déplacement_droite")]):
            
            if self.effets.contient("Recul"):
                attaquant = self.effets.récupérer("Recul").attaquant
                direction = round(math.atan2(self.y - attaquant.y, self.x - attaquant.x) / (math.pi/2)) * (math.pi/2)
                dx = round(math.cos(direction))
                dy = round(math.sin(direction))
            
            else:
                dx = liste_paramètres.touché_pressé_clavier("déplacement_droite") - liste_paramètres.touché_pressé_clavier("déplacement_gauche")
                if dx == 0:
                    dy = liste_paramètres.touché_pressé_clavier("déplacement_arrière") - liste_paramètres.touché_pressé_clavier("déplacement_devant")
                else:
                    dy = 0

            self.mettre_direction(dx, dy)

    def calculer_attaque(self):
        """ Joueur -> None
        Gère l'attaque du Joueur `self`. """

        if souris_pressée and chronomètre.temps_écoulé() - self.début_attaque >= 30000 / self.statistiques.vitesse_physique.valeur / self.arme.vitesse:

            if self.arme.nom == "Soin" and self.inventaire.longueur() > 1:
                partie = self.statistiques.vie.maximum / self.statistiques.vie.division
                self.statistiques.vie.valeur = min((self.statistiques.vie.valeur - 1.02) // partie * partie + 2 * partie, self.statistiques.vie.maximum)
                
                self.inventaire.defiler()
                self.arme = self.inventaire.tete()
            
            elif self.arme.nom == "Cadeau":
                self.inventaire.defiler()

                armes = exécuter_sql(f"""SELECT nom FROM Arme""")

                arme = random.choice(armes)[0]
                while exécuter_sql(f"""SELECT COUNT(*) FROM Projectile WHERE nom = '{arme}';""")[0][0] > 0:
                    arme = random.choice(armes)[0]

                self.inventaire.enfiler(Arme(arme))

                self.arme = self.inventaire.tete()

            position_souris_en_jeu = coordonnées_réelles(position_souris[0] - marge, position_souris[1])

            self.attaquer(position_souris_en_jeu[0] - taille_case/2, position_souris_en_jeu[1] - taille_case/2,)

class PNJ(Entité):
    """ Représente un Personnage Non Joueur """
    
    def initialiser_monde(self):
        """ Monstre -> None
        Initialise le monde du Monstre `self`. """
        
        self.monde: list[str] = [monde[0] for monde in exécuter_sql(f"""SELECT monde FROM MondePersonnage WHERE personnage = '{self.nom}';""")]

    def initialiser_image(self):
        """ Joueur -> None
        Initialise l'image du joueur. """

        self.image = charger_image(f"Entités/Personnages/{self.nom}", taille_case, taille_case)

class Projectile:
    """ Représente un projectile créé par une Entité. """

    def __init__(self, x: int, y: int, direction: float, vitesse: int, nom: str, monde_arme: list[str], immunisés: set[type] = {}, effets: dict[str, float] = {}, attaquant: Entité = None):
        """ Projectile, int, int, float, int, str, [str], {type}, {str: float}, Entité -> None """

        self.x = x
        self.y = y

        self.x_départ = x
        self.y_départ = y

        self.direction = direction
        self.vitesse = vitesse
        self.nom = nom
        self.monde = monde_arme
        self.immunisés = immunisés
        self.attaquant = attaquant

        puissance, duree, attente = exécuter_sql(f"""SELECT puissance, duree, attente FROM Arme WHERE nom = '{nom}';""")[0]
        self.puissance: int = puissance
        self.durée: float = duree
        self.attente: float = attente

        self.début_attaque = chronomètre.temps_écoulé()

        sql: list[tuple[str, float]] = exécuter_sql(f"""SELECT nom, duree FROM EffetsArme WHERE arme = '{self.nom}';""")
        self.effets = {nom: duree for nom, duree in sql}

        self.particule = charger_image(f"Armes/Particules/{self.nom}", changement_taille=False)
    
    def avancer(self):
        """ Projectile -> bool
        Fait avancer le Projectile `self`.
        Détermine s'il entre en collision avec une case. """

        self.x += math.cos(self.direction) * self.vitesse
        self.y += math.sin(self.direction) * self.vitesse

        return self.collision()

    def collision(self):
        """ Projectile -> bool
        Détermine si le Projectile `self` entre en collision avec une case. """

        salle = donjon.récupérer(round(self.x / taille_case) // taille_salle, round(self.y / taille_case) // taille_salle)        
        case = salle.récupérer(round(self.x / taille_case) % taille_salle, round(self.y / taille_case) % taille_salle)

        return case is not None and case.collision

    def attaquer(self):
        """ Projectile -> None
        Ajoute une Attaque à l'emplacement du Projectile `self`. """

        if possède_amélioration(self.attaquant.enchantements, 17):
            self.effets["Feu"] = max(self.effets.get("Feu",0), 1)

        if possède_améliorations(self.attaquant.enchantements, [3, 2003, 1003]):
            self.effets["Intoxication"] = max(self.effets.get("Intoxication",0), 2000 * nombre_améliorations(self.attaquant.enchantements, [3, 2003, 1003]))
                        
        if possède_améliorations(self.attaquant.enchantements, [11]):
            self.effets["Liaison"] = max(self.effets.get("Liaison",0), 2000)

        if possède_améliorations(self.attaquant.enchantements, [10]):
            self.effets["Froid"] = max(self.effets.get("Froid",0), 2000)

        if chronomètre.temps_écoulé() - self.début_attaque >= self.durée:
            
            attaques.ajouter(Attaque(round(self.x / taille_case) * taille_case, round(self.y / taille_case) * taille_case, self.puissance * max(1,joueur.enchantements.possède_enchant(17)*distance((self.x, self.y),(self.x_départ,self.y_départ))/3), self.durée, self.attente, self.monde, immunisés=self.immunisés, effets=self.effets, attaquant=self.attaquant))

            particules.ajouter(Particule(self.x, self.y, self.particule, self.durée, direction=self.direction, nom_arme=self.nom))
            
            self.début_attaque = chronomètre.temps_écoulé()

class GestionnaireProjectiles:
    """ Gère la liste des Projectiles. """

    def __init__(self):
        """ GestionnaireProjectiles -> None """

        self.contenu: list[Projectile] = []
    
    def ajouter(self, projectile: Projectile):
        """ GestionnaireProjectiles, Projectile -> None
        Ajoute un Projectile `donné` à la liste `self.contenu`. """

        self.contenu.append(projectile)
    
    def avancer(self):
        """ GestionnaireProjectiles -> None """

        for i, projectile in enumerate(self.contenu):
            if projectile.avancer():
                del self.contenu[i]
                jouer_son("Destruction")
    
    def attaquer(self):
        """ GestionnaireProjectiles -> None """

        for projectile in self.contenu:
            projectile.attaquer()

class Effet:
    """ Représente un effet qu'une Entité peut avoir. """

    def __init__(self, nom: str, durée: float, attaquant: Entité = None):
        """ Effet, str, float, Entité -> None """

        self.nom = nom
        self.durée = durée
        self.attaquant = attaquant
        
        self.début = chronomètre.temps_écoulé()

    def initialiser_image(self):
        """ Effet -> None
        Initialise l'image de l'Effet `self`. """

        if self.nom == "Liaison":
            self.image = charger_image(f"Effets/Liaison", taille_case * 5, taille_case)
    
    def afficher(self, entité: Entité):
        """ Effet, Entité -> None
        Affiche l'Effet `self`. """

        if self.nom == "Liaison":

            entité_x, entité_y = entité.coordonnées_affichage()
            entité_x, entité_y = coordonnées_en_jeu(entité_x + taille_case//2, entité_y + taille_case//2)

            attaquant_x, attaquant_y = self.attaquant.coordonnées_affichage()
            attaquant_x, attaquant_y = coordonnées_en_jeu(attaquant_x + taille_case//2, attaquant_y + taille_case//2)

            global marge
            pygame.draw.line(fenêtre, (103, 141, 212), (marge + round(entité_x), round(entité_y)), (marge + round(attaquant_x), round(attaquant_y)), width=round(20 * caméra.zoom))
    
    def est_active(self):
        """ Effet -> bool
        Détermine si l'Effet `self` est encore actif. """

        return chronomètre.temps_écoulé() - self.début < self.durée
    
    @property
    def temps_restant(self):
        """ Effet -> float
        Renvoie le temps restant avant la fin de l'Effet `self`. """

        return self.durée - (chronomètre.temps_écoulé() - self.début)
    
    def __repr__(self):
        """ Effet -> str
        Renvoie une chaîne de charactères représentant l'Effet `self`. """

        return f"Effet({self.nom, self.temps_restant, self.attaquant})"

class GestionnaireEffets:
    """ Gère la liste des Effets d'une Entité. """

    def __init__(self):
        """ GestionnaireEffets -> None """

        self.contenu: list[Effet] = []
    
    def ajouter(self, effet: Effet):
        """ GestionnaireEffets, Effet -> None
        Ajoute l'`effet` donné à la liste `self.contenu`. """

        if self.contient(effet.nom) and effet != "Liaison":
            self.récupérer(effet.nom).durée = effet.durée
        else:
            self.contenu.append(effet)
            
            jouer_son("Effet")
    
    def supprimer(self):
        """ GestionnaireEffets -> None
        Supprime chaque Effet de la liste `self.contenu` s'ils ne sont plus actifs. """

        for i, effet in enumerate(self.contenu):
            if not effet.est_active():
                del self.contenu[i]
            elif effet.nom == "Liaison" and effet.attaquant.statistiques.vie.valeur <= 0:
                del self.contenu[i]
    
    def contient(self, nom: str):
        """ GestionnaireEffets, str -> bool
        Détermine si l'effet de `nom` donné est dans la liste `self.contenu`. """

        for effet in self.contenu:
            if effet.nom == nom:
                return True
        
        return False

    def récupérer(self, nom: str):
        """ GestionnaireEffets, str -> bool
        Renvoie l'effet de `nom` donné de la liste `self.contenu`. """

        for effet in self.contenu:
            if effet.nom == nom:
                return effet
        
        raise NameError ("L'effet de nom '{nom}' n'appartient pas à {self}.")
    
    def retirer(self, nom: str, attaquant: Entité = None):
        """ GestionnaireEffets, str -> None
        Supprime l'effet de `nom` donné de la liste `self.contenu`. """

        for i, effet in enumerate(self.contenu):
            if effet.nom == nom:
                if attaquant is None or effet.attaquant is attaquant:
                    del self.contenu[i]

class Arme:
    """ Représente une Arme """

    def __init__(self, nom: str):
        """ Arme, str -> None """

        self.nom = nom

        self.modèle: list[tuple[int, int]] = exécuter_sql(f"""SELECT CasesViseesArme.x, CasesViseesArme.y FROM CasesViseesArme JOIN Arme ON Arme.nom = CasesViseesArme.arme WHERE Arme.nom = '{self.nom}';""")

        centre_x, centre_y, centree_joueur, puissance, duree, attente, vitesse, projectiles, invocation = exécuter_sql(f"""SELECT centre_x, centre_y, centree_joueur, puissance, duree, attente, vitesse, projectiles, invocation FROM Arme WHERE nom = '{self.nom}';""")[0]
        
        self.centre: tuple[int, int] = centre_x, centre_y
        self.centrée_joueur = bool(centree_joueur)
        self.puissance: int = puissance
        self.durée: float = duree
        self.attente: float = attente
        self.vitesse: int = vitesse
        self.projectiles: int = projectiles
        self.invocation: int = invocation

        self.monde: list[str] = [monde[0] for monde in exécuter_sql(f"""SELECT monde FROM MondeArme WHERE arme = '{self.nom}';""")]

        self.initialiser_image()

    def initialiser_image(self):
        """ Arme -> None
        Initialise les images. """

        if exécuter_sql(f"""SELECT COUNT(*) FROM Projectile WHERE nom = '{self.nom}';""")[0][0] == 0:
            self.icône = charger_image(f"Armes/Icônes/{self.nom}")

        if self.puissance > 0:
            self.particule = charger_image(f"Armes/Particules/{self.nom}", changement_taille=False)

    def __repr__(self):
        """ Arme -> str """

        return f"#{self.nom}"

class Attaque:
    """ Représente une Attaque """

    def __init__(self, x: int, y: int, puissance: int, durée: float, attente: float, monde_arme: list[str], immunisés: set[type] = {}, effets: dict[str, float] = {}, attaquant: Entité = None):
        """ Attaque, int, int, int, float, float, [str], {type}, {str: float} -> None """

        self.x = x
        self.y = y

        self.puissance = puissance
        self.monde = monde_arme

        self.début = chronomètre.temps_écoulé()
        self.durée = durée
        self.attente = attente

        self.immunisés = immunisés
        self.effets = effets
        self.attaquant = attaquant
    
    def afficher(self):
        """ Attaque -> None
        Affiche l'attaque `self`. """
        
        surface_attaque = pygame.Surface((taille_case, taille_case), pygame.SRCALPHA)
        surface_attaque.fill((255, 0, 0, compression(255 - 255 / 3000 * self.puissance * (chronomètre.temps_écoulé() - self.début - self.attente) / self.durée, 0, 255)))
        
        afficher_en_jeu(surface_attaque, (int(self.x / taille_case) * taille_case, int(self.y / taille_case) * taille_case))

    def active(self):
        """ Attaque -> bool
        Détermine si l'attaque `self` est encore active. """

        return chronomètre.temps_écoulé() - self.début - self.attente <= self.durée
    
    def dangereuse(self):
        """ Attaque -> bool
        Détermine si l'attaque `self` peut faire des dégâts. """

        return chronomètre.temps_écoulé() - self.début >= self.attente

    def __repr__(self):
        """ Attaque -> str
        Renvoie une représentation de l'attaque. """

        return f"Attaque({self.x}, {self.y}, {self.puissance}, {self.durée})"

class GestionnaireAttaques:
    """ Gère l'ensemble des Attaques """

    def __init__(self):
        """ GestionnaireAttaques -> None """

        self.contenu: list[Attaque] = []
    
    def supprimer(self):
        """ GestionnaireAttaques -> None
        Supprime les Attaques qui ne sont plus actives de la liste `self.contenu`. """

        for i, attaque in enumerate(self.contenu):
            if not attaque.active():
                del self.contenu[i]
                continue
    
    def afficher(self):
        """ GestionnaireAttaques -> None
        Affiche toutes les Attaques de la liste `self.contenu`. """

        if not getattr(liste_paramètres,"show_damage",True): 
            return

        for attaque in self.contenu:
            attaque.afficher()
    
    def ajouter(self, attaque: Attaque):
        """ GestionnaireAttaques, Attaque -> None
        Ajoute une `attaque` à la liste `self.contenu`. """

        self.contenu.append(attaque)
    
    def __len__(self):
        """ GestionnaireAttaques -> int
        Renvoie la longeur de la liste `self.contenu`. """

        return len(self.contenu)

class FileInventaire:
    """ Représente un Inventaire composé d'une file d'Armes. """

    def __init__(self, armes: list[Arme] = []):
        """ FileInventaire, [Arme] -> None """

        self.armes = File()
        for arme in armes:
            self.armes.enfiler(arme)
    
    def est_vide(self):
        """ FileInventaire -> bool
        Détermine si la FileInventaire `self` est vide. """
        
        return self.armes.est_vide()
    
    def enfiler(self, v):
        """ FileInventaire, int -> None
        Ajoute l'élément v à la FileInventaire `self`. """
        
        return self.armes.enfiler(v)
    
    def defiler(self):
        """ FiFileInventairele -> int
        Renvoie le premier élément de la FileInventaire `self` en le supprimant de celle-ci. """
        
        return self.armes.defiler()  
    
    def longueur(self):
        """ File -> int
        Renvoie la longueur de la FileInventaire `self`. """

        return self.armes.longueur()

    def tete(self):
        """ File -> int
        Renvoie la valeur du premier élément de la FileInventaire `self` sans la modifier. """

        return self.armes.tete()

    def __str__(self):
        """ self -> str
        Construit la chaîne de caractères représentant la FileInventaire `self`. """

        return str(self.armes)

class Particule:
    """ Représente une Particule """

    def __init__(self, x: int, y: int, image: pygame.Surface, durée: float, direction: float = 0, nom_arme: str = None):
        """ Particule, int, int, Surface, float, float -> None """

        if nom_arme is None:
            self.x = x
            self.y = y

            self.image = pygame.transform.rotate(image, -math.degrees(direction))
        
        else:
            largeur, hauteur, centre_x, centre_y = taille_arme(nom_arme)

            self.image = pygame.transform.scale(image, (largeur, hauteur))

            self.image = pygame.transform.rotate(self.image, -math.degrees(direction))

            décalage_x = centre_x - largeur / 2
            décalage_y = centre_y - hauteur / 2

            cos = math.cos(direction)
            sin = math.sin(direction)

            décalage_tourné_x = cos * décalage_x - sin * décalage_y
            décalage_tourné_y = cos * décalage_y + sin * décalage_x
            
            self.x, self.y = self.image.get_rect(center=(x + taille_case//2 + décalage_tourné_x, y + taille_case//2 + décalage_tourné_y)).topleft

        self.début = chronomètre.temps_écoulé()
        self.durée = durée

    def afficher(self):
        """ Particule -> None
        Affiche la Particule `self`. """

        if not est_visible(pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())):
            return

        afficher_en_jeu(self.image, (self.x, self.y))
    
    def est_active(self):
        """ Particule -> bool
        Détermine si la Particule `self` est encore active. """

        return chronomètre.temps_écoulé() - self.début <= self.durée

class GestionnaireParticules:
    """ Gère la liste des Patricules. """

    def __init__(self):
        """ GestionnaireParticules -> None """

        self.contenu: list[Particule] = []
    
    def ajouter(self, particule: Particule):
        """ GestionnaireParticules, Particule -> None
        Ajoute la `particule` donnée à la liste `self.contenu`. """

        self.contenu.append(particule)
    
    def afficher(self):
        """ GestionnaireParticules -> None
        Affiche chaque Particule de la liste `self.contenu` en les supprimant si elles ne sont plus actives. """

        for i, particule in enumerate(self.contenu):
            if particule.est_active():
                particule.afficher()
            else:
                del self.contenu[i]

class Scène:
    """ Représente une scène. """

    def __init__(self, nom: str = None):
        """ Scène, str -> None """
        
        self.nom = nom

    def initialiser(self):
        """ Scène -> None
        Initialise la scène. """
        pass

    def modifier_boutons(self):
        """ Scène -> None
        Modifie le texte des boutons de la Scène `self`. """
        pass

    def action(self):
        """ Scène -> None
        Gère la scène. """
        pass

    def boucle_événements(self):
        """ Scène -> None
        Gère la boucle des événements de pygame pour la scène. """
        pass

    def afficher(self):
        """ Scène -> None
        Affiche la scène. """
        pass

    def afficher_boutons(self):
        """ Scène -> None
        Affiche les Boutons du dictionnaire `self.boutons`. """

        for bouton in self.boutons.values():
            bouton.afficher()

class ChoixLangue(Scène):
    """ Représente l'écran de Choix de Langue. """
    
    def initialiser(self):
        """ ChoixLangue -> None
        Initialise l'écran de Choix de Langue. """

        self.bouton_titre = Bouton("Titre", "§Choose a Language§", animation=3., superposition=False, center=(taille_fenêtre//2, taille_fenêtre//7))

        self.boutons_langue: list[Bouton] = []

        self.liste_langue = {"Français": 'fr', "Français scientifique": "fr-scientifique","Français Amusant": "fr-drôle","English": "en", "Pirate English": "en-p", "Deutsch": "de", "中文": "cn", "Türkçe": "tu", "Latinus, a, um": "la"}
        for i, langue in enumerate(self.liste_langue):
            self.boutons_langue.append(Bouton("Moyen", f"§{langue}§", color=(205, 205, 205), background=(50, 50, 50), durées_états=[.5, float("inf")], center=((i%2+1)*taille_fenêtre//3, (i//2+2)*taille_fenêtre//7)))
    
    def action(self):
        """ ChoixLangue -> None
        Gère l'écran de Choix de Langue. """

        self.boucle_événements()

        self.afficher()

    def boucle_événements(self):
        """ ChoixLangue -> None
        Gère la boucle des événements de pygame pour l'écran de Choix de Langue. """

        for événement in pygame.event.get():
            if fenêtre_fermée(événement):
                quitter()
            
            elif souris_est_pressée(événement):
                for bouton in self.boutons_langue:
                    if bouton.bouton_touché():
                        jouer_son("Sélection")

                        setattr(liste_paramètres, "language", self.liste_langue[bouton.texte])

                        global scène
                        scène = "Intro"
                
                jouer_son("Clique")
            
            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos

    def afficher(self):
        """ ChoixLangue -> None
        Affiche l'écran de Choix de Langue. """

        fenêtre.fill((0, 0, 0))

        self.bouton_titre.afficher()

        for bouton in self.boutons_langue:
            bouton.afficher()

class Cinématique(Scène):
    """ Représente une Cinématique """
    
    def initialiser(self):
        """ Cinématique -> None
        Initialise la Cinématique. """

        if self.nom == "Intro":
            self.boutons = [
                Bouton("Moyen", "Cinématique1", color=(0, 0, 0), superposition=False, largeur=taille_fenêtre, center=(taille_fenêtre//2, taille_fenêtre//2)),
                Bouton("Moyen", "Cinématique2", color=(255, 255, 255), superposition=False, largeur=taille_fenêtre, midtop=(taille_fenêtre//2, 0)),
                Bouton("Moyen", "Cinématique3", color=(255, 255, 255), superposition=False, largeur=taille_fenêtre, midbottom=(taille_fenêtre//2, taille_fenêtre)),
                Bouton("Moyen", "Cinématique4", color=(255, 255, 255), superposition=False, largeur=taille_fenêtre, center=(taille_fenêtre//2, taille_fenêtre//2))
            ]

            self.images = [
                charger_image("Interface Utilisateur/Cinématique/1", taille_fenêtre, taille_fenêtre),
                charger_image("Interface Utilisateur/Cinématique/2", taille_fenêtre, taille_fenêtre),
                charger_image("Interface Utilisateur/Cinématique/3", taille_fenêtre, taille_fenêtre),
                pygame.Surface((taille_fenêtre, taille_fenêtre))
            ]
        
        elif self.nom == "Monologue":
            self.boutons = [
                Bouton("Moyen", "Cinématique5", color=(255, 255, 255), superposition=False, largeur=taille_fenêtre, midbottom=(taille_fenêtre//2, taille_fenêtre)),
                Bouton("Moyen", "Cinématique6", color=(255, 255, 255), superposition=False, largeur=taille_fenêtre, midtop=(taille_fenêtre//2, 0)),
                Bouton("Moyen", "Cinématique7", color=(255, 255, 255), superposition=False, largeur=taille_fenêtre, midtop=(taille_fenêtre//2, 0)),
                Bouton("Moyen", "Cinématique8", color=(255, 255, 255), superposition=False, largeur=taille_fenêtre, midbottom=(taille_fenêtre//2, taille_fenêtre)),
                Bouton("Moyen", "Cinématique9", color=(255, 255, 255), superposition=False, largeur=taille_fenêtre, midbottom=(taille_fenêtre//2, taille_fenêtre)),
                Bouton("Moyen", "Cinématique10", color=(255, 255, 255), superposition=False, largeur=taille_fenêtre, center=(taille_fenêtre//2, taille_fenêtre//2))
            ]

            self.images = [
                charger_image("Interface Utilisateur/Cinématique/5", taille_fenêtre, taille_fenêtre),
                charger_image("Interface Utilisateur/Cinématique/6", taille_fenêtre, taille_fenêtre),
                charger_image("Interface Utilisateur/Cinématique/7", taille_fenêtre, taille_fenêtre),
                charger_image("Interface Utilisateur/Cinématique/8", taille_fenêtre, taille_fenêtre),
                charger_image("Interface Utilisateur/Cinématique/9", taille_fenêtre, taille_fenêtre),
                pygame.Surface((taille_fenêtre, taille_fenêtre))
            ]

        self.page = 0

        jouer_musique("Cinématique")
    
    def action(self):
        """ Cinématique -> None
        Gère la Cinématique. """

        self.boucle_événements()

        self.afficher()

    def boucle_événements(self):
        """ Cinématique -> None
        Gère la boucle des événements de pygame pour la Cinématique. """

        for événement in pygame.event.get():
            if fenêtre_fermée(événement):
                quitter()
            
            elif souris_est_pressée(événement):
                self.page += 1
                jouer_son("Clique")

                if self.page >= len(self.boutons):
                    global scène

                    if self.nom == "Intro":
                        jouer_son("Sélection")

                        scène = "Menu"
                    
                    elif self.nom == "Monologue":
                        jouer_musique("M.Picard")

                        global actualiser_nouvelle_scène

                        chronomètre.continuer()

                        actualiser_nouvelle_scène, scène = False, "Niveau"
            
            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos

    def afficher(self):
        """ Cinématique -> None
        Affiche la Cinématique. """

        if self.page >= len(self.boutons):
            return

        afficher(self.images[self.page], (0, 0))

        self.boutons[self.page].afficher()

class Menu(Scène):
    """ Représente le menu du jeu. """

    def initialiser(self):
        """ Menu -> None
        Initialise le menu. """

        self.boutons = {
            "Titre": Bouton("Titre", "The Legend of M.Picard", superposition=False, animation=3., durées_états=[.5, float("inf")], center=(taille_fenêtre//2, taille_fenêtre//5)),
            "Jouer": Bouton("Gros", "Jouer", durées_états=[1., float("inf")], center=(taille_fenêtre//2, 2*taille_fenêtre//3)),
            "Paramètres": Bouton("Moyen", "Paramètres", durées_états=[1.5, float("inf")], bottomleft=(0, taille_fenêtre)),
            "Quitter": Bouton("Moyen", "§x§", bottomright=(taille_fenêtre,taille_fenêtre))
        }

        self.image_fond = charger_image("Interface Utilisateur/Menu", taille_fenêtre, taille_fenêtre)

        jouer_musique("Menu")

    def modifier_boutons(self):
        """ Menu -> None
        Modifie le texte des boutons du Menu `self`. """

        for bouton in self.boutons.values():
            bouton.changer_langue()

    def action(self):
        """ Menu -> None
        Gère le menu. """

        self.boucle_événements()

        self.afficher()

    def boucle_événements(self):
        """ Menu -> None
        Gère la boucle des événements de pygame pour le menu. """

        for événement in pygame.event.get():
            if fenêtre_fermée(événement):
                quitter()
            elif souris_est_pressée(événement):
                if self.boutons["Jouer"].bouton_touché():
                    jouer_son("Sélection")
                    global scène
                    scène = "SélectionPersonnage"
                if self.boutons["Paramètres"].bouton_touché():
                    jouer_son("Sélection")
                    scène = "Paramètres"
                elif self.boutons["Quitter"].bouton_touché():
                    quitter()
                jouer_son("Clique")
            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos

    def afficher(self):
        """ Menu -> None
        Affiche le menu. """

        afficher(self.image_fond, (0, 0))

        self.afficher_boutons()

class SélectionPersonnage(Scène):
    """ Représente le menu de Sélection du Personnage. """

    def initialiser(self):
        """ SélectionPersonnage -> None
        Initialise le menu de Sélection du Personnage `self`. """

        self.boutons = {
            "Titre": Bouton("Titre", "Sélectionne un Personnage", superposition=False, animation=2., durées_états=[.5, float("inf")], center=(taille_fenêtre//2, taille_fenêtre//5)),
            "Paramètres": Bouton("Moyen", "Paramètres", durées_états=[1.5, float("inf")], bottomleft=(0, taille_fenêtre)),
            "Menu": Bouton("Moyen", "Menu", durées_états=[1.5, float("inf")], bottomright=(taille_fenêtre, taille_fenêtre)),
            "Gauche": Bouton("Moyen", "", image=charger_image("Interface Utilisateur/Flèche"), durées_états=[2., float("inf")], midbottom=(3*taille_fenêtre//7, taille_fenêtre)),
            "Droite": Bouton("Moyen", "", image=pygame.transform.flip(charger_image("Interface Utilisateur/Flèche"), True, False), durées_états=[2., float("inf")], midbottom=(4*taille_fenêtre//7, taille_fenêtre))
        }

        self.image_fond = charger_image("Interface Utilisateur/Menu", taille_fenêtre, taille_fenêtre)

        self.page = 0

        self.initialiser_boutons_personnages()

        jouer_musique(nom="Menu")

    def initialiser_boutons_personnages(self):
        """ SélectionPersonnage -> None
        Initialise les Boutons des personnages du menu de Sélection du Personnage `self`. """

        personnages: list[tuple[str]] = exécuter_sql(f"""SELECT nom FROM Personnage;""")
        random.shuffle(personnages)
        nombre_personnage = len(personnages)

        self.boutons_personnages: list[Bouton] = []
        for i, nom in enumerate(personnages):
            x = taille_fenêtre // 2 + 1.5 * taille_fenêtre // 22 * (2 * ((i % 28) % 7) - 6)
            y = taille_fenêtre // 2 + 1.5 * taille_fenêtre // 22 * (2 * ((i % 28) // 7) - (((nombre_personnage - 1) % 28 + 1) // 7 - 1))

            bouton = Bouton("Gros", f"§{nom[0]}§", image=ajouter_cadre(charger_image(f"Entités/Personnages/{nom[0]}")), durées_états=[.5, float("inf")], center=(x, y))
            self.boutons_personnages.append(bouton)

    def modifier_boutons(self):
        """ SélectionPersonnage -> None
        Modifie le texte des boutons du menu de Sélection du Personnage `self`. """

        for bouton in self.boutons.values():
            bouton.changer_langue()

    def action(self):
        """ SélectionPersonnage -> None
        Gère le menu de Sélection du Personnage `self`. """

        self.boucle_événements()

        self.afficher()

    def boucle_événements(self):
        """ SélectionPersonnage -> None
        Gère la boucle des événements de pygame pour le menu de Sélection du Personnage `self`. """

        for événement in pygame.event.get():
            if fenêtre_fermée(événement):
                quitter()
            
            elif souris_est_pressée(événement):
                for i, bouton in enumerate(self.boutons_personnages):
                    if i // 28 == self.page and bouton.bouton_touché():
                        global scène
                        données_scène_suivante["joueur"] = bouton.texte
                        scène = "Partie"
                
                if self.boutons["Paramètres"].bouton_touché():
                    jouer_son("Sélection")
                    scène = "Paramètres"

                elif self.boutons["Menu"].bouton_touché():
                    jouer_son("Retour")
                    scène = "Menu"
                
                elif self.boutons["Gauche"].bouton_touché():
                    jouer_son("Sélection")
                    if self.page > 0:
                        self.page -= 1
                
                elif self.boutons["Droite"].bouton_touché():
                    jouer_son("Sélection")
                    if self.page < (len(self.boutons_personnages) - 1) // 28:
                        self.page += 1
                
                jouer_son("Clique")
            
            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos

    def afficher(self):
        """ SélectionPersonnage -> None
        Affiche le menu de Sélection du Personnage `self`. """

        afficher(self.image_fond, (0, 0))

        self.afficher_boutons()
        
        for i, bouton in enumerate(self.boutons_personnages):
            if i // 28 == self.page:
                bouton.afficher()

def pathfinding():
    """ () -> Grille
    Génère une grille remplie des directions pour aller au joueur le plus vite. """

    grille = Grille()
    for _ in range(taille_salle): grille.ajouter_ligne([None] * taille_salle)

    joueur_x = joueur.x % taille_salle
    joueur_y = joueur.y % taille_salle

    contamination(grille, joueur_x, joueur_y, None, 0)

    return grille

def contamination(grille: Grille, x: int, y: int, valeur: int, distance: int):
    """ Grille, int, int, tuple[int, int, int], int -> None
    Modifie récursivement la `grille donnée`. """
    get = grille.récupérer(x, y)
    if not joueur.salle.récupérer(x, y).collision:
        if get is None or get[2] > distance:
            if valeur is None:
                grille.placer(x, y, None)
            else:
                grille.placer(x, y, (valeur[0], valeur[1], distance))
            
            if x > 0:
                contamination(grille, x-1, y, (1, 0), distance+1)
            if x < taille_salle-1:
                contamination(grille, x+1, y, (-1, 0), distance+1)
            if y > 0:
                contamination(grille, x, y-1, (0, 1), distance+1)
            if y < taille_salle-1:
                contamination(grille, x, y+1, (0, -1), distance+1)
        elif get is not None and get[2] == distance and random.randint(0, 1):
            if valeur is None:
                grille.placer(x, y, None)
            else:
                grille.placer(x, y, (valeur[0], valeur[1], distance))
            
            if x > 0:
                contamination(grille, x-1, y, (1, 0), distance+1)
            if x < taille_salle-1:
                contamination(grille, x+1, y, (-1, 0), distance+1)
            if y > 0:
                contamination(grille, x, y-1, (0, 1), distance+1)
            if y < taille_salle-1:
                contamination(grille, x, y+1, (0, -1), distance+1)

# salle = joueur.salle

# joueur_x = joueur.x % taille_salle
# joueur_y = joueur.y % taille_salle
# for monstre in salle.monstres:
#     monstre_x = monstre.x % taille_salle
#     monstre_y = monstre.y % taille_salle

# case = salle.récupérer(x, y)
# if case.collision:
#     ...

# for x in range(taille_salle):
    # for y in range(taille_salle):
        # ...

    
def chemins_entités(faits, l_direction, position, joueur):
    x, y = position
    xj, yj = joueur
    taille = len(faits.contenu)
    if 0 <= x < taille and 0 <= y < taille:
        if not faits.récupérer(x, y):
            l_direction.placer(x, y, [xj - x, yj - y])
            faits.placer(x, y, True)
            if x > 0:
                chemins_entités(faits, l_direction, (x - 1, y), joueur)
            if y > 0:
                chemins_entités(faits, l_direction, (x, y - 1), joueur)
            if x < taille - 1:
                chemins_entités(faits, l_direction, (x + 1, y), joueur)
            if y < taille - 1:
                chemins_entités(faits, l_direction, (x, y + 1), joueur)
    return faits, l_direction




def convertir_en_tuple(x, y):
    liste=[]
    if x < 0 and math.sqrt(y**2)<=math.sqrt(x**2) :
        liste.append((-1, 0))
    if x > 0 and math.sqrt(y**2)<=math.sqrt(x**2):
        liste.append((1, 0))  
    if y > 0 and math.sqrt(y**2)>=math.sqrt(x**2) :
        liste.append((0, 1))
    if y < 0 and math.sqrt(y**2)>=math.sqrt(x**2):
        liste.append((0, -1))
    if len(liste)>0:
        random.shuffle(liste)
        return liste[0]
    else :
        return (0,0)

class Partie(Scène):
    """ Représente la partie du jeu. """

    def initialiser(self):
        """ Partie -> None
        Initialise la niveau. """

        global difficulté_monde
        difficulté_monde = 0

        sql: list[tuple[str]] = exécuter_sql(f"""SELECT nom FROM Monde;""")
        random.shuffle(sql)

        self.mondes = Pile()

        for monde in sql:
            self.mondes.empiler(monde[0])

        # global monde
        # monde = "Musique"
        
        global joueur
        joueur = Joueur(données_scène_suivante["joueur"], 0, 0, None)

        global gold
        gold = 5

        global surcis
        surcis = True

        jouer_musique("Donjon")
        self.initialiser_arbre()
    
    def action(self):
        """ Niveau -> None
        Gère la niveau. """
        
        if self.mondes.est_vide():
            
            global monde
            if monde == "Parcoursup":

                global scène
                scène = "Fin"

                return
            
            else:

                monde = "Parcoursup"
                scène = "Niveau"

                return

        monde = str(self.mondes.depiler())
        # monde = "Francais"

        scène = "Niveau"

    def initialiser_arbre(self):

        global arbre, amélioration, option_suivante, noeux_actuel

        f = File()

        status_goat = [1, 2, 3]
        random.shuffle(status_goat)
        g1 = status_goat.pop()
        g1 = [g1 + i *1000 for i in range(3)]
        g2 = status_goat.pop()
        g2 = [g2 + i *1000 for i in range(3)]
        g3 = status_goat.pop()
        g3 = [g3 + i *1000 for i in range(3)]

        amé_bien = [10, 11, 14, 13]
        random.shuffle(amé_bien)

        amé_ok = [12, 16, 18, 34, 37]
        random.shuffle(amé_ok)

        amé_moyenne = [36, 35]
        random.shuffle(amé_moyenne)

        amé_nul = [6, 15, 17, 51]
        random.shuffle(amé_nul)

        amé_spécial = [amé_bien.pop(), amé_nul.pop(), amé_bien.pop()]
        random.shuffle(amé_spécial)

        potion = [52]
        
        amélioration = {1:("criticalhit", 30), 2:("vampire", 30), 3: ("poison",30), 1001:("criticalhit", 25), 1002:("vampire", 25), 1003: ("poison",25), 2001:("criticalhit", 20), 2002:("vampire", 20), 2003: ("poison",20)} 

        for ench_id in g3:
            amélioration[ench_id] = (amélioration[ench_id][0],min(25,amélioration[ench_id][1]))

        amélioration[4] = ("doublegold", 25)
        amélioration[51] = ("potion", 8)
        amélioration[52] = ("potion", 8)
        amélioration[71] = ("teleport", 10)
        amélioration[72] = ("teleport", 10)
        amélioration[8] = ("random", random.randint(5, 15))
        amélioration[81] = ("random", random.randint(5, 15))
        amélioration[82] = ("random", random.randint(5, 15))
        amélioration[83] = ("random", random.randint(5, 15))
        amélioration[9] = ("reset", 35)

        amélioration[10] = ("freeze", 20)
        amélioration[11] = ("chaines", 20)
        amélioration[14] = ("double_attack", 20)

        amélioration[12] = ("coffre", 15)
        amélioration[16] = ("arrow", 15)
        amélioration[18] = ("rage", 15)

        amélioration[6] = ("antistun", 8)
        amélioration[15] = ("vie", 8)
        amélioration[17] = ("arrow_flame", 8)
        amélioration[36] = ("epeerare", 8)

        amélioration[34] = ("enclume", 15)
        amélioration[35] = ("fontaine", 10)
        
        amélioration[37] = ("revive", 60)

        for i in range(9991,9999) : amélioration[i]=("empty", 0)

        amélioration[13] = ("régénération", 8)

        l = [9, amé_ok.pop(), amé_ok.pop(), amé_bien.pop(), amé_nul.pop(), amé_spécial.pop(), amé_moyenne.pop(), amé_moyenne.pop(), amé_spécial.pop(), g3.pop(0), 81, amé_ok.pop(), g1.pop(0), potion.pop(), amé_nul.pop(), amé_spécial.pop()]
        l = [4, g1.pop(-1)] + [71, g2.pop(), amé_bien.pop(), g1.pop(-1)] + [amé_nul.pop(), amé_ok.pop(), 82, g2.pop(), g3.pop(), amé_ok.pop(), 83, 72] + l
        
        l = [0] + l
        for i in l:
            f.enfiler(i)
        arbre = creer_arbre(f)

        t1 = gauche(gauche(arbre))
        t2 = droit(droit(droit(arbre)))
        t1.teleport = t2
        t2.teleport = t1

        noeux_actuel = arbre
        option_suivante = [gauche(noeux_actuel), droit(noeux_actuel)]
        inverser_arbre(arbre)

class Niveau(Scène):
    """ Représente un niveau du jeu. """

    def initialiser(self):
        """ Niveau -> None
        Initialise la niveau. """

        global chargement
        chargement = Bouton("Gros", f"Chargement§{'.'*(int(chronomètre.temps_écoulé())%3+1)}§", superposition=False, animation=1., durées_états=[1., float("inf")], center=(taille_fenêtre//2, taille_fenêtre//2))

        global taille_donjon
        taille_donjon = 4
        
        global taille_salle
        taille_salle = 12

        global donjon
        donjon = Donjon()

        global entités
        entités = GestionnaireEntités()

        global caméra
        x, y = joueur.coordonnées_affichage()
        caméra = Caméra((x + taille_case // 2, y + taille_case // 2), 1)

        global attaques
        attaques = GestionnaireAttaques()

        global souris_pressée
        souris_pressée = False

        global particules
        particules = GestionnaireParticules()

        global projectiles
        projectiles = GestionnaireProjectiles()
        
        self.texte_monde = Bouton("Gros", monde, background=(55, 55, 55, 128), superposition=False, durées_états=[1., 2., 3.], center=(taille_fenêtre//2, round(taille_fenêtre/5.5)))

        self.bouton_difficulté = Bouton("Gros", f"§{joueur.salle.difficulté}§", color=(255, 140, 140), topright=(taille_fenêtre, 0))

        joueur.effets = GestionnaireEffets()

        global path
        path = Grille()

        if monde == "Parcoursup":
            jouer_musique("Parcoursup")

    def modifier_boutons(self):
        """ Niveau -> None
        Modifie le texte des boutons du Niveau `self`. """
        
        self.texte_monde.changer_langue()

    def action(self):
        """ Niveau -> None
        Gère le niveau. """

        self.boucle_événements()

        global clavier
        clavier = pygame.key.get_pressed()

        attaques.supprimer()
        donjon.rajouter_monstre()
        entités.déplacement()
        projectiles.avancer()
        entités.attaquer()
        projectiles.attaquer()
        entités.dégâts()
        entités.effets()
        entités.supprimer_entités()
        entités.ajouter_récompense()
        self.déplacement_caméra()

        self.afficher()

    def boucle_événements(self):
        """ Niveau -> None
        Gère la boucle des événements de pygame pour le niveau. """

        for événement in pygame.event.get():
            if fenêtre_fermée(événement):
                quitter()
            
            elif souris_est_pressée(événement):
                global souris_pressée
                souris_pressée = True
            
            elif souris_est_relachée(événement):
                souris_pressée = False
            
            elif touche_pressée(événement, [pygame.K_ESCAPE]):
                global scène

                jouer_son("Retour")

                scène = "Pause"
                global défilement
                défilement = 0
            
            elif liste_paramètres.touché_pressé("inventory", événement):
                jouer_son("Sélection")

                scène = "Inventaire"

            elif liste_paramètres.touché_pressé("upgrade", événement):
                jouer_son("Sélection")

                global actualiser_nouvelle_scène
                scène = "Arbre_Amélioration"

            elif touche_pressée(événement, [pygame.K_r]):
                actualiser_nouvelle_scène, scène = False, "Partie"

            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos
            
            elif événement.type == pygame.MOUSEWHEEL:
                if liste_paramètres.recupérer_paramètre("freecam"):
                    caméra.mettre_objectif_zoom(caméra.zoom * (1 + 0.5 * (événement.y)), 0.1)
            
        return False        

    def déplacement_caméra(self):
        """ Niveau -> None
        Gère le déplacement de la caméra. """
        
        joueur_x, joueur_y = joueur.coordonnées_affichage()
        joueur_x += taille_case // 2
        joueur_y += taille_case // 2

        centre_salle_x = joueur_x // (taille_case * taille_salle)
        centre_salle_y = joueur_y // (taille_case * taille_salle)

        centre_salle_x += 1/2
        centre_salle_y += 1/2

        centre_salle_x *= taille_case * taille_salle
        centre_salle_y *= taille_case * taille_salle

        x_final = (joueur_x + centre_salle_x) // 2
        y_final = (joueur_y + centre_salle_y) // 2

        caméra.mettre_objectif_déplacement((x_final, y_final), 0.1)
        caméra.déplacer()

    def afficher(self):
        """ Niveau -> None
        Affiche le niveau. """

        fenêtre.fill((0, 0, 0))

        donjon.afficher(0)

        attaques.afficher()

        #images={
        #    (0,0):charger_image("Cases/NSI/Mur.png", taille_case, taille_case),
        #    (1, 0):charger_image("Cases/Ouest.png", taille_case, taille_case),
        #    (-1, 0):charger_image("Cases/Est.png", taille_case, taille_case),
        #    (0,-1):charger_image("Cases/Nord.png", taille_case, taille_case),
        #    (0,1):charger_image("Cases/Sud.png", taille_case, taille_case),
        #     }


        #faits = Grille()
        #for _ in range(taille_salle):
        #    faits.ajouter_ligne([[] for _ in range(taille_salle)])
        
        #l_direction = Grille()
        #for _ in range(taille_salle):
        #    l_direction.ajouter_ligne([[] for _ in range(taille_salle)])
        #xj=(entités[0].x)
        #yj=(entités[0].y)
        #_, direction= chemins_entités(faits, l_direction, ((taille_donjon//2*taille_salle)%8, (taille_donjon//2*taille_salle)%taille_salle), (xj%taille_salle, yj%taille_salle))
        #salle_joueur_x=xj//taille_salle
        #salle_joueur_y=yj//taille_salle
        #for x in range(len(direction.contenu)): 
        #    for y in range(len(direction.contenu[0])):
        #        if direction.dans_la_grille(x, y):
        #            données = direction.récupérer(x, y)
        #            tintin = convertir_en_tuple(données[0], données[1])
        #            afficher_en_jeu(images[tintin], (x, y))

        particules.afficher()
        entités.afficher_effets()

        entités.afficher()

        donjon.afficher(1)

        entités.afficher_barre_de_vie()
        
        self.texte_monde.afficher()

        if liste_paramètres.recupérer_paramètre("show_difficulty", False):
            self.bouton_difficulté.modifier_texte(f"§{str(joueur.salle.difficulté)}§")
            self.bouton_difficulté.afficher()
        
        global affichage_dégat
        for bouton in affichage_dégat:
            bouton.afficher()

class Disposition: 
 
    @classmethod
    def constante_bouton(self,taille):
        return Bouton(taille,"",background=(0,0,0),topleft=(0,0)).rectangle.bottomleft[1]
    
    @classmethod
    def paramètre(self, paramètre):
        #Marge inférieur correspont à la marge entre deux section
        taille_élément = {"marge_coté": 0.06 * taille_fenêtre, "marge_coté_paramètre": 0.02 * taille_fenêtre, "nom_paramètre": 0.35 * taille_fenêtre, "espace_option": 0.5 * taille_fenêtre, "marge_inférieur": Disposition.constante_bouton("Moyen") * 0.3, "Occupation_y défileur": 0.15, "margex_défileur":0.07, "largeurdéfilant":0.02, "option_langue":1.0}
        return taille_élément[paramètre]
    
    @classmethod
    def aller_jusqua_paramètre(self, paramètre):
        somme = 0
        for para, distance in {"marge_coté": 0.06 * taille_fenêtre, "marge_coté_paramètre": 0.02 * taille_fenêtre, "nom_paramètre": 0.35 * taille_fenêtre, "espace_option": 0.5 * taille_fenêtre}.items():
            if para == paramètre:
                return somme
            somme += distance
    
    @classmethod
    def arbre_binaire(self, paramètre):
        taille_élément = {"marge": 0.05 * taille_fenêtre, "marge_y": 0.05 * taille_fenêtre, "espace_frères": 0.1, "espace_entre_branches":0.5}
        return taille_élément[paramètre]

    @classmethod
    def décalage_bouton(self):
        return Disposition.paramètre("nom_paramètre") * 0.04

class Paramètres_v2(Scène):
    
    def initialiser(self, ajouter_espace = False):
        """ Paramètres_v2 -> None
        Initialise les Paramètres """

        # INITIALISATION DES PARAMETRES FACILES
        global option_séléctionné
        option_séléctionné = None

        # INITIALISATION DE L'AFFICHAGE
        if ajouter_espace:
            dico = {("language", "Langue") : Option_Langue,
                    ("",""): None,
                    (".",""): None,
                    ("","."): None,
                    (".","."): None}
        else :
            dico = {("language", "Langue") : Option_Langue}
        section:dict[str,dict[tuple[str,str],str]] = {"géneral":dico,
                                                    "Audio":{("audio_global","Audio Globale"):Défilement,
                                                                    ("audio_musique","Musique du Jeu"):Défilement,
                                                                    ("audio_son","Effet de son"):Défilement},
                                                    "Affichage":{("fullscreen","Affichage plein écran"): initialiser_QCM({"Oui": True, "Non": False}),
                                                                    ("lighting","Luminosité"):Défilement,
                                                                    ("game_quality","Qualité des graphismes"): initialiser_QCM({"Maximum": 2, "Moyen": 1, "Minimum": 0}),
                                                                    ("show_damage","Afficher les dégâts"): initialiser_QCM({"Oui": True, "Non": False})},
                                                                    #("show_number_damage","§Afficher le nombre de dégats§"): initialiser_QCM({"Oui": True, "Non": False})},
                                                    "Contrôles":{("déplacement_devant","Déplacement Devant"):Entrée_ContrôleTouche,
                                                                    ("déplacement_arrière","Déplacement Derrière"):Entrée_ContrôleTouche,
                                                                    ("déplacement_gauche","Déplacement à Gauche"):Entrée_ContrôleTouche,
                                                                    ("déplacement_droite","Déplacement à Droite"):Entrée_ContrôleTouche,
                                                                    ("",""): None,
                                                                    ("inventory","Inventaire"):Entrée_ContrôleTouche,
                                                                    ("upgrade","Menu Amélioration"):Entrée_ContrôleTouche}}
                                                                    #("minimap","Mini map"):Entrée_ContrôleTouche}}
        if debug:
            section["Debugage"] = {("show_difficulty","Afficher la difficulté"): initialiser_QCM({"Oui": True, "Non": False}),
                                    ("show_layout","Afficher le layout"): initialiser_QCM({"Max": 2, "Mini": 1, "Non": 0}), 
                                    ("freecam","Option Camera libre"): initialiser_QCM({"Oui": True, "Non": False}),
                                    ("visionIR","Option Voir tout"): initialiser_QCM({"Oui": True, "Non": False}),
                                    ("godmode","Option Invincibilité"): initialiser_QCM({"Oui": True, "Non": False}),
                                    ("noclip","Option Passe-Muraille"): initialiser_QCM({"Oui": True, "Non": False}),
                                    ("infgold","Gold Infini"): initialiser_QCM({"Oui": True, "Non": False})}

        self.liste_section = []
        self.bouton_paramètre = Bouton("Gros", "Paramètres", color=(255,255,255), animation=.4, défilement=True, center=(taille_fenêtre // 2, Disposition.constante_bouton("Gros") * 0.7))
        défilement_actuel = Disposition.constante_bouton("Gros") * 1.8
        for section, liste_options in section.items():
            section_créer = Section(section,liste_options,défilement_actuel)
            défilement_actuel += section_créer.hauteur_affichage
            self.liste_section.append(section_créer)

        if ajouter_espace:
            option_séléctionné = self.liste_section[0].liste_option[0].valeur
        
        self.défilement_horizontale = Bouton("Mini", "", background=(200,200,200,200),largeur=taille_fenêtre*0.01, hauteur=taille_fenêtre**2/self.hauteur_affichage, topleft=(taille_fenêtre*0.99,(défilement/self.hauteur_affichage)*taille_fenêtre))
        self.barre_défilement_horizontale = Bouton("Mini", "", background=(200,200,200,20), superposition=False, largeur=taille_fenêtre*0.01, hauteur=taille_fenêtre, topleft=(taille_fenêtre*0.99,0))
        
        global sous_scène
        sous_scène = True

    def afficher(self):
        """ Paramètres_v2 -> None
        Affiche les paramètres """

        #Affichage Globale0

        flouter(6.)
        écran_noir = pygame.Surface((taille_fenêtre, taille_fenêtre), pygame.SRCALPHA)
        écran_noir.fill((0, 0, 0, 128))
        afficher(écran_noir, (0, 0))
        
        fenêtre.blit(surface_curseur_souris, surface_curseur_souris.get_rect(center=pygame.mouse.get_pos()))

        if liste_paramètres.recupérer_paramètre("show_layout")>0:
            taille = [Disposition.paramètre("marge_coté"), Disposition.paramètre("marge_coté_paramètre"), Disposition.paramètre("nom_paramètre"), Disposition.paramètre("espace_option")//2, Disposition.paramètre("espace_option")//2, Disposition.paramètre("marge_coté"),taille_fenêtre*0.01]
            couleur = [(200,0,0),(200,200,200),(20,100,255),(30,120,0),(0,120,30),(200,0,0),(255,255,255)]
            compteur = marge
            for i in range(len(taille)):
                pygame.draw.rect(fenêtre,couleur[i],pygame.Rect(compteur,0,taille[i],20))
                compteur += taille[i]

        self.bouton_paramètre.afficher()
        #Affichage Des boutons en tant que tel 
        for section in self.liste_section:
            section.afficher() #Affiche linéairement (à une certaine hauteur) et modifie l'hauteur d'affichage d'après
        
        self.défilement_horizontale.coordonnées = {"topleft":(taille_fenêtre*0.99,(-défilement/self.hauteur_affichage)*taille_fenêtre)}
        self.défilement_horizontale.mise_à_jour_interface()
        self.défilement_horizontale.afficher()
        self.barre_défilement_horizontale.afficher()

    def action(self):

        if self.boucle_événements(): 
            self.afficher()
            jouer_musique()

    def boucle_événements(self):
        
        global option_séléctionné
        for événement in pygame.event.get():

            if fenêtre_fermée(événement):
                quitter()

            elif touche_pressée(événement, [pygame.K_ESCAPE]):
                if not isinstance(option_séléctionné, Entrée_ContrôleTouche) and not isinstance(option_séléctionné, Défilement): 
                    liste_paramètres.enregistrer()
                    jouer_musique()
                    global scène, actualiser_nouvelle_scène, dernière_scène
                    actualiser_nouvelle_scène, scène = False, dernière_scène

                    jouer_son("Retour")

                    return False
            
            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos
            
            elif événement.type == pygame.MOUSEWHEEL:
                global défilement
                défilement = compression(défilement + événement.y * 25, - self.hauteur_affichage + taille_fenêtre - 20, 0)
                self.mise_à_jour_interface()
                return True #Pour ré-afficher tous (CASSE LA BOUCLE)

            #Interraction avec les objets
            if option_séléctionné is None: 
                if souris_est_pressée(événement):
                    if self.barre_défilement_horizontale.bouton_touché():
                        défilement = compression(- (position_souris[1]/taille_fenêtre) * self.hauteur_affichage, - self.hauteur_affichage + taille_fenêtre - 20, 0)
                        return True
                    for section in self.liste_section:
                        section.est_cliquée()
                    
                    jouer_son("Clique")
                
            else:
                if type(option_séléctionné) is Entrée_ContrôleTouche:

                    if événement.type == pygame.KEYDOWN :
                        touche = pygame.key.name(événement.key)
                        if touche == "escape": #On met à None la touche
                            touche = None

                        #détermine de quel bouton il s'agit 1 ou 2 et modif en conséquence
                        valeur_actuel = getattr(liste_paramètres,option_séléctionné.variable)
                        #Mise à jour de la couleur
                        option_séléctionné.séléction.couleur = (255,255,255)
                        if option_séléctionné.séléction == option_séléctionné.bouton_touche1:
                            valeur_actuel[0] = touche
                            if touche!=None:
                                option_séléctionné.séléction.modifier_texte(f'§[ {touche.upper()} ]§')
                            else :
                                option_séléctionné.séléction.modifier_texte(f'§x§')

                        elif option_séléctionné.séléction == option_séléctionné.bouton_touche2:
                            valeur_actuel[1] = touche
                            if touche!=None:
                                option_séléctionné.séléction.modifier_texte(f'§[ {touche.upper()} ]§')
                            else :
                                option_séléctionné.séléction.modifier_texte(f'§x§')

                        setattr(liste_paramètres,option_séléctionné.variable,valeur_actuel)

                        #Reset de l'état du paramètre (pas séléctionné)
                        option_séléctionné.séléction = None
                        option_séléctionné = None
                        
                        return True #Pour ré-afficher tous (CASSE LA BOUCLE)
                    
                elif type(option_séléctionné) is Défilement and option_séléctionné.séléction == "input":
                    #Reset de l'état du paramètre (pas séléctionné), lorsque la condition est comprise
                    liste_touche_chiffre = [f'{i%10}' for i in range(0, 10)] + [f'[{i%10}]' for i in range(0, 10)]
                    if événement.type == pygame.KEYDOWN and pygame.key.name(événement.key) in liste_touche_chiffre:
                        chiffre = liste_touche_chiffre.index(pygame.key.name(événement.key)) % 10
                        if option_séléctionné.pourcentage is None:
                            option_séléctionné.pourcentage = chiffre
                        else : 
                            option_séléctionné.pourcentage = 10 * option_séléctionné.pourcentage + chiffre
                            option_séléctionné.pourcentage = compression(option_séléctionné.pourcentage, 0, 100)
                        option_séléctionné.bouton_pourcentage.modifier_texte(f"§{option_séléctionné.pourcentage}%§")
                    elif touche_pressée(événement, [pygame.K_BACKSPACE]):
                        option_séléctionné.pourcentage //= 10
                        option_séléctionné.bouton_pourcentage.modifier_texte(f'§{option_séléctionné.pourcentage}%§')
                    elif touche_pressée(événement, [13, 1073741912]): #ENTER
                        if option_séléctionné.pourcentage is None:
                            option_séléctionné.pourcentage = getattr(liste_paramètres, option_séléctionné.variable)
                        else :  
                            setattr(liste_paramètres, option_séléctionné.variable, option_séléctionné.pourcentage)
                        option_séléctionné.bouton_pourcentage.couleur = (255,255,255)
                        option_séléctionné.bouton_pourcentage.texte = f'§{option_séléctionné.pourcentage}%§'
                        option_séléctionné.bouton_pourcentage.modifier_texte(f'§{option_séléctionné.pourcentage}%§')
                        option_séléctionné.bouton_pourcentage.mise_à_jour_interface()
                        option_séléctionné = None
                    elif touche_pressée(événement, [pygame.K_ESCAPE]):
                        option_séléctionné.pourcentage = getattr(liste_paramètres, option_séléctionné.variable)
                        option_séléctionné.bouton_pourcentage.couleur = (255,255,255)
                        option_séléctionné.bouton_pourcentage.modifier_texte(f'§{option_séléctionné.pourcentage}%§')
                        option_séléctionné.bouton_pourcentage.mise_à_jour_interface()
                        option_séléctionné = None
                    
                elif type(option_séléctionné) is Défilement and option_séléctionné.séléction == "scroll":

                    if souris_est_pressée(événement) or touche_pressée(événement, [pygame.K_ESCAPE]):
                        setattr(liste_paramètres,option_séléctionné.variable,option_séléctionné.pourcentage)
                        option_séléctionné = None
                        return True
                    début = sum([marge, Disposition.aller_jusqua_paramètre("espace_option"),Disposition.paramètre("espace_option") * 0.2, Disposition.paramètre("margex_défileur") * (Disposition.paramètre("espace_option") * 0.8)])
                    fin = début + ((Disposition.paramètre("espace_option") * 0.8) - (Disposition.paramètre("espace_option") * 0.8) * Disposition.paramètre("margex_défileur") * 2)
                    option_séléctionné.pourcentage = compression(int(round((début - position_souris[0]) / (début - fin), 2) * 100), 0, 100)
                    option_séléctionné.bouton_pourcentage.texte = f'{option_séléctionné.pourcentage}%'
                    option_séléctionné.bouton_pourcentage.modifier_texte(f'§{option_séléctionné.pourcentage}%§')
                    option_séléctionné.bouton_pourcentage.mise_à_jour_interface()
                    setattr(liste_paramètres,option_séléctionné.variable,option_séléctionné.pourcentage)

                elif type(option_séléctionné) is Option_Langue:
                    
                    for bouton_langue in option_séléctionné.bouton_langue:

                        if bouton_langue.bouton_touché() and souris_est_pressée(événement): 
                            l = bouton_langue.texte.split("(")[1].removesuffix(")")
                            setattr(liste_paramètres, "language", l)
                            option_séléctionné.__init__(option_séléctionné.défilement_actuel)
                            option_séléctionné = None
                            scènes["Paramètres"] = Paramètres_v2()
                            scènes["Paramètres"].initialiser()
                            scènes[dernière_scène].modifier_boutons()
                            return True
        return True
    
    @property
    def hauteur_affichage(self):
        return sum([section.hauteur_affichage for section in self.liste_section]) + Disposition.constante_bouton("Gros") * 1.8

    def mise_à_jour_interface(self):
        """Paramètres_v2 -> None
        Mets à jour chaque composant de l'interface (les boutons in fine)"""
        
        for section in self.liste_section:
            section.mise_à_jour_interface()

class Section:
    
    def __init__(self,nom_section: str, paramètres: dict[tuple,str], défilement_actuel: int):
        """Section -> None"""

        self.nom = nom_section
        self.text_section = Bouton("Moyen", self.nom, superposition=False, défilement=True, topleft=(Disposition.paramètre("marge_coté"),défilement_actuel))
        self.liste_option: list[Option_v2] = []

        défilement_actuel += Disposition.constante_bouton("Moyen") * 1.2

        self.ligne_separation = pygame.Rect((Disposition.aller_jusqua_paramètre("espace_option") + marge, défilement_actuel),(100, len(self.liste_option) * Disposition.constante_bouton("Moyen")))
        for (keval,knom),vtype in paramètres.items():
            if vtype is not None:
                self.liste_option.append(Option_v2(vtype, keval, knom, défilement_actuel))
            else :
                self.liste_option.append(None)
            défilement_actuel += Disposition.constante_bouton("Moyen")

    @property
    def hauteur_affichage(self):
        return Disposition.constante_bouton("Moyen") * 1.2 + len(self.liste_option) * Disposition.constante_bouton("Moyen") + Disposition.paramètre("marge_inférieur")
    
    def afficher(self):
        """ Section -> None
        Affiche la section relative au paramètres """

        self.text_section.afficher()

        for option in self.liste_option:
            if option is not None:
                option.afficher()

        global défilement
        """self.ligne_separation.y += défilement
        pygame.draw.rect(fenêtre,(255,255,255),self.ligne_separation)
        self.ligne_separation.y -= défilement"""

    def est_cliquée(self):
        """ Section -> None
        Regarde dans les options si l'un est séléctionnée pour un changement"""

        for option in self.liste_option:
            if option is not None:
                option.est_cliquée()
    
    def mise_à_jour_interface(self):
        """Section -> None
        Mets à jour chaque composant de l'interface (les boutons in fine)"""

        for option in self.liste_option:
            if option is not None:
                option.mise_à_jour_interface()

class Option_v2:

    def __init__(self,type_option,nom_paramètre_machine,nom_paramètre_humain,pos_y):
        """ Option_v2 -> None"""

        self.nom_paramètre = nom_paramètre_machine
        self.nom_affiché = nom_paramètre_humain
        self.text_paramètre = Bouton("Mini", self.nom_affiché, color=(255,255,255), background=(200,200,200,20), défilement = True, largeur = Disposition.paramètre("nom_paramètre"), hauteur = Disposition.constante_bouton("Moyen"), alignement_x="gauche", midleft=(Disposition.paramètre("marge_coté") + Disposition.paramètre("marge_coté_paramètre"), pos_y + Disposition.constante_bouton("Moyen")/2))
        self.type_option = type_option
        
        self.y = pos_y

        self.valeur = None
        if type_option is Défilement:
            self.valeur = Défilement(self.nom_paramètre, self.y)
        elif type_option is Entrée_ContrôleTouche:
            self.valeur = Entrée_ContrôleTouche(self.nom_paramètre, self.y)
        elif isinstance(type_option, QCM):
            self.valeur = QCM(self.nom_paramètre, self.y, **type_option.args)
            type_option = QCM
        elif type_option is Option_Langue:
            self.valeur = Option_Langue(self.y)

    def afficher(self):
        """ Option_v2 -> None
        Affiche l'option """

        surligné = False
        for bouton in self.valeur.renvoie_sous_bouton()+[self.text_paramètre]:
            if bouton.bouton_touché():
                surligné = True

        self.text_paramètre.afficher(superposition_forcée=surligné)
        if self.valeur is not None:
            self.valeur.afficher(superposition_forcée=surligné)

    def est_cliquée(self):
        """ Option_v2 -> None
        Regarde si l'option (si elle existe) est séléctionnée pour un changement"""

        self.valeur is not None and self.valeur.est_cliquée() #Le début de la ligne évite l'excusion d'une valeur pas défini
    
    def mise_à_jour_interface(self):
        """Option_v2 -> None
        Mets à jour chaque composant de l'interface (les boutons)"""

        self.valeur.mise_à_jour_interface()

class Défilement:

    def __init__(self, variable, défilement):
        """ Défilement -> None"""
        
        self.variable = variable
        self.séléction = None
  
        self.pourcentage = getattr(liste_paramètres, self.variable)
        taille_coté = Disposition.paramètre("espace_option") * 0.2
        self.bouton_pourcentage = Bouton("Mini", f'§{self.pourcentage}%§', background=(200,200,200,20), superposition=True, défilement=True, largeur=taille_coté, hauteur=Disposition.constante_bouton("Moyen"), center=(Disposition.aller_jusqua_paramètre("espace_option") + taille_coté * 0.5, défilement + Disposition.constante_bouton("Moyen")/2))
        taille_coté_défileur = Disposition.paramètre("espace_option") * 0.8
        self.défileur_arrière_plan = Bouton("Mini", "", background=(200,200,200,20), superposition=True, défilement=True, largeur=taille_coté_défileur, hauteur=Disposition.constante_bouton("Moyen"), center=(Disposition.aller_jusqua_paramètre("espace_option") + taille_coté + taille_coté_défileur * 0.5, défilement + Disposition.constante_bouton("Moyen")/2))
        self.défileur = Bouton("Mini", "", background=(50,50,200,120), superposition=False, défilement=True, 
                               largeur=taille_coté_défileur*(1 - 2*Disposition.paramètre("margex_défileur")), hauteur=Disposition.paramètre("Occupation_y défileur")*Disposition.constante_bouton("Moyen"), 
                               center=(Disposition.aller_jusqua_paramètre("espace_option") + taille_coté + taille_coté_défileur * 0.5, défilement + Disposition.constante_bouton("Moyen")/2))
        
        co_x = Disposition.aller_jusqua_paramètre("espace_option") + Disposition.paramètre("espace_option") * 0.2 + Disposition.paramètre("margex_défileur") * Disposition.paramètre("espace_option") * 0.8 + (1 - 2*Disposition.paramètre("margex_défileur")) * (self.pourcentage/100) * taille_coté_défileur
        self.défilant = Bouton("Mini","", background=(50,50,200,255), défilement=True, largeur=Disposition.paramètre("largeurdéfilant")*Disposition.aller_jusqua_paramètre("espace_option"), hauteur=self.bouton_pourcentage.surface.get_height(),center=(co_x ,défilement + Disposition.constante_bouton("Moyen")/2))

    def afficher(self, superposition_forcée=False):
        """ Défilement -> None
        Affiche l'option de Défilement"""

        self.bouton_pourcentage.afficher(superposition_forcée=superposition_forcée)
        self.défileur_arrière_plan.afficher(superposition_forcée=superposition_forcée)
        self.défileur.afficher(superposition_forcée=superposition_forcée)
        self.mettre_à_jour_défilant()
        self.défilant.afficher(superposition_forcée=superposition_forcée)

    def est_cliquée(self):

        global option_séléctionné
        if self.bouton_pourcentage.bouton_touché():
            option_séléctionné = self
            self.bouton_pourcentage.couleur = (255,0,0)
            self.bouton_pourcentage.modifier_texte(f"§. . .§")
            self.pourcentage = None
            self.séléction = "input"
        
        elif self.défilant.bouton_touché():
            option_séléctionné = self
            self.séléction = "scroll"

        elif self.défileur_arrière_plan.bouton_touché():
            début = sum([marge, Disposition.aller_jusqua_paramètre("espace_option"),Disposition.paramètre("espace_option") * 0.2, Disposition.paramètre("margex_défileur") * (Disposition.paramètre("espace_option") * 0.8)])
            fin = début + ((Disposition.paramètre("espace_option") * 0.8) - (Disposition.paramètre("espace_option") * 0.8) * Disposition.paramètre("margex_défileur") * 2)
            self.pourcentage = compression(int(round((début - position_souris[0]) / (début - fin), 2) * 100), 0, 100)
            self.bouton_pourcentage.texte = f'{self.pourcentage}%'
            self.bouton_pourcentage.modifier_texte(f'§{self.pourcentage}%§')
            self.bouton_pourcentage.mise_à_jour_interface()
            setattr(liste_paramètres,self.variable,self.pourcentage)

    def mise_à_jour_interface(self):
        """Défilement -> None
        Mets à jour chaque composant de l'interface (les boutons)"""

        self.mettre_à_jour_défilant()

    def mettre_à_jour_défilant(self):
        """Défilement -> None
        Mets à jour chaque composant de l'interface (les boutons)"""
        
        if self.pourcentage == None:
            co_x = Disposition.aller_jusqua_paramètre("espace_option") + Disposition.paramètre("espace_option") * 0.2 + Disposition.paramètre("margex_défileur") * Disposition.paramètre("espace_option") * 0.8
        else : 
            taille_coté_défileur = Disposition.paramètre("espace_option") * 0.8
            co_x = Disposition.aller_jusqua_paramètre("espace_option") + Disposition.paramètre("espace_option") * 0.2 + Disposition.paramètre("margex_défileur") * Disposition.paramètre("espace_option") * 0.8 + (1 - 2*Disposition.paramètre("margex_défileur")) * (self.pourcentage/100) * taille_coté_défileur
        self.défilant.coordonnées["center"] = (co_x,self.défilant.coordonnées["center"][1])
        self.défilant.mise_à_jour_interface()

    def renvoie_sous_bouton(self):
        """Défilement -> Bouton
        Renvoie les boutons utlisées dans l'interface"""

        return [self.bouton_pourcentage, self.défileur_arrière_plan]

class Entrée_ContrôleTouche:

    def __init__(self, variable, défilement):
        """Entrée_ContrôleTouche -> None"""

        self.variable = variable
        self.séléction = None

        if getattr(liste_paramètres,self.variable)[0]!=None:
            self.touche1 = f'[ {getattr(liste_paramètres,self.variable)[0].upper()} ]'
        else : 
            self.touche1 = "x"
        if getattr(liste_paramètres,self.variable)[1]!=None:
            self.touche2 = f'[ {getattr(liste_paramètres,self.variable)[1].upper()} ]'
        else : 
            self.touche2 = "x"

        taille_coté = Disposition.paramètre("espace_option")/2
        self.bouton_touche1 = Bouton("Mini", f"§{self.touche1}§", background=(200,200,200,20), superposition=True, défilement=True, largeur=taille_coté, hauteur=Disposition.constante_bouton("Moyen"), center=(Disposition.aller_jusqua_paramètre("espace_option") + taille_coté * 0.5, défilement + Disposition.constante_bouton("Moyen")/2)) #Il faudrait ajouter une size
        self.bouton_touche2 = Bouton("Mini", f"§{self.touche2}§", background=(200,200,200,20), superposition=True, défilement=True, largeur=taille_coté, hauteur=Disposition.constante_bouton("Moyen"), center=(Disposition.aller_jusqua_paramètre("espace_option") + taille_coté * 1.5, défilement + Disposition.constante_bouton("Moyen")/2))
    
    def afficher(self, superposition_forcée=False):
        """Entrée_ContrôleTouche, bool -> None
        Affiche l'option pour la saisie des touches et affiche en surlignage si `superposition_forcée` est vraie"""

        self.bouton_touche1.afficher(superposition_forcée=superposition_forcée)
        self.bouton_touche2.afficher(superposition_forcée=superposition_forcée)

    def est_cliquée(self):
        """Entrée_ContrôleTouche -> None
        Regarde si boîte est touché """
        
        if self.bouton_touche1.bouton_touché():
            self.séléction = self.bouton_touche1
            self.bouton_touche1.couleur = (255,0,0)
            self.bouton_touche1.modifier_texte(f"§. . .§")
        elif self.bouton_touche2.bouton_touché():
            self.séléction = self.bouton_touche2
            self.bouton_touche2.couleur = (255,0,0)
            self.bouton_touche2.modifier_texte(f"§. . .§")
        else : 
            return
        
        global option_séléctionné
        option_séléctionné = self

    def mise_à_jour_interface(self):
        """Entrée_ContrôleTouche -> None
        Mets à jour chaque composant de l'interface (les boutons)"""

        self.bouton_touche1.mise_à_jour_interface()
        self.bouton_touche2.mise_à_jour_interface()
    
    def renvoie_sous_bouton(self):
        """Entrée_ContrôleTouche -> Bouton
        Renvoie les boutons utlisées dans l'interface"""

        return [self.bouton_touche1, self.bouton_touche2]

class QCM:
    
    def __init__(self, variable, défilement, **kargs):
        """ QCM, str, [str, Any] -> None
        Initialise les boutons.
        /!\\    `variable` : correspond l'artibut dans `liste_paramètres`
                `args` : correspond à un dictionnaire avec le `titre` du paramètre et comme valeur à quelle valeur il met `variable`"""
        
        self.variable = variable
        self.séléction_id = 0
        
        self.liste_option_valeur = list(kargs.values())
        taille_coté = Disposition.paramètre("espace_option")/len(self.liste_option_valeur)
        self.bouton_option = [Bouton("Mini", nom, color=(255,255,255), background=(200,200,200,20), superposition=True, fond_sélection=(197, 215, 219), défilement=True, largeur=taille_coté, hauteur=Disposition.constante_bouton("Moyen"), center=(Disposition.aller_jusqua_paramètre("espace_option") + (i + 0.5)*taille_coté, défilement + Disposition.constante_bouton("Moyen")/2)) for i, nom in enumerate(kargs.keys())]
        
        self.séléction_id = self.liste_option_valeur.index(getattr(liste_paramètres,self.variable))
        self.bouton_option[self.séléction_id].fond = (20, 20, 200, 100)
        self.bouton_option[self.séléction_id].fond_sélection = (20, 20, 255)
        self.bouton_option[self.séléction_id].mise_à_jour_interface()
        #print(self.séléction_id)
        
    def afficher(self, superposition_forcée = False):
        """QCM, bool -> None
        Affiche les option du QCM et en surlignage si `superposition_forcée` est vraie"""

        défilement_horizontale = taille_fenêtre//2
        for bouton in self.bouton_option:

            bouton.afficher(superposition_forcée=superposition_forcée)

    def est_cliquée(self):
        """QCM -> None
        Regarde et modifie l'option séléctionnée par un clique"""

        for bouton in self.bouton_option:
            if bouton.bouton_touché():

                #Reset du bouton actuellement séléctionnée
                ancien_bouton = self.bouton_option[self.séléction_id]
                ancien_bouton.fond = (200,200,200, 20)
                ancien_bouton.fond_sélection = (197, 215, 219)
                ancien_bouton.mise_à_jour_interface()

                #Mise à jour du bouton cliqué
                self.séléction_id = self.bouton_option.index(bouton)
                bouton.fond = (20, 20, 200, 100)
                bouton.fond_sélection = (20, 20, 255)
                setattr(liste_paramètres,self.variable,self.liste_option_valeur[self.séléction_id])
                bouton.mise_à_jour_interface()

    def mise_à_jour_interface(self):
        """QCM -> None
        Mets à jour chaque composant de l'interface (les boutons)"""

        for bouton in self.bouton_option:
            bouton.mise_à_jour_interface()
    
    def renvoie_sous_bouton(self):
        """QCM -> Bouton
        Renvoie le bouton utlisée dans l'interface"""

        return self.bouton_option

class Option_Langue:

    def __init__(self, défilement_actuel):
        """Option_Langue -> None"""

        self.défilement_actuel = défilement_actuel

        self.liste_langue = {'fr':"Français (fr)", "fr-scientifique" : "Français scientifique (fr-scientifique)","fr-drôle":"Français Amusant (fr-drôle)","en":"English (en)", "en-p": "Pirate English (en-p)", "de":"Deutsch (de)", "cn":"中文 (cn)", "tu":"Türkçe (tu)", "la":"Latinus, a, um (la)"}
        self.bouton_langue = [Bouton("Mini", f"§{self.liste_langue.pop(liste_paramètres.recupérer_paramètre('language'))}§", background=(20, 20, 200, 100), superposition=True, défilement=True, largeur=Disposition.paramètre("espace_option"), hauteur=Disposition.constante_bouton("Moyen"), center=(Disposition.aller_jusqua_paramètre("espace_option") + 0.5 * Disposition.paramètre("espace_option"), défilement_actuel + Disposition.constante_bouton("Moyen")/2))]
        for i,langue in enumerate(self.liste_langue.values()):
            self.bouton_langue.append(Bouton("Mini", f"§{langue}§", background=(200,200,200,20), superposition=True, défilement=True, largeur=Disposition.paramètre("espace_option"), hauteur=Disposition.constante_bouton("Mini") * Disposition.paramètre("option_langue"), alignement_x="gauche", center=(Disposition.aller_jusqua_paramètre("espace_option") + 0.5 * Disposition.paramètre("espace_option"), défilement_actuel + Disposition.constante_bouton("Mini") * (i + 0.5) * Disposition.paramètre("option_langue") + Disposition.constante_bouton("Moyen"))))
        
    def afficher(self, superposition_forcée = False):
        """Option_Langue -> None
        Affiche les options pour les langues (`superposition_forcée` n'est pas utlisé, mais nécessaire pour éviter une erreur) """
            
        global option_séléctionné
        self.bouton_langue[0].afficher()
        if option_séléctionné is self:
            for bouton in self.bouton_langue[1::]:
                bouton.afficher()
        
    def est_cliquée(self):
        """Option_Langue -> None
        Modifie la langue et mets à jour l'interface"""

        global option_séléctionné
        if not self.bouton_langue[0].bouton_touché():
            return
        if option_séléctionné is None:
            option_séléctionné = self
            option_séléctionné.afficher()
            scènes["Paramètres"] = Paramètres_v2()
            scènes["Paramètres"].initialiser(True)
    
    def mise_à_jour_interface(self):
        
        for bouton in self.bouton_langue:
            bouton.mise_à_jour_interface()

    def renvoie_sous_bouton(self):
        global option_séléctionné
        if option_séléctionné is not self:
            return [self.bouton_langue[0]]
        else:
            return self.bouton_langue

class Mort(Scène):
    """ Représente l'écran de mort du jeu. """

    def initialiser(self):
        """ Mort -> None
        Initialise l'écran de mort. """

        self.écran_rouge = pygame.Surface((taille_fenêtre, taille_fenêtre), pygame.SRCALPHA)
        self.écran_rouge.fill((255, 0, 0, 16))

        self.boutons = {
            "Titre": Bouton("Titre", "Tu es MORT", superposition=False, animation=1., durées_états=[2., float("inf")], center=(taille_fenêtre//2, taille_fenêtre//4)),
            "Mini": Bouton("Mini", "Peut-être la prochaine fois...", superposition=False, durées_états=[3., float("inf")], center=(taille_fenêtre//2, taille_fenêtre//3)),
            "Rejouer": Bouton("Gros", "Rejouer", background=(0, 0, 0, 32), durées_états=[1., float("inf")], center=(taille_fenêtre//4, 2*taille_fenêtre//3)),
            "Menu": Bouton("Gros", "Menu", background=(0, 0, 0, 32), durées_états=[1., float("inf")], center=(3*taille_fenêtre//4, 2*taille_fenêtre//3))
        }

        global sous_scène
        sous_scène = True

        jouer_son("Mort")

    def action(self):
        """ Mort -> None
        Gère l'écran de mort. """

        self.boucle_événements()

        entités.déplacement()
        caméra.déplacer()

        self.afficher()
        
    def boucle_événements(self):
        """ Mort -> None
        Gère la boucle des événements de pygame pour l'écran de mort. """

        for événement in pygame.event.get():
            if fenêtre_fermée(événement):
                quitter()
            
            elif souris_est_pressée(événement):
                global scène

                if self.boutons["Rejouer"].bouton_touché():
                    jouer_son("Sélection")

                    scène = "Partie"

                elif self.boutons["Menu"].bouton_touché():
                    jouer_son("Retour")

                    scène = "Menu"
                
                jouer_son("Clique")
            
            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos
    
    def afficher(self):
        """ Mort -> None
        Affiche l'écran de mort. """

        flouter(10.)

        afficher(self.écran_rouge, (0, 0))

        self.afficher_boutons()

class Fin(Scène):
    """ Représente l'écran de fin du jeu. """

    def initialiser(self):
        """ Fin -> None
        Initialise l'écran de fin. """

        sql: list[tuple[str]] = exécuter_sql(f"""SELECT nom FROM Projectile WHERE arme = '{joueur.arme.nom}';""")

        projectile = len(sql) > 0

        image_joueur = charger_image(f"Entités/Personnages/{joueur.nom}", changement_taille=False)
        image_joueur.set_at((6, 5 if joueur.nom == "Richard Feynman" else 6), (109, 209, 223))
        image_joueur.set_at((9, 5 if joueur.nom == "Richard Feynman" else 6), (109, 209, 223))
        image_joueur = pygame.transform.scale(image_joueur, (taille_fenêtre/2.25, taille_fenêtre/2.25))

        self.boutons = {
            "pisurquatre": Bouton("Gros", "", image=charger_image("Interface Utilisateur/i've won...... but at what cost", 16*taille_fenêtre/45, taille_fenêtre/4.5), superposition=False, bottomleft=(taille_fenêtre/9, taille_fenêtre + 2*taille_fenêtre/45)),
            "projectile": Bouton("Gros", "", image=pygame.transform.rotate(charger_image(f"Armes/{'Particules' if projectile else 'Icônes'}/{sql[0][0] if projectile else joueur.arme.nom}", taille_fenêtre/4, taille_fenêtre/4).subsurface((0, taille_fenêtre/32, taille_fenêtre/4, taille_fenêtre/4 - taille_fenêtre/32)), 180), superposition=False, midbottom=(taille_fenêtre/9 + taille_case * 3.475, taille_fenêtre - 2*taille_fenêtre/45)),
            "joueur": Bouton("Gros", "", image=image_joueur, superposition=False, bottomright=(taille_fenêtre, taille_fenêtre)),
            "arme": Bouton("Gros", "", image=pygame.transform.rotate(charger_image(f"Armes/Icônes/{joueur.arme.nom}", taille_fenêtre/4, taille_fenêtre/4), 45), superposition=False, center=(taille_fenêtre - 6 * taille_case, taille_fenêtre - 7 * taille_case / 3)),
            "Titre": Bouton("Titre", "§i've won......§", superposition=False, animation=1., durées_états=[.5, float("inf")], topleft=(0, 2 * taille_case)),
            "Titre2": Bouton("Titre", "§but at what cost§", superposition=False, animation=1., durées_états=[.5, float("inf")], topright=(taille_fenêtre, 4 * taille_case)),
        }

        self.image_fond = charger_image("Interface Utilisateur/Fin", taille_fenêtre, taille_fenêtre)
        
        jouer_musique("i've won...... but at what cost")

    def action(self):
        """ Fin -> None
        Gère l'écran de fin. """

        self.boucle_événements()

        self.afficher()
        
    def boucle_événements(self):
        """ Fin -> None
        Gère la boucle des événements de pygame pour l'écran de fin. """

        for événement in pygame.event.get():
            if fenêtre_fermée(événement):
                quitter()
            
            elif souris_est_pressée(événement):
                global scène

                jouer_son("Retour")

                scène = "Menu"
            
            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos
    
    def afficher(self):
        """ Fin -> None
        Affiche l'écran de fin. """

        afficher(self.image_fond, (0, 0))

        self.afficher_boutons()

class Pause(Scène):
    """ Représente l'écran de pause du jeu. """

    def initialiser(self):
        """ Pause -> None
        Initialise l'écran de pause. """

        chronomètre.pause()

        self.écran_noir = pygame.Surface((taille_fenêtre, taille_fenêtre), pygame.SRCALPHA)
        self.écran_noir.fill((0, 0, 0, 64))

        self.boutons = {
            "Titre": Bouton("Titre", "Pause", superposition=False, animation=1., durées_états=[1., float("inf")], en_pause=True, center=(taille_fenêtre//2, taille_fenêtre//5)),
            "Continuer": Bouton("Moyen", "Continuer", background=(0, 0, 0, 32), durées_états=[2., float("inf")], en_pause=True, center=(taille_fenêtre//2, 5*taille_fenêtre//12)),
            "Paramètres": Bouton("Moyen", "Paramètres", background=(0, 0, 0, 32), durées_états=[2., float("inf")], en_pause=True, center=(taille_fenêtre//2, taille_fenêtre//2)),
            "Menu": Bouton("Moyen", "Menu", background=(0, 0, 0, 32), durées_états=[2., float("inf")], en_pause=True, center=(taille_fenêtre//2, 7*taille_fenêtre//12))
        }

        global sous_scène
        sous_scène = True

        jouer_musique(volume=.5)

    def action(self):
        """ Pause -> None
        Gère l'écran de pause. """

        self.boucle_événements()

        self.afficher()
        
    def boucle_événements(self):
        """ Pause -> None
        Gère la boucle des événements de pygame pour l'écran de pause. """

        for événement in pygame.event.get():
            if fenêtre_fermée(événement):
                quitter()
            
            elif souris_est_pressée(événement):
                global scène

                if self.boutons["Continuer"].bouton_touché():
                    jouer_son("Sélection")
                    chronomètre.continuer()
                    jouer_musique()

                    global actualiser_nouvelle_scène, dernière_scène
                    actualiser_nouvelle_scène, scène = False, dernière_scène

                elif self.boutons["Paramètres"].bouton_touché():
                    jouer_son("Sélection")
                    chronomètre.continuer()

                    scène = "Paramètres"

                elif self.boutons["Menu"].bouton_touché():
                    jouer_son("Retour")
                    chronomètre.continuer()

                    scène = "Menu"
                
                jouer_son("Clique")
            
            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos
            
            elif touche_pressée(événement, [pygame.K_ESCAPE]):
                chronomètre.continuer()

                jouer_musique()
                jouer_son("Sélection")

                actualiser_nouvelle_scène, scène = False, "Niveau"
            
            elif touche_pressée(événement, [pygame.K_p]):
                jouer_son("Sélection")

                chronomètre.continuer()

                scène = "Paramètres"
            
            elif touche_pressée(événement, [pygame.K_m]):
                jouer_son("Retour")

                chronomètre.continuer()

                scène = "Menu"
    
    def afficher(self):
        """ Pause -> None
        Affiche l'écran de pause. """

        flouter(5.)

        afficher(self.écran_noir, (0, 0))

        self.afficher_boutons()

class Inventaire(Scène):
    """ Représente l'inventaire du joueur. """

    def initialiser(self):
        """ Inventaire -> None
        Initialise l'écran d'inventaire. """

        chronomètre.pause()
        
        self.écran_noir = pygame.Surface((taille_fenêtre // 2, taille_fenêtre // 2), pygame.SRCALPHA)
        self.écran_noir.fill((0, 0, 0, 64))

        self.bouton_titre = Bouton("Gros", "Inventaire", superposition=False, animation=1., durées_états=[.5, float("inf")], en_pause=True, center=(taille_fenêtre//2, taille_fenêtre//3))
        self.bouton_défiler = Bouton("Gros", "Défiler", background=(63, 63, 63, 64), fond_sélection=(0, 255, 0, 96), durées_états=[1., float("inf")], en_pause=True, center=(taille_fenêtre//2, 2*taille_fenêtre//3))

        self.flèche = charger_image("Interface Utilisateur/Flèche", taille_case, taille_case)

        self.initialiser_images_armes()

        global sous_scène
        sous_scène = True

        jouer_musique(volume=.5)

    def initialiser_images_armes(self):
        """ Inventaire -> None
        Initialise les images des armes de l'écran d'inventaire. """

        longueur = joueur.inventaire.longueur() + 2

        self.boutons = [Bouton("Gros", "", image=self.flèche, durées_états=[1., float("inf")], en_pause=True, center=(taille_fenêtre//2 - (longueur - 1) * 1.5 * taille_fenêtre//22, taille_fenêtre//2))]

        file_temporaire = File()

        i = 1
        while not joueur.inventaire.est_vide():
            arme: Arme = joueur.inventaire.defiler()

            self.boutons.append(Bouton("Gros", "", image=ajouter_cadre(arme.icône), durées_états=[0.5, float("inf")], en_pause=True, center=(taille_fenêtre//2 - (longueur - 1) * 1.5 * taille_fenêtre//22 + i * 3 * taille_fenêtre//22, taille_fenêtre//2)))
            
            file_temporaire.enfiler(arme)

            i += 1
        
        self.boutons.append(Bouton("Gros", "", image=self.flèche, durées_états=[1., float("inf")], en_pause=True, center=(taille_fenêtre//2 + (longueur - 1) * 1.5 * taille_fenêtre//22, taille_fenêtre//2)))
        
        while not file_temporaire.est_vide():

            joueur.inventaire.enfiler(file_temporaire.defiler())

    def action(self):
        """ Inventaire -> None
        Gère l'écran d'inventaire. """

        self.boucle_événements()

        self.afficher()
        
    def boucle_événements(self):
        """ Inventaire -> None
        Gère la boucle des événements de pygame pour l'écran d'inventaire. """

        for événement in pygame.event.get():
            if fenêtre_fermée(événement):
                quitter()
            
            elif souris_est_pressée(événement):

                if joueur.inventaire.longueur() > 1 and self.bouton_défiler.bouton_touché():
                    joueur.inventaire.defiler()
                    joueur.arme = joueur.inventaire.tete()
                    self.initialiser_images_armes()
                
                    jouer_son("Sélection")
                
                jouer_son("Clique")
            
            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos
            
            elif touche_pressée(événement, [pygame.K_ESCAPE, pygame.K_e]):
                jouer_son("Retour")

                global actualiser_nouvelle_scène, scène

                chronomètre.continuer()
                jouer_musique()

                actualiser_nouvelle_scène, scène = False, "Niveau"
    
    def afficher(self):
        """ Inventaire -> None
        Affiche l'écran d'inventaire. """

        flouter(3.)

        afficher(self.écran_noir, (taille_fenêtre // 4, taille_fenêtre // 4))

        for bouton in self.boutons:
            bouton.afficher()

        self.bouton_défiler.afficher(sélectionné=(joueur.inventaire.longueur() > 1))
        self.bouton_titre.afficher()

class Récompense(Scène):
    """ Représente l'écran de récompense des coffres. """

    def initialiser(self):
        """ Récompense -> None
        Initialise l'écran de récompense. """

        chronomètre.pause()

        self.type = données_scène_suivante["récompense"]
        
        self.écran_noir = pygame.Surface((round(taille_fenêtre / 1.75), round(taille_fenêtre / 1.75)), pygame.SRCALPHA)
        self.écran_noir.fill((0, 0, 0, 64))

        self.bouton_titre = Bouton("Gros", "" if self.type == "Enclume" else "Fais ton choix", superposition=False, animation=1., durées_états=[.5, float("inf")], en_pause=True, center=(taille_fenêtre//2, taille_fenêtre//3))

        self.passer = Bouton("Moyen", f"Passer§ (+{2+joueur.enchantements.possède_enchant(4)}g)§", superposition=True, durées_états=[.5, float("inf")], en_pause=True, midleft=(.75 * taille_fenêtre / 3.5 + 0.05 * taille_fenêtre, taille_fenêtre//1.5))
        self.reroll = Bouton("Moyen", "Reroll§ (9g)§", color=(255,255,255), superposition=True, durées_états=[.5, float("inf")], en_pause=True, midright=(taille_fenêtre - (.75 * taille_fenêtre / 3.5) - 0.05 * taille_fenêtre, taille_fenêtre//1.5))
        self.sql: list[tuple[str]] = exécuter_sql(f"""SELECT monstre FROM MondeMonstre{f" WHERE monde = '{monde}'" if monde != "Parcoursup" and not joueur.enchantements.possède_enchant(12) else ""};""")

        if not len(self.sql):
            global actualiser_nouvelle_scène, scène
                        
            chronomètre.continuer()

            actualiser_nouvelle_scène, scène = False, "Niveau"

        if self.type == "Coffre":
            self.initialiser_boutons_armes(self.sql)

        elif self.type == "EpeeRocher":
            self.initialiser_boutons_stats(self.sql)

        elif self.type == "Enclume":
            self.initialiser_enclume()

        global sous_scène
        sous_scène = True

        jouer_musique(volume=.5)
        jouer_son("Ouvrir")

    def initialiser_enclume(self):
        """ Récompense, [(str)] -> None
        Initialise les boutons des armes de l'écran de récompense. """

        self.boutons = []
        nombre_proposition = 1
        i=0
        arme = Arme("GlaceEpee")
        image = ajouter_cadre(charger_image(f"Armes/Icônes/{arme.nom}", taille_case, taille_case))
        self.boutons.append(Bouton("Gros", f"§{arme.nom}§", image=image, durées_états=[.1, float("inf")], en_pause=True, center=(taille_fenêtre//2 - (nombre_proposition - 1) * 1.5 * taille_fenêtre//22 + i * 3 * taille_fenêtre//22, taille_fenêtre//2)))

    def initialiser_boutons_armes(self, sql: list[tuple[str]]):
        """ Récompense, [(str)] -> None
        Initialise les boutons des armes de l'écran de récompense. """

        nombre_proposition = 3

        self.boutons: list[Bouton] = []

        for i in range(nombre_proposition):
            
            if random.random() < 0.091:
                arme = "Cadeau"

            elif random.random() < 0.307 + 0.091:
                arme = "Soin"
            
            else:
                arme = Monstre(random.choice(sql)[0], 0, 0, Salle(Composition())).arme.nom

            image = ajouter_cadre(charger_image(f"Armes/Icônes/{arme}", taille_case, taille_case))
            bouton = Bouton("Gros", f"§{arme}§", image=image, durées_états=[.1, float("inf")], en_pause=True, center=(taille_fenêtre//2 - (nombre_proposition - 1) * 1.5 * taille_fenêtre//22 + i * 3 * taille_fenêtre//22, taille_fenêtre//2))
            
            self.boutons.append(bouton)
    
    def initialiser_boutons_stats(self, sql: list[tuple[str]]):
        """ Récompense, [(str)] -> None
        Initialise les boutons des stats de l'écran de récompense. """

        nombre_proposition = 2

        noms_stats = ["vie", "puissance_physique", "vitesse_physique", "vitesse_déplacement", "régénération"]

        self.boutons: list[Bouton] = []

        for i in range(nombre_proposition):

            statistiques_monstre = Monstre(random.choice(sql)[0], 0, 0, Salle(Composition())).statistiques

            stat = random.choices(noms_stats, [round(statistiques_monstre.vie.régénération * 1000 / 2.380952381) if nom_stat == "régénération" else getattr(statistiques_monstre, nom_stat).maximum for nom_stat in noms_stats])[0]

            image = ajouter_cadre(charger_image(f"Stats/{stat}", taille_case, taille_case))
            bouton = Bouton("Gros", f"§{stat}§", image=image, durées_états=[.1, float("inf")], en_pause=True, center=(taille_fenêtre//2 - (nombre_proposition - 1) * 1.5 * taille_fenêtre//22 + i * 3 * taille_fenêtre//22, taille_fenêtre//2))
            
            self.boutons.append(bouton)

    def action(self):
        """ Récompense -> None
        Gère l'écran de récompense. """

        self.boucle_événements()

        self.afficher()
        
    def boucle_événements(self):
        """ Récompense -> None
        Gère la boucle des événements de pygame pour l'écran de récompense. """

        for événement in pygame.event.get():
            if fenêtre_fermée(événement):
                quitter()
            
            elif souris_est_pressée(événement):
                global gold
                if self.reroll.bouton_touché() and (gold>=9 or liste_paramètres.recupérer_paramètre("infgold")):
                    if self.type == "Coffre":
                        self.initialiser_boutons_armes(self.sql)
                    elif self.type == "EpeeRocher":
                        self.initialiser_boutons_stats(self.sql)
                    gold -= 9

                    jouer_son("Sélection")

                    return

                elif self.passer.bouton_touché():
                    jouer_son("Retour")

                    global actualiser_nouvelle_scène, scène

                    chronomètre.continuer()
                    jouer_musique()

                    gold += 2 +joueur.enchantements.possède_enchant(4)

                    actualiser_nouvelle_scène, scène = False, "Niveau"
                
                for bouton in self.boutons:
                    if bouton.bouton_touché():
                        if self.type == "Coffre":
                            joueur.inventaire.enfiler(Arme(bouton.texte))
                        elif self.type == "EpeeRocher":
                            if bouton.texte == "régénération":
                                joueur.statistiques.vie.régénération = max(joueur.statistiques.vie.régénération + 1, round(joueur.statistiques.vie.régénération * 1.1))
                            else:
                                getattr(joueur.statistiques, bouton.texte).maximum = max(getattr(joueur.statistiques, bouton.texte).maximum + 420, round(getattr(joueur.statistiques, bouton.texte).maximum * 1.1))
                                getattr(joueur.statistiques, bouton.texte).valeur = max(getattr(joueur.statistiques, bouton.texte).valeur + 420, round(getattr(joueur.statistiques, bouton.texte).valeur * 1.1))
                        elif self.type == "Enclume":
                            joueur.inventaire.enfiler(Arme("GlaceEpee"))

                        chronomètre.continuer()
                        jouer_musique()

                        jouer_son("Sélection")

                        actualiser_nouvelle_scène, scène = False, "Niveau"
                
                jouer_son("Clique")
            
            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos
    
    def afficher(self):
        """ Récompense -> None
        Affiche l'écran de récompense. """

        flouter(3.)

        afficher(self.écran_noir, (round(.75 * taille_fenêtre / 3.5), round(.75 * taille_fenêtre / 3.5)))

        self.bouton_titre.afficher()
        global gold
        if gold<9 and not liste_paramètres.recupérer_paramètre("infgold"):
            self.reroll.couleur = (200, 200, 200)
            self.reroll.mise_à_jour_interface()
        if self.type != "Enclume":
            self.reroll.afficher()
            self.passer.afficher()
        for bouton in self.boutons:
            bouton.afficher()

class Dialogue(Scène):
    """ Représente l'écran de Dialogue du jeu. """

    def initialiser(self):
        """ Dialogue -> None
        Initialise l'écran de Dialogue. """

        chronomètre.pause()

        self.pnj = données_scène_suivante["pnj"]

        texte = récupérer_dialogue(self.pnj)

        self.boutons = {
            "Texte": Bouton("Mini", f"§[§{self.pnj}§] ~ §{texte}", color=(0, 0, 0), background=(255, 255, 255), superposition=False, durées_états=[.5, float("inf")], en_pause=True, largeur=taille_fenêtre, hauteur=taille_fenêtre//3, alignement_x="gauche", alignement_y="haut", topleft=(0, 2*taille_fenêtre//3))
        }

        global sous_scène
        sous_scène = True

    def action(self):
        """ Dialogue -> None
        Gère l'écran de Dialogue. """

        self.boucle_événements()

        self.afficher()
        
    def boucle_événements(self):
        """ Dialogue -> None
        Gère la boucle des événements de pygame pour l'écran de Dialogue. """

        for événement in pygame.event.get():
            if fenêtre_fermée(événement):
                quitter()
            
            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos
            
            elif touche_pressée(événement, [pygame.K_ESCAPE]):
                chronomètre.continuer()

                global actualiser_nouvelle_scène, scène
                actualiser_nouvelle_scène, scène = False, "Niveau"
    
    def afficher(self):
        """ Dialogue -> None
        Affiche l'écran de Dialogue. """

        self.afficher_boutons()

def creer_arbre(liste_valeur : File):
    """ File -> Noeud
    Créer un arbre avec comme valeur les éléments de `liste_valeur` dans un ordre préfixe"""
    file = File()
    file.enfiler(Noeud(liste_valeur.defiler(), creer_vide(), creer_vide()))
    valeur_retour = None
    while not liste_valeur.est_vide():
        noeud_gauche = Noeud(liste_valeur.defiler(), creer_vide(), creer_vide())
        noeud_droit = creer_vide()
        if not liste_valeur.est_vide():
            noeud_droit = Noeud(liste_valeur.defiler(), creer_vide(), creer_vide())
        noeud_actuel = file.defiler()
        noeud_actuel.gauche = noeud_gauche
        noeud_actuel.droit = noeud_droit
        if file.est_vide(): #Aucun élément = début
            valeur_retour = noeud_actuel #Endroit dans la mémoire (car c'est une class)
        file.enfiler(noeud_gauche)
        file.enfiler(noeud_droit)
    return valeur_retour
        
def afficher_arbre_text(a, decalement=0):
    """ Noeud -> None
    Affiche l'arbre binaire (sert pour le débuggage)"""
    if est_vide(a):
        return
    # print(decalement*" - "+etiquette_str(a))
    afficher_arbre(gauche(a),decalement+1)
    afficher_arbre(droit(a),decalement+1)

def possède_amélioration(gestionnaire_enchantement: GestionnaireEnchantement, id):
    """ GestionnaireEnchantement, int -> bool
    Regarde si une amélioration appartient au Gestionnaire d'enchantement"""
    return gestionnaire_enchantement.possède_enchant(id)

def possède_améliorations(gestionnaire_enchantement: GestionnaireEnchantement, liste_id):
    """ GestionnaireEnchantement, [int] -> bool
    Regarde si l'une amélioration appartient au Gestionnaire d'enchantement"""
    return any([possède_amélioration(gestionnaire_enchantement, i) for i in liste_id])

def nombre_améliorations(gestionnaire_enchantement: GestionnaireEnchantement, liste_id):
    """ GestionnaireEnchantement, [int] -> bool
    Regarde le nombre d'amélioration qui appartiennent au Gestionnaire d'enchantement"""
    return sum([possède_amélioration(gestionnaire_enchantement, i) for i in liste_id])

def trouver_bouton(liste_bouton, id):
    """ [Bouton], int -> Bouton
    Renvoie le bouton qui correspond à l'amélioration d'id `id` """
    for bouton in liste_bouton:
        if bouton.texte == f'{id}':
            return bouton

def prix_total(a, id_object):
    """ Noeux, int -> int
    Renvoie le prix pour accèder à une amélioration"""

    if est_vide(a): #Objet n'a pas été trouvé
        return float("inf")
    if etiquette(a)==id_object:
        return amélioration[etiquette(a)][1]
    p_min = min(prix_total(gauche(a), id_object), prix_total(droit(a), id_object))
    if etiquette(a) in [71, 72]:
        p_min = min(p_min, prix_total(gauche(a.teleport), id_object), prix_total(droit(a.teleport), id_object))

    return p_min + amélioration.get(etiquette(a), ("", 0))[1]

class Arbre_Amélioration(Scène):

    def initialiser(self):
        """ Arbre_Amélioration -> None
        Initialise Arbre_Amélioration. """

        global arbre, amélioration, option_suivante
        niveau = nb_niveaux(arbre)
        nombre_couples_frères_max = 2**(niveau-2)
        nombre_gros_séparateur = nombre_couples_frères_max - 1
        nombre_de_noueux = 2**(niveau-1)
        taille_amélioration = (taille_fenêtre - 2* Disposition.arbre_binaire("marge")) / (nombre_couples_frères_max*Disposition.arbre_binaire("espace_frères") + nombre_gros_séparateur*Disposition.arbre_binaire("espace_entre_branches") + nombre_de_noueux)

        self.liste_bouton = []
        self.couleur = []
        hauteur_y = taille_fenêtre - taille_amélioration - Disposition.arbre_binaire("marge_y")
        défilement_x = Disposition.arbre_binaire("marge")

        self.écran_noir = pygame.Surface((taille_fenêtre, taille_fenêtre), pygame.SRCALPHA)
        self.écran_noir.fill((200, 200, 200, 64))

        for i, (ag, ad) in enumerate(recupérer_niveau_tuple(arbre, niveau)):
            image_ag = amélioration.get(ag,("empty", 10))[0]
            image_ad = amélioration.get(ad,("empty", 10))[0]
            self.liste_bouton.append(Bouton("Mini", f"§{ad}§", image=charger_image(f"Amélioration/{image_ad}", taille_amélioration, taille_amélioration), largeur=taille_amélioration, hauteur=taille_amélioration, topleft=(défilement_x,hauteur_y)))
            if liste_paramètres.recupérer_paramètre("show_layout")>1: 
                self.couleur.append(((255,255,255), pygame.Rect(marge + défilement_x, hauteur_y, taille_amélioration, taille_amélioration)))
            if liste_paramètres.recupérer_paramètre("show_layout")>0: 
                self.couleur.append(((200,100,100), pygame.Rect(marge + défilement_x + taille_amélioration, hauteur_y, Disposition.arbre_binaire("espace_frères") * taille_amélioration, taille_amélioration)))
            défilement_x += (1 + Disposition.arbre_binaire("espace_frères")) * taille_amélioration
            self.liste_bouton.append(Bouton("Mini", f"§{ag}§", image=charger_image(f"Amélioration/{image_ag}", taille_amélioration, taille_amélioration), largeur=taille_amélioration, hauteur=taille_amélioration, topleft=(défilement_x,hauteur_y)))
            if liste_paramètres.recupérer_paramètre("show_layout")>1:
                self.couleur.append(((255,255,255), pygame.Rect(marge + défilement_x, hauteur_y, taille_amélioration, taille_amélioration)))
            if liste_paramètres.recupérer_paramètre("show_layout")>0 and i+1!=nombre_de_noueux//2: 
                self.couleur.append(((100,100,200), pygame.Rect(marge + défilement_x + taille_amélioration, hauteur_y, Disposition.arbre_binaire("espace_entre_branches") * taille_amélioration, taille_amélioration)))
            défilement_x += (1 + Disposition.arbre_binaire("espace_entre_branches"))* taille_amélioration
        
        if liste_paramètres.recupérer_paramètre("show_layout")>0:
            self.couleur.append(((100,100,0), pygame.Rect(marge, hauteur_y, Disposition.arbre_binaire("marge"), taille_amélioration)))
            self.couleur.append(((100,100,0), pygame.Rect(marge + taille_fenêtre - Disposition.arbre_binaire("marge"), hauteur_y, Disposition.arbre_binaire("marge"), taille_amélioration)))

        hauteur_y -= 1.2 * taille_amélioration
        
        taille = taille_fenêtre - Disposition.arbre_binaire("marge")
        niveau-=1
        while niveau>1:

            nombre_de_noueux = 2**(niveau-1)
            hauteur_y -= taille_amélioration
            for i, k in enumerate(recupérer_niveau(arbre, niveau)):
                lien_image = amélioration.get(k,("empty", 10))[0]
                self.liste_bouton.append(Bouton("Mini", f"§{k}§", charger_image(f"Amélioration/{lien_image}", taille_amélioration, taille_amélioration), largeur=taille_amélioration, hauteur=taille_amélioration, topleft=(taille/nombre_de_noueux * (i + 0.5),hauteur_y)))
            
            hauteur_y -= 1.2 * taille_amélioration
            niveau -= 1

        global sous_scène
        sous_scène = True
        
    def action(self):
        """ Arbre_Amélioration -> None
        Gère l'écran d'amélioration """
        self.afficher()
        self.boucle_événements()

    def afficher(self):
        """ Arbre_Amélioration -> None
        Affiche l'écran d'amélioration """

        global arbre, amélioration, option_suivante, noeux_actuel

        afficher(self.écran_noir, (0, taille_fenêtre//1.8))
        for bouton in self.liste_bouton:
            """if self.option_suivante is not None and bouton in [(trouver_bouton(self.liste_bouton, etiquette(noeux)),noeux) for noeux in self.option_suivante]:
                bouton.fond = (80,80,255,80)
            else:
                bouton.fond = (255,255,255,80)
            bouton.mise_à_jour_interface()"""
            bouton.afficher()
            if bouton.bouton_touché() and not int(bouton.texte) in joueur.enchantements.liste_enchantements and option_suivante is not None and int(bouton.texte) in liste_possibilité(noeux_actuel):
                couleur = (80,200,80)
                if gold<prix_total(noeux_actuel, int(bouton.texte))-amélioration.get(etiquette(noeux_actuel), ('',0))[1]:
                    couleur = (200,120,80)
                if not int(bouton.texte) in [etiquette(i) for i in option_suivante]:
                    r,g,b = couleur
                    couleur = (r//2,g//2,b//2)
                texte = f"§{amélioration[int(bouton.texte)][1]}g§"
                
                if not int(bouton.texte) in [etiquette(i) for i in option_suivante]:
                    texte = f"§{amélioration[int(bouton.texte)][1]}g ({prix_total(noeux_actuel, int(bouton.texte))-amélioration.get(etiquette(noeux_actuel), ('',0))[1]})§"
                b = Bouton("Mini", texte, background= couleur, largeur=bouton.largeur*2.5, hauteur=bouton.hauteur, center=(bouton.coordonnées[list(bouton.coordonnées.keys())[0]][0]+bouton.hauteur*0.75, bouton.coordonnées[list(bouton.coordonnées.keys())[0]][1]+bouton.hauteur*1.5))
                b.afficher()

        for i,bouton in enumerate([copier_class(trouver_bouton(self.liste_bouton, id_amé)) for id_amé in joueur.enchantements.liste_enchantements]):
            bouton.coordonnées = {"topright":(taille_fenêtre*0.95-(i*bouton.largeur*1.2), taille_fenêtre*0.05)}
            bouton.mise_à_jour_interface()
            bouton.afficher()
        for k,v in self.couleur:
            pygame.draw.rect(fenêtre, k, v)

        #print(joueur.inventaire.armes.tete().puissance)
    def boucle_événements(self):
        """ Arbre_Amélioration -> None
        Gère la boucle des événements de pygame pour l'écran de l'arbre d'amélioration. """

        global arbre, amélioration, option_suivante, noeux_actuel
        for événement in pygame.event.get():
            if fenêtre_fermée(événement):
                quitter()
            
            elif souris_déplacée(événement):
                global position_souris
                position_souris = événement.pos
            
            elif touche_pressée(événement, [pygame.K_ESCAPE]):
                global scène, actualiser_nouvelle_scène
                actualiser_nouvelle_scène, scène = False, "Niveau"
            elif souris_est_pressée(événement) and option_suivante is not None:
                global gold
                for bouton, noeux_id in [(trouver_bouton(self.liste_bouton, etiquette(noeux)),noeux) for noeux in option_suivante]:
                    if bouton.bouton_touché() and (amélioration[etiquette(noeux_id)][1]<=gold or liste_paramètres.recupérer_paramètre("infgold")):
                        if etiquette(noeux_id) in [81, 82, 83]:
                            l = ((set(récuperer_toute_les_valeurs(arbre)) ^ set(([0] + joueur.enchantements.liste_enchantements))) ^ set([etiquette(i) for i in option_suivante])) ^ set([71, 72, 13, 9, 51, 52])

                            joueur.enchantements.ajouter_enchantement(random.choice(list(l)))
                            gold -= amélioration[etiquette(noeux_id)][1]

                            if est_vide(gauche(noeux_id)):
                                option_suivante = None
                            else:
                                option_suivante = [gauche(noeux_id), droit(noeux_id)]
                            
                        elif etiquette(noeux_id)==9: #RESET
                            global scènes
                            Partie.initialiser_arbre(Partie)
                            scènes[scène].initialiser()
                            joueur.enchantements.liste_enchantements = []
                            return
                        else:
                            noeux_actuel = noeux_id
                            
                            if etiquette(noeux_id) in [51, 52]:
                                joueur.inventaire.enfiler(Arme("Soin"))
                                joueur.enchantements.ajouter_enchantement(etiquette(noeux_id))
                            elif etiquette(noeux_id) in [13]:
                                joueur.statistiques.vie.division -= 2
                                joueur.enchantements.ajouter_enchantement(etiquette(noeux_id))
                            else : 
                                joueur.enchantements.ajouter_enchantement(etiquette(noeux_id))
                                gold -= amélioration[etiquette(noeux_id)][1]

                            if est_vide(gauche(noeux_id)):
                                option_suivante = None
                            elif etiquette(noeux_id) in [71, 72]:
                                option_suivante = [gauche(noeux_id), droit(noeux_id), gauche(noeux_id.teleport), droit(noeux_id.teleport)]
                            else:
                                option_suivante = [gauche(noeux_id), droit(noeux_id)]
                        



class Langue:
    
    def __init__(self, adresse):
        self.adresse = adresse
    
    @property
    def valeur(self):
        global liste_paramètres
        with open("Ressources/Données Textuel/Traductions.json", "r", encoding="utf-8") as f:
            return json.load(f)[self.adresse][liste_paramètres.recupérer_paramètre("language")]
    
class Données_Paramètres:
    """ Représente les paramètres du jeu. """
    
    def initialiser(self):
        """ Paramètres -> None """

        for k, v in {"audio_son": 50, "audio_musique": 50, "audio_global": 50, "déplacement_devant": ["up", "z"], "déplacement_arrière": ["down", "s"], "déplacement_gauche": ["left", "q"], "déplacement_droite": ["right", "d"], "inventory": ["e", None],"fullscreen": True, "lighting": 100, "game_quality":2, "minimap":["m", None],"show_difficulty": False, "monster_number": None, "show_layout":0, "freecam":False, "show_damage":False, "godmode":False, "visionIR":False, "noclip":False, "language":"fr", "upgrade":["i", None], "show_number_damage":False, "infgold":False}.items():
            setattr(self, k, v)

    def __init__(self):
        """ Données_Paramètres -> None """
        
        self.chemin = "paramètres.txt" #TEMPORAIRE
        self.initialiser()

        global première_fois

        if os.path.exists(self.chemin):
            première_fois = False

            with open(self.chemin,"r",encoding="utf-8") as f:
                lignes = f.readlines()
            
            for ligne in lignes : 
                if len(ligne.split("="))==2:
                    setattr(self,ligne.split("=")[0].removesuffix(" "),eval(ligne.split("=")[1].removeprefix(" ").removesuffix("\n")))
        
        else:
            première_fois = True

        self.enregistrer()

    def enregistrer(self):
        """ Données_Paramètres -> None
        Enregistre les paramètres dans un fichier texte. """

        with open(self.chemin,"w",encoding="utf-8") as f:
            for keys,values in self.__dict__.items():
                if keys!="chemin":
                    if type(values) == str:
                        values = f"\'{values}\'"
                    f.write(f"{keys} = {values}\n")
    
    @classmethod
    def touché_pressé(self, touche_attribut, événement):
        """ Données_Paramètres, str, pygame.Event -> bool
        Renvoie si la touche pressé `événement` correspont à la touche qui correspond à la touche enregistrer en paramètre pour le paramètre `touche_attribut`."""
        
        if événement.type != pygame.KEYDOWN:
            return False
        for touche in getattr(liste_paramètres, touche_attribut):
            if touche != None and pygame.key.name(événement.key) == touche:
                return True
        return False
    
    @classmethod
    def touché_pressé_clavier(self, touche_attribut):
        """ Données_Paramètres, str -> bool
        Renvoie si la touche pressé `évenement` correspont à la touche qui correspond à la touche enregistrer en paramètre pour le paramètre `touche_attribut`."""
        
        global clavier
        for touche in getattr(liste_paramètres, touche_attribut):
            if touche != None and clavier[pygame.key.key_code(touche)]:
                return True
        return False
    
    @classmethod
    def recupérer_paramètre(self, paramètres, ini=True):
        """ Données_Paramètres, str, bool -> Any
        Renvoie la valeur associé à un paramètres. `ini` sert à savoir si les paramètres ont été initialiser"""
        
        global liste_paramètres
        return getattr(liste_paramètres, paramètres)

def afficher_chargement():   
    """ () -> None
    Affiche un écran de chargement. """

    fenêtre.fill((0, 0, 0))
    chargement.modifier_texte(f"Chargement§{'.'*(int(chronomètre.temps_écoulé())%3+1)}§")
    chargement.afficher()
    pygame.display.flip()

class Chronomètre:
    """ Représente un chronomètre qui regarde le temps écoulé """

    def __init__(self):
        """ Chronomètre -> None """

        self.début = time.monotonic()
        self.temps_en_pause = 0
        self.en_pause = False
        self.début_pause = None

    def pause(self):
        """ Chronomètre -> None
        Met le chronomètre `self` en pause. """

        if not self.en_pause:
            self.début_pause = time.monotonic()
            self.en_pause = True

    def continuer(self):
        """ Chronomètre -> None
        Enlève la pause du chronomètre `self`. """

        if self.en_pause:
            self.temps_en_pause += time.monotonic() - self.début_pause
            self.en_pause = False

    def temps_écoulé(self, en_pause: bool = False) -> float:
        """ Chronomètre, bool -> float
        Renvoie le décompte du temps du chronomètre `self`. """

        if en_pause:
            return self.temps_en_pause + time.monotonic() - self.début_pause

        if self.en_pause:
            return self.début_pause - self.début - self.temps_en_pause
        
        return time.monotonic() - self.début - self.temps_en_pause

jeu = Jeu()
if __name__ == "__main__":
    jeu.jouer()
else:
    global données_scène_suivante
    données_scène_suivante = {
        "joueur": "Yann",
        "récompense": "Coffre",
        "pnj": "Ciceron"
    }
