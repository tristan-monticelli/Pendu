"""Calcul du score - A IMPLEMENTER"""

from core.models import GameState
from settings import MAX_ERRORS_HARD

#--------------------------------------Score--------------------------------------#

def compute_score(game_state: GameState, elapsed_seconds: float, won: bool) -> int:
    """
    Calcule le score final
    A IMPLEMENTER: Formule de score (lettres, erreurs, temps, bonus)
    """
    pass  # TODO: Implementer
    return 0

#--------------------------------------Formatage--------------------------------------#

def format_score(score: int) -> str:
    """Formate le score pour l'affichage (ex: 1 000)"""
    pass  # TODO: Implementer
    return str(score)

def format_time(seconds: int) -> str:
    """Formate le temps en mm:ss"""
    pass  # TODO: Implementer
    return "00:00"
