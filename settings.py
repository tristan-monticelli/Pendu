"""
BUT DU FICHIER
- Mettre tous les réglages importants du projet au même endroit.
- Comme ça, si on veut changer la taille de la fenêtre, les chemins des fichiers,
  ou la difficulté, on ne cherche pas partout dans le code.

IMPORTANT
- Ici, on met pas de logique compliquée : uniquement des constantes (des "valeurs fixes").
- Les autres fichiers vont importer ces constantes.
"""

from __future__ import annotations

from pathlib import Path


"""
CHEMINS (où sont nos fichiers)
"""

# PROJECT_ROOT = dossier où se trouve settings.py
# -> pratique pour construire des chemins "propres" même si on lance le projet ailleurs
PROJECT_ROOT = Path(__file__).resolve().parent

# Dossier data/ (contient les fichiers textes)
DATA_DIR = PROJECT_ROOT / "data"

# Fichier des mots pour le pendu (1 mot par ligne)
WORDS_PATH = str(DATA_DIR / "mots.txt")

# Fichier du classement (généré / mis à jour après les parties)
LEADERBOARD_PATH = str(DATA_DIR / "leaderboard.txt")


"""
FENÊTRE PYGAME (taille + FPS)
"""

# Taille de la fenêtre
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

# FPS = nombre d'images par seconde
# 60 c'est fluide et classique
FPS = 60


"""
TAILLES UI (boutons + champs texte)
"""

# Boutons standards (menu, leaderboard, etc.)
BTN_W = 320
BTN_H = 56

# Champs texte (pseudo, ajouter un mot)
INPUT_W = 420
INPUT_H = 52


"""
PSEUDO (obligatoire avant de jouer)
"""

# Longueur minimale / maximale du pseudo
PSEUDO_MIN_LEN = 1
PSEUDO_MAX_LEN = 16

# Caractères interdits :
# - ";" interdit parce que c'est utilisé comme séparateur dans leaderboard.txt
# - "\n" et "\r" interdits pour éviter de casser le format du fichier texte
PSEUDO_FORBIDDEN_CHARS = [";", "\n", "\r"]


"""
DIFFICULTÉ (nombre d'erreurs autorisées)
"""

# On stocke la difficulté sous forme de texte :
# "FACILE", "MOYEN", "DIFFICILE"
# et chaque difficulté donne un max d'erreurs.
MAX_ERRORS_BY_DIFFICULTY = {
    "FACILE": 8,
    "MOYEN": 6,
    "DIFFICILE": 5,
}


"""
COULEURS (pour que tout soit cohérent)
"""

# Couleurs en RGB : (rouge, vert, bleu)
# On les met ici pour éviter de les répéter dans tous les fichiers.

COLOR_BG = (18, 18, 18)          # fond sombre
COLOR_TEXT = (230, 230, 230)     # texte clair
COLOR_MUTED = (170, 170, 170)    # texte "secondaire"

COLOR_BTN = (40, 40, 40)         # bouton normal
COLOR_BTN_HOVER = (60, 60, 60)   # bouton survolé
COLOR_BTN_DISABLED = (30, 30, 30)

COLOR_INPUT_BG = (30, 30, 30)        # fond des inputs
COLOR_INPUT_BORDER = (90, 90, 90)    # bordure input
COLOR_INPUT_ACTIVE = (140, 140, 140) # bordure quand focus

COLOR_GOOD = (60, 190, 110)      # feedback positif
COLOR_BAD = (220, 80, 80)        # feedback négatif


"""
POLICES (tailles, simple)
"""

# On met juste les tailles ici.
# Le chargement réel des polices (pygame.font.Font) se fait dans main.py.
FONT_SIZE_TITLE = 56
FONT_SIZE_BODY = 28
FONT_SIZE_SMALL = 20

"""
CLASSEMENT (optionnel)
"""

# Si on veut afficher seulement un TOP N dans la scène classement.
# - None => on affiche tout
# - 20 => on affiche seulement les 20 premiers
LEADERBOARD_TOP_N = None
