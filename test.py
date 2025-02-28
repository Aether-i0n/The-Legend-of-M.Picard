from main import *

for scène in scènes.values():
    scène.initialiser()
    if type(scène) is Partie:
        scène.action()

# (function) est_visible
rectangle = pygame.Rect(0, 0, taille_case, taille_case)
assert not est_visible(rectangle)

from main import joueur

rectangle = pygame.Rect(joueur.x * taille_case, joueur.y * taille_case, taille_case, taille_case)
assert est_visible(rectangle)

# (function) coordonnées_réelles
réelles_x, réelles_y = coordonnées_réelles(0, 0)

# (function) coordonnées_en_jeu
en_jeu_x, en_jeu_y = coordonnées_en_jeu(0, 0)

assert réelles_x == -en_jeu_x and réelles_y == -en_jeu_y

# (function) compression
assert compression(10, 5, 15) == 10
assert compression(5, 10, 15) == 10
assert compression(15, 5, 10) == 10

# (function) distance
assert distance((0, 0), (0, 0)) == 0
assert distance((0, 0), (0, 1)) == 1
assert distance((0, 0), (1, 1)) == math.sqrt(2)

# (function) taille_arme
assert taille_arme("Epee") == (4. * taille_case, taille_case, 3.5 * taille_case, .5 * taille_case)

# (function) intéraction
assert intéraction(["SVT"], ["NSI"]) == 1.5
assert intéraction(["EPS"], ["SVT"]) == 1.

# (class) Bouton
bouton = Bouton("Titre", "§Test§", topleft=(0, 0))
assert bouton.style == "Titre"
assert bouton.texte_original == "§Test§"
assert bouton.texte == "Test"
assert bouton.coordonnées == {"topleft": (0, 0)}

# (class) Grille
grille = Grille()
for _ in range(5):
    grille.ajouter_ligne([i for i in range(5)])

assert grille.dans_la_grille(2, 3)
assert not grille.dans_la_grille(2, 6)
assert not grille.dans_la_grille(2, -1)

assert grille.récupérer(3, 3) == 3

grille.placer(3, 3, 49)
assert grille.récupérer(3, 3) == 49

assert grille.longueur() == 5
grille.ajouter_colonne([6 for i in range(5)])
assert grille.longueur() == 6

assert grille.hauteur() == 5
grille.ajouter_ligne([i for i in range(6)])
assert grille.hauteur() == 6

# Arbre binaire
f = File()
for i in range((2**4)-1):
    f.enfiler(i)
arbre = creer_arbre(f)

assert nb_niveaux(arbre) == 4

assert recupérer_niveau(arbre, 2) == [1, 2]
assert recupérer_niveau(arbre, 3) == [3, 4, 5, 6]

assert recupérer_niveau_tuple(arbre, 3) == [(3,4), (5,6)]

print("Exécuté sans erreur")