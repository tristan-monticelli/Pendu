"""Configuration globale du jeu du Pendu"""

import os

#--------------------------------------Chemins--------------------------------------#

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PATHS = {
    "mots": os.path.join(BASE_DIR, "data", "mots.txt"),
    "leaderboard": os.path.join(BASE_DIR, "data", "leaderboard.txt"),
    "assets": os.path.join(BASE_DIR, "assets"),
    "images": os.path.join(BASE_DIR, "assets", "images"),
    "fonts": os.path.join(BASE_DIR, "assets", "fonts"),
    "sounds": os.path.join(BASE_DIR, "assets", "sounds"),
}

#--------------------------------------Affichage--------------------------------------#

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BACKGROUND_COLOR = "#193CA3"

#--------------------------------------Jeu--------------------------------------#

# Normal: 6 vies (tete, corps, bras G, bras D, jambe G, jambe D)
# Difficile: 4 vies (tete, corps, 2 bras ensemble, 2 jambes ensemble)
MAX_ERRORS_NORMAL = 6
MAX_ERRORS_HARD = 4
MAX_HINTS = 3

#--------------------------------------Polices--------------------------------------#

FONT_NAME = "Simpsonfont DEMO.otf"

FONT_SIZES = {
    "small": 16,
    "medium": 24,
    "large": 36,
    "title": 48,
}

#--------------------------------------Pseudo--------------------------------------#

PSEUDO_MIN_LENGTH = 1
PSEUDO_MAX_LENGTH = 15
PSEUDO_FORBIDDEN_CHARS = [";", "\n", "\t"]
