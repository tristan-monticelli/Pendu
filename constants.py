"""
constants.py

Ce fichier contient toutes les constantes globales du jeu.
Cela permet de s'assurer que tout le monde utilise les mêmes valeurs (taille écran, couleurs, etc.).
"""

# Dimensions de l'écran / Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Couleurs / Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Chemins des fichiers / File paths
# Chemins des fichiers / File paths
WORD_FILE = "mots.json"
SCORE_FILE = "scores.json"

# Paramètres du jeu / Game settings
MAX_LIVES = 7
TIME_LIMIT_HARD = 30
TIME_LIMIT_NORMAL = 60

# Niveaux de difficulté
DIFFICULTY = {
    "NORMAL": TIME_LIMIT_NORMAL,
    "HARD": TIME_LIMIT_HARD
}
