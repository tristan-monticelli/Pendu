"""Modeles de donnees du jeu"""

from dataclasses import dataclass, field
from typing import List
from settings import MAX_ERRORS_NORMAL

#--------------------------------------GameState--------------------------------------#

@dataclass
class GameState:
    """Etat d'une partie en cours"""
    secret_word: str
    guessed_letters: List[str] = field(default_factory=list)
    wrong_letters: List[str] = field(default_factory=list)
    max_errors: int = MAX_ERRORS_NORMAL
    status: str = "playing"

    @property
    def errors(self) -> int:
        """Nombre d'erreurs actuelles"""
        return len(self.wrong_letters)

    @property
    def lives(self) -> int:
        """Nombre de vies restantes"""
        return self.max_errors - self.errors

#--------------------------------------PlayerProfile--------------------------------------#

@dataclass
class PlayerProfile:
    """Profil d'un joueur (pour le classement)"""
    pseudo: str
    best_score: int = 0
    best_score_time_seconds: int = 0
    total_play_time_seconds: int = 0
    games_played: int = 0
    last_played_iso: str = ""

#--------------------------------------SessionStats--------------------------------------#

@dataclass
class SessionStats:
    """Stats d'une session de jeu"""
    start_time: float = 0.0
    elapsed_seconds: float = 0.0
    score: int = 0
    difficulty: str = "normal"
