# The Legend of M.Picard.

Ce projet est un jeu d'aventure inspiré du fameux jeu "*Piotr, l'explorateur de labyrinthes*" développé avec la bibliothèque graphique *Pygame* et du module *SQLite* qui permet l'accès à une interface SQL. L'objectif de ce projet est d'utiliser les notions vues en cours ce trimestre, notamment le SQL, pour construire un jeu vidéo ; tout en rendant homage à ce jeu oublié, codé en seulement six petites heures.

##  Installation des outils nécessaires

###  Prérequis

Avant de lancer le jeu, assurez vous d'avoir **Python 3** installé sur votre ordinateur. Vous pouvez télécharger Python à partir du site officiel : [https://www.python.org/downloads/](https://www.python.org/downloads/).

###  Installation de Pygame

Pour exécuter ce projet, vous devez installer **Pygame**. Voici les étapes pour installer Pygame :

1. Ouvrez un *terminal* ou une *invite de commande*.

2. Exécutez la commande suivante pour installer Pygame via `pip`, le gestionnaire de paquets Python :

```bash
pip install pygame
```

Cette commande téléchargera et installera automatiquement Pygame pour votre version de Python.

##  Utilisation du programme

### Intro

Lorsque vous lancez le jeu pour la première fois, une cinématique apparaît. Pour passer à l'image suivante, il suffit de cliquer n'importe où. Cette cinématique ne se lance qu'une seule fois (lorsque le fichier paramètre.txt n'existe pas), alors profitez-en !

### Menu

A la fin de la cinémtique, on arrive sur le `Menu`. Dans celui-ci on peut appuyer sur `Jouer` pour accéder à l'écran `Sélection du Personnage` ou sur `Paramètres` pour accéder aux `Paramètres`.

### Sélection du Personnage

Ce menu nous montre l'ensemble des **44 Personnages** jouables dans ce jeu. Ceux-ci sont répartis en deux pages qu'on peut naviguer à l'aide des flèches en bas de l'écran. On peut retourner au menu en appuyant sur `Menu` et accéder aux `Paramètres` en appuyant sur `Paramètres`. Cliquer sur un personnage le sélectionne immédiatement et lance la `Partie`.

### Partie

#### Objectif

La partie est composée d'un ensemble de **15 `Niveaux`** représentant les matières scolaires accompagnés d'un dernier `Niveau` pour finaliser la partie.

Pour gagner une partie, il suffit de finir le dernier `Niveau`. Cependant pour y accéder, il faut déjà avoir fini les 15 précédents niveaux rangés dans une Pile de manière aléatoire. Le premier `Niveau` se lance automatiquement après un chargement.

#### Informations

Vous incarnez le Personnage que vous avez sélectionné dans l'écran de `Sélection du Personnage`. Celui possède au moins un monde, c'est-à-dire au moins une matière scolaire. Celui se vera aussi attribuer une arme, parfois fixe, parfois aléatoire.

Vous avez un Inventaire et des Statistiques qui restent les même entre les `Niveaux`.

### Niveau

#### Apparition

Vous apparaissez dans un Donjon labyrinthique composé de Salles, elles-mêmes composées de Cases.

#### Contrôles

Vous pouvez déplacer à l'aide des contrôles définis dans les paramètres, mais ceux-ci sont, par défaut, ZQSD et les flèches directionnels.

Vous pouvez accéder à l'`Inventaire` à l'aide des contrôles définis dans les paramètres, mais ceux-ci sont, par défaut, la touche E.

Vous pouvez attaquer à l'aide la souris. Cliquer avec celle-ci déclenchera une attaque dans la direction pointée, si c'est une arme de contact, à l'endroit pointé, si c'est une arme de distance, ou invoquera des projectiles ou des monstres, dans les autres cas.

Vous pouvez accéder à l'écran d'`Amélioration` à l'aide des contrôles définis dans les paramètres, mais ceux-ci sont, par défaut, la touche I.

Pour accéder à l'écran de `Dialogue` d'un PNJ, il faut être à côté de lui et avancer vers lui.

Vous pouvez accéder à l'écran de `Pause` en appuyant sur la touche échap.

#### Salle

Les Salles peuvent posséder un Motif qui change l'aspect de la Salle en rajoutant des murs par exemple.

Lorsque vous entrez dans une salle non libérée, un combat se lance.

##### Salle classique

Les Salles classiques sont les plus courantes dans le Donjon. Elles contiennent plus ou moins d'ennemis en fonction de la "distance" de la Salle au centre du Donjon, c'est-à-dire le nombre minimum de salle par lequel il faut passer pour arriver à cette Salle donnée. Il y a un total de **38 Ennemis**.

Il faut attaquer pour infliger des dégâts aux ennemis jusqu'à les tuer. Une fois que tous les ennemis sont morts, une Récompense apparait au centre. Elle se matérialise sous la forme d'un Coffre, d'une Fontaine ou bien d'une Épée dans un Rocher.

Pour accéder à l'écran de `Récompense` d'une Récompense, il faut être à côté d'elle et avancer vers elle.

##### Salle de Boss

Il n'y a qu'une Salle de Boss par `Niveau`. Celle-ci contient un Monstre de type Boss. Celui a plus d'attaques que les Monstres habituels et possède des armes exclusives au personnage du Boss et une arme d'Invocation supplémentaire.

Une fois le Boss tué, la Sortie apparait. Celle-ci te mène au prochain `Niveau`.

### Pause

Durant votre partie, vous pouvez appuyez sur la touche Échap afin d'aller dans le menu Pause.
Appuyer sur `Continuer` pour accéder à la `Partie`.
Appuyer sur `Paramètres` pour accéder au `Paramètres`.
Appuyer sur `Menu` pour accéder au `Menu`.

### Paramètres

Vous pouvez modifier la Langue parmi les **9 Langues** disponibles.
Vous pouvez modifier l'Audio.
Vous pouvez modifier l'Affichage.
Vous pouvez modifier les Contrôles.
Vous pouvez modifier le méthodes utilisées pour Débuger le jeu.

### Inventaire

L'inventaire du joueur est représenté sous la forme d'une File. Le bouton `Défiler` enlève l'Arme en tête de File. Lorsqu'on gagne une Arme, elle se rajoute en bout de File.

### Amélioration 

A chaque partie l'utilisateur peut acheter sous forme d'un `arbre binaire` des améliorations. Elle s'achete avec du `gold` qu'on obtient en tuant des monstres et passant des récompenses (coffre, épée dans le rocher)

Vous pouvez votre le prix de l'amélioration en passant votre souris dessus, ainsi que le `gold` a déboursé pour l'obtenir (il faut parfois avoir obtenu certaines améliorations au préalable). Si vous ne pouvez pas l'obtenir l'amélioration alors le prix ne sera pas indiquer 

Chaque compétences est inédite. Elle affecte votre jeu positivement il faut les choisir avec sagesse.

Voici une liste non-exhaustive d'amélioration : 
 - **Rage (15g) :** Lorsque le joueur prend des dégats, il lance une salve de flèche qui impacte les monstres autours.
 - **Vampire (20g + 5 par niveau) :** vole **7%** de la vie du monstre touché
 - **Bourse d'or (25g) :** Tous les 5 monstres tué, `1` de gold suplémentaire est obtenu. De plus, les coffres octroie `1` de gold de plus lorsque la récompenses est passé (ce qui revient à un total de **3g**)

Précision sur l'utlisation de l'arbre des compétences :

L'amélioration choisie doit décendre des sous-arbres
L'arbre a 2 améliorations **téléportation**, qui ne font rien mais qui permet de changer l'arbre si souhaité

### Récompense

#### Coffre

Vous pouvez choisir entre trois armes à ajouter à votre Inventaire. Vous pouvez passer pour remportez du `gold` et relancer pour changer les armes distribuées. Il y a un total de **42 Armes** à récolter.

#### Fontaine

Soigne jusqu'au prochain palier de vie.

#### Épée dans le Rocher

Vous pouvez choisir entre deux statistiques à améliorer. Vous pouvez passer pour remportez du `gold` et relancer pour changer les améliorations distribuées.

### Mort

Lorsqu'on a plus de vie, on accède à l'écran de mort.

Il faut appuyer sur `Rejouer` pour recommencer une partie.

Il faut appuyer sur `Menu` pour accéder au `Menu`.

### Fin

Après avoir battu le Boss du dernier monde, vous accédez à l'écran de fin.

Appuyez n'importe où sur l'écran pour accéder au `Menu`.

##  Bugs connus

aucun bug connu

##  Évolutions possibles

- Ajouter un système de sauvegarde de données à l'aide de SQL.
- Ajouter des descriptions pour chacun des personnages.
- Ajouter d'autres systèmes d'amélioration du personnage pour compléter les Récompenses et l'écran d'Amélioration.