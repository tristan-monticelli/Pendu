"""
settings.py — Configuration globale du jeu Pendu (DA Simpson)

Rôle du fichier
- Centraliser toutes les constantes et réglages du projet au même endroit.
- Éviter d'avoir des valeurs "en dur" dispersées dans le code (tailles, couleurs, chemins...).
- Faciliter les ajustements de design (DA), de layout (positions/tailles) et de gameplay.

Ce que ce fichier doit contenir
- Uniquement des constantes et des petits helpers simples (ex: calcul de largeur de colonne).
- Des chemins vers les ressources (assets), des paramètres d'affichage, des couleurs, etc.
- Pas de logique métier du jeu (pas de règles de pendu, pas de scènes, pas d'I/O complexe).

Organisation
Le fichier est volontairement découpé en sections :
1) Chemins (data + assets)
2) Affichage (résolution, fps, fullscreen)
3) Couleurs (palette Simpson + UI + états)
4) Typographie (police + tailles)
5) Grille / layout (marges, colonnes, ratios d'écran)
6) Style (bordures, arrondis, ombres)
7) UI (dimensions boutons, couleurs boutons)
8) Gameplay (difficultés, erreurs max, indices)
9) Validation pseudo (longueur + caractères interdits)
10) Animations (timings)
11) Alphabet (disposition + tailles)
12) Assets (chemins images + tailles de référence)
13) Classement (options d'affichage)
14) Debug (flags)

Remarque
- Beaucoup de valeurs sont calibrées pour une résolution de référence 1920x1080.
  Si on change cette base, il faudra vérifier le rendu et les ratios dans les scènes.
"""

from __future__ import annotations
from pathlib import Path
import pygame

"""
CHEMINS :
Objectif : définir ici tous les chemins utiles (fichiers data, images, fonts, sons).
Comme ça, le reste du projet n'a qu'à importer les constantes et n'a jamais besoin
de reconstruire des chemins à la main.
"""
# Dossier racine du projet = dossier où se trouve ce fichier settings.py
PROJECT_ROOT = Path(__file__).resolve().parent

# Dossier "data" : fichiers texte/stockage (mots, leaderboard, etc.)
DATA_DIR = PROJECT_ROOT / "data"

# Fichiers data principaux (convertis en str pour compatibilité avec les appels I/O)
WORDS_PATH = str(DATA_DIR / "mots.txt")
LEADERBOARD_PATH = str(DATA_DIR / "leaderboard.txt")

# Dossier "assets" : toutes les ressources graphiques/sonores/polices
ASSETS_DIR = PROJECT_ROOT / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
FONTS_DIR = ASSETS_DIR / "fonts"
SOUNDS_DIR = ASSETS_DIR / "sounds"

# Musique de fond (jouée en boucle dans le menu / pendant le jeu selon l'implémentation)
MUSIC_PATH = str(SOUNDS_DIR / "background_music.mp3")

# Volume de la musique : valeur entre 0.0 (muet) et 1.0 (max)
MUSIC_VOLUME = 1.0

# Effets sonores (sons "évènementiels" du personnage Trump)
# Les clés servent d'identifiants dans le code (ex: SOUND_PATHS["trump_angry"])
SOUND_PATHS = {
    "trump_angry": str(SOUNDS_DIR / "trump_angry.mp3"),
    "trump_sad": str(SOUNDS_DIR / "trump_sad.mp3"),
    "trump_dead": str(SOUNDS_DIR / "trump_dead.mp3"),
}

# Volume des effets sonores : même principe que MUSIC_VOLUME
SOUND_VOLUME = 1.0

"""
AFFICHAGE - HAUTE QUALITÉ : 
Ici on définit la "résolution de référence" (base de calibrage du design).
Beaucoup d'éléments (tailles polices, boutons, spacing...) ont été choisis pour
une fenêtre Full HD afin d'avoir un rendu propre et lisible.
"""
# Résolution de référence utilisée pour calibrer le design (base du layout)
REFERENCE_WIDTH = 1920
REFERENCE_HEIGHT = 1080

# Mode d'affichage général
# FULLSCREEN à False : fenêtré par défaut (plus simple pour debug/développement)
FULLSCREEN = False
FPS = 60

# Résolution effective de la fenêtre.
# Par défaut on prend la référence. Certaines parties du code peuvent l'ajuster
# au démarrage (ex: si on décide d'adapter à l'écran).
WINDOW_WIDTH = REFERENCE_WIDTH
WINDOW_HEIGHT = REFERENCE_HEIGHT


"""
PALETTE SIMPSON - COULEURS OFFICIELLES : 
Toutes les couleurs du projet sont regroupées dans un dictionnaire.
Le but :
- avoir des noms explicites (pas de (255, 217, 15) dispersés partout),
- faciliter les changements de DA,
- garantir une cohérence graphique (mêmes teintes partout).
"""
COLORS = {
    # Couleurs "iconiques" de la DA Simpson
    "simpson_yellow": (255, 217, 15),      # Jaune peau
    "simpson_blue": (108, 180, 238),       # Bleu ciel
    "simpson_sky": (126, 192, 238),        # Variante ciel Springfield

    # Backgrounds / fonds généraux
    "bg_sky": (135, 206, 235),             # Ciel principal
    "bg_clouds": (255, 255, 255),          # Nuages
    "bg_grass": (144, 238, 144),           # Herbe
    "bg_card": (255, 235, 153),            # Jaune pâle cards (conteneurs)
    "bg_dark": (30, 30, 30),               # Fond sombre pour contraste

    # UI Elements (contours/ombres)
    "border_black": (0, 0, 0),             # Contours noirs épais
    "shadow": (0, 0, 0),                   # Base ombre (alpha géré ailleurs)

    # Accents colorés (feedback, états, éléments visuels)
    "pink_donut": (255, 105, 180),
    "purple_marge": (123, 104, 238),
    "orange_homer": (255, 140, 0),
    "red_error": (255, 0, 0),
    "green_success": (0, 255, 0),
    "blue_info": (65, 105, 225),

    # Couleurs texte (principale + contraste + secondaire)
    "text_black": (0, 0, 0),
    "text_white": (255, 255, 255),
    "text_shadow_blue": (0, 0, 255),       # Ombre bleue (style cartoon)
    "text_gray": (128, 128, 128),
    "text_indice": (102, 0, 153),          # Violet foncé (lisible sur fond clair)

    # États des lettres (alphabet)
    # - available : pas encore cliquée
    # - correct : lettre trouvée
    # - wrong : lettre fausse
    "letter_available": (255, 255, 220),
    "letter_correct": (180, 230, 180),
    "letter_wrong": (255, 180, 180),

    # Couleurs "pâles" dédiées aux boutons (cohérence UI + lisibilité texte)
    "btn_yellow_pale": (255, 245, 180),
    "btn_green_pale": (180, 230, 180),
    "btn_blue_pale": (180, 210, 255),
    "btn_orange_pale": (255, 210, 160),
    "btn_red_pale": (255, 180, 180),
    "btn_pink_pale": (255, 200, 220),
}


"""
TYPOGRAPHIE : 
Ce bloc définit la police principale (DA Simpson) et les tailles utilisées.
On préfère des tailles nommées ("tiny", "title"...), car c'est plus lisible
dans le code que des nombres.
"""
# Police Simpson stockée dans assets/fonts
FONT_SIMPSON = "Simpsonfont DEMO.otf"
FONT_PATH = str(FONTS_DIR / FONT_SIMPSON)

# Tailles de police calibrées pour 1920x1080 (haute lisibilité)
# Chaque valeur correspond à une intention :
# - tiny/small : labels secondaires
# - body : texte standard (UI + infos)
# - large/title/huge : titres, écrans d'accueil, etc.
FONT_SIZES = {
    "tiny": 24,
    "small": 32,
    "body": 40,
    "large": 56,
    "title": 80,
    "huge": 120,
}


"""
GRID SYSTEM - Layout précis : 
Le but ici est d'avoir une base "grille" pour positionner proprement les éléments,
surtout sur les écrans à haute résolution.
Même si toutes les scènes ne l'utilisent pas directement, ces constantes donnent
une cohérence : mêmes marges, mêmes espacements, etc.
"""
# Marges/espacements (en pixels pour la résolution de référence)
MARGIN_SCREEN = 60
PADDING_CARD = 50
GAP_ELEMENTS = 35
GAP_BUTTONS = 24

# Grille 12 colonnes (standard UI)
GRID_COLUMNS = 12
GRID_GUTTER = 30


def get_column_width(screen_width=REFERENCE_WIDTH):
    """
    Calcule la largeur d'une colonne dans une grille 12 colonnes.

    Principe
    - On réserve d'abord les marges gauche/droite (MARGIN_SCREEN).
    - On retire ensuite les espacements entre colonnes (gouttières / GRID_GUTTER).
    - Le reste est divisé en GRID_COLUMNS colonnes de largeur égale.

    Paramètres
    - screen_width : largeur de l'écran (ou de la fenêtre) en pixels.

    Retour
    - float : largeur d'une colonne (peut être non entière, selon la division).
    """
    usable_width = screen_width - (2 * MARGIN_SCREEN)
    return (usable_width - (GRID_GUTTER * (GRID_COLUMNS - 1))) / GRID_COLUMNS


"""
ZONES DE LAYOUT (pourcentages de l'écran) : 
Ces ratios servent à découper l'écran en grandes zones (header / zone de jeu / footer).
L'intérêt : on raisonne en proportions plutôt qu'en pixels fixes, ce qui aide
si on adapte plus tard à d'autres tailles d'écran.
"""
LAYOUT = {
    # Bandeau du haut (titre, infos rapides)
    "header_height_ratio": 0.10,

    # Zone de jeu principale (pendu + informations + alphabet)
    "game_area_height_ratio": 0.70,
    "pendu_width_ratio": 0.45,
    "info_width_ratio": 0.50,

    # Zone basse (boutons, actions)
    "footer_height_ratio": 0.20,
}


"""
STYLE CARTOON - Paramètres visuels : 
Règles de style pour obtenir un rendu "cartoon" (Simpson-like) :
- contours épais et noirs
- coins arrondis
- ombres simples (décalage + alpha)
"""
BORDER_WIDTH_THIN = 2
BORDER_WIDTH_NORMAL = 4
BORDER_WIDTH_THICK = 6

CORNER_RADIUS_SMALL = 10
CORNER_RADIUS_NORMAL = 20
CORNER_RADIUS_LARGE = 30

# Ombres : décalage (px) + alpha (0-255). La couleur de base est COLORS["shadow"].
SHADOW_OFFSET = 6
SHADOW_ALPHA = 100


"""
BOUTONS - Dimensions et styles : 
Les tailles de boutons sont normalisées pour éviter des boutons "au hasard"
selon les écrans/scènes. On choisit ensuite une taille en fonction du contexte.
"""
BUTTON_SIZES = {
    "large": (400, 100),      # Boutons principaux menu
    "normal": (300, 80),      # Boutons standards
    "small": (200, 60),       # Petits boutons
    "compact": (150, 50),     # Très petits boutons
}

# Couleurs "sémantiques" : utilisées selon le type d'action
# - primary : action principale
# - danger : action risquée / erreur
# - success : validation / victoire
BUTTON_COLORS = {
    "primary": COLORS["simpson_yellow"],
    "secondary": COLORS["simpson_blue"],
    "danger": COLORS["red_error"],
    "success": COLORS["green_success"],
    "info": COLORS["blue_info"],
}


"""
JEU - Paramètres de gameplay : 
Cette section regroupe ce qui impacte les règles du pendu.
Ici, on fixe les difficultés, les erreurs max, et les indices.
"""
# Difficultés disponibles (valeurs attendues par le reste du projet)
DIFFICULTIES = ["FACILE", "MOYEN", "DIFFICILE"]
DEFAULT_DIFFICULTY = "MOYEN"

# Consigne projet : peu importe la difficulté, on a toujours 7 erreurs max
# (la difficulté peut plutôt jouer sur le choix des mots et l'aide éventuelle).
MAX_ERRORS_BY_DIFFICULTY = {
    "FACILE": 7,
    "MOYEN": 7,
    "DIFFICILE": 7,
}

# Indices : utilisés uniquement en FACILE selon le design prévu
MAX_HINTS = 3


"""
PSEUDO - Validation : 
Règles simples pour le pseudo joueur.
Objectif : éviter des pseudos vides, trop longs, ou contenant des caractères
qui cassent le parsing du leaderboard (ex: ';' si on stocke en CSV-like).
"""
PSEUDO_MIN_LEN = 1
PSEUDO_MAX_LEN = 16
PSEUDO_FORBIDDEN_CHARS = [";", "\n", "\r", "\t"]


"""
ANIMATIONS - Timings (en millisecondes)
Dictionnaire des durées/temps utilisés par les animations UI.
Ex : toasts (messages temporaires), hover des boutons, shake sur erreur, etc.
"""
ANIM_TIMINGS = {
    "toast_duration": 2000,
    "button_hover": 100,
    "letter_pop": 150,
    "shake_duration": 300,
    "fade_in": 400,
}


"""
ALPHABET - Configuration :
Configuration de l'alphabet affiché à l'écran.
On stocke :
- la liste des lettres possibles
- une disposition "clavier" (AZERTY) sur plusieurs lignes
- la taille des cases + l'espacement (lisibilité/accessibilité)
"""
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ALPHABET_LAYOUT = [
    "AZERTYUIOP",
    "QSDFGHJKLM",
    "WXCVBN"
]

# Dimensions des touches alphabet (pensées pour être cliquables facilement)
LETTER_BOX_SIZE = 80
LETTER_SPACING = 16


"""
ASSETS - Chemins vers les images : 
Dictionnaire central pour retrouver facilement les images.
Les clés sont des identifiants utilisés dans le code, les valeurs sont les chemins.
Important : si un nom de fichier change dans assets, on corrige ici, pas ailleurs.
"""
ASSETS_PATHS = {
    # Trump (têtes / émotions)
    "trump_happy": str(IMAGES_DIR / "Trump" / "Head" / "Happy.png"),
    "trump_angry": str(IMAGES_DIR / "Trump" / "Head" / "Angry.png"),
    "trump_sad": str(IMAGES_DIR / "Trump" / "Head" / "Sad.png"),
    "trump_dead": str(IMAGES_DIR / "Trump" / "Head" / "Dead.png"),

    # Corps Trump (éléments séparés pour animation)
    "trump_body": str(IMAGES_DIR / "Trump" / "Body.png"),
    "trump_arm_left": str(IMAGES_DIR / "Trump" / "Arm-L.png"),
    "trump_arm_right": str(IMAGES_DIR / "Trump" / "Arm-R.png"),
    "trump_leg_left": str(IMAGES_DIR / "Trump" / "Limb-L.png"),
    "trump_leg_right": str(IMAGES_DIR / "Trump" / "Limb-R.png"),

    # Pendu (structures)
    "pendu_wood": str(IMAGES_DIR / "Pendu" / "Wood.png"),
    "pendu_metal": str(IMAGES_DIR / "Pendu" / "Metal.png"),

    # Vies (coeurs)
    "heart_full": str(IMAGES_DIR / "Gui" / "Health" / "Full.png"),
    "heart_empty": str(IMAGES_DIR / "Gui" / "Health" / "Empty.png"),

    # Indices (icônes)
    "hint_available": str(IMAGES_DIR / "Gui" / "Hint" / "New.png"),
    "hint_used": str(IMAGES_DIR / "Gui" / "Hint" / "Used.png"),
}

# Tailles de référence utilisées pour le scaling des assets.
# L'idée : on charge l'image puis on la redimensionne vers ces dimensions,
# afin d'avoir un rendu cohérent d'un écran à l'autre.
ASSET_SIZES = {
    "trump_head": (180, 180),
    "trump_body": (150, 150),
    "trump_arm": (150, 150),
    "trump_leg": (150, 150),
    "pendu": (500, 500),
    "heart": (50, 50),
    "hint": (50, 60),
}


"""
CLASSEMENT : 
Réglages pour l'affichage du leaderboard.
None signifie "on n'applique pas de limite" (on affiche tout ce qui est disponible).
"""
LEADERBOARD_TOP_N = None


"""
DEBUG : 
Flags pour activer des aides visuelles pendant le dev.
Ne doivent pas être True en version "rendu final" sauf si demandé.
"""
DEBUG_MODE = False
SHOW_FPS = False
 