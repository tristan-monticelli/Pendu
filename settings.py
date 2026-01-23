"""
BUT DU FICHIER
- Mettre tous les réglages importants du projet au même endroit.
- Comme ça, si on veut changer la taille de la fenêtre, les chemins des fichiers,
  ou la difficulté, on ne cherche pas partout dans le code.

IMPORTANT
- Ici, on met pas de logique compliquée : uniquement des constantes (des "valeurs fixes").
- Les autres fichiers vont importer ces constantes.

CHANGEMENT CONSIGNE
- Peu importe la difficulté : 7 erreurs maximum (pas plus, pas moins).
- La difficulté sert uniquement à choisir les mots (et éventuellement l'affichage d'un indice).
"""

from __future__ import annotations

from pathlib import Path


"""
CHEMINS (où sont nos fichiers)
"""

# PROJECT_ROOT = dossier où se trouve settings.py
PROJECT_ROOT = Path(__file__).resolve().parent

# Dossier data/ (contient les fichiers textes)
DATA_DIR = PROJECT_ROOT / "data"

# Fichier des mots pour le pendu (format : DIFFICULTE;mot;indice?)
WORDS_PATH = str(DATA_DIR / "mots.txt")

# Fichier du classement (généré / mis à jour après les parties)
LEADERBOARD_PATH = str(DATA_DIR / "leaderboard.txt")


"""
FENÊTRE PYGAME (taille + FPS)
"""

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

FPS = 60


"""
TAILLES UI (boutons + champs texte)
"""

BTN_W = 320
BTN_H = 56

INPUT_W = 420
INPUT_H = 52


"""
PSEUDO (obligatoire avant de jouer)
"""

PSEUDO_MIN_LEN = 1
PSEUDO_MAX_LEN = 16

PSEUDO_FORBIDDEN_CHARS = [";", "\n", "\r"]


"""
DIFFICULTÉ (liste + erreurs autorisées)

CONSIGNE :
- peu importe la difficulté : 7 erreurs maximum
"""

DIFFICULTIES = ["FACILE", "MOYEN", "DIFFICILE"]
DEFAULT_DIFFICULTY = "MOYEN"

# On garde ce dictionnaire pour ne pas casser les imports existants,
# mais toutes les valeurs sont à 7 (consigne du sujet).
MAX_ERRORS_BY_DIFFICULTY = {
    "FACILE": 7,
    "MOYEN": 7,
    "DIFFICILE": 7,
}


"""
COULEURS (pour que tout soit cohérent)
"""

COLOR_BG = (18, 18, 18)
COLOR_TEXT = (230, 230, 230)
COLOR_MUTED = (170, 170, 170)

COLOR_BTN = (40, 40, 40)
COLOR_BTN_HOVER = (60, 60, 60)
COLOR_BTN_DISABLED = (30, 30, 30)

COLOR_INPUT_BG = (30, 30, 30)
COLOR_INPUT_BORDER = (90, 90, 90)
COLOR_INPUT_ACTIVE = (140, 140, 140)

COLOR_GOOD = (60, 190, 110)
COLOR_BAD = (220, 80, 80)


"""
POLICES (tailles, simple)
"""

FONT_SIZE_TITLE = 56
FONT_SIZE_BODY = 28
FONT_SIZE_SMALL = 20


"""
CLASSEMENT (optionnel)
"""

LEADERBOARD_TOP_N = None
