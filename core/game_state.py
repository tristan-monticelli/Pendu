"""Logique du jeu du pendu - A IMPLEMENTER"""

from typing import Tuple, List
from core.models import GameState
from settings import MAX_ERRORS_NORMAL, MAX_ERRORS_HARD

#--------------------------------------Demarrage--------------------------------------#

def start_game(words_list: List[str], difficulty: str, player_pseudo: str) -> GameState:
    """
    Demarre une nouvelle partie
    A IMPLEMENTER: Selection aleatoire du mot, initialisation du GameState
    """
    pass  # TODO: Implementer
    return GameState(secret_word="TEST", guessed_letters=[], wrong_letters=[], max_errors=6, status="playing")

#--------------------------------------Tentative--------------------------------------#

def apply_guess(game_state: GameState, letter: str) -> Tuple[GameState, str]:
    """
    Applique une tentative de lettre
    A IMPLEMENTER: Verifier si la lettre est dans le mot, mettre a jour l'etat
    Retourne: (game_state, "correct"/"wrong"/"already_played")
    """
    pass  # TODO: Implementer
    return game_state, "correct"

#--------------------------------------Affichage--------------------------------------#

def build_masked_word(secret_word: str, guessed_letters: List[str]) -> str:
    """
    Construit le mot masque : "_ A _ _ E"
    A IMPLEMENTER: Remplacer les lettres non trouvees par des underscores
    """
    pass  # TODO: Implementer
    return "_ _ _ _"

#--------------------------------------Condition de fin--------------------------------------#

def check_end_condition(game_state: GameState) -> str:
    """
    Verifie si la partie est terminee
    A IMPLEMENTER: Retourner "won", "lost" ou "playing"
    """
    pass  # TODO: Implementer
    return "playing"

#--------------------------------------Indice--------------------------------------#

def get_hint(game_state: GameState) -> str:
    """
    Retourne une lettre non trouvee (indice)
    A IMPLEMENTER: Trouver une lettre du mot pas encore devinee
    """
    pass  # TODO: Implementer
    return ""
