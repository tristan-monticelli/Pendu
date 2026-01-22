"""
Objectif :
- Convertir difficulté -> max_errors
- Calculer un score stable et simple

Fonctions :
- set_difficulty(difficulty) -> int
- compute_score(game_state, difficulty, elapsed_seconds) -> int
- format_game_result(score, elapsed_seconds, status) -> str
"""

from __future__ import annotations

from typing import Optional

from settings import MAX_ERRORS_BY_DIFFICULTY
from core.models import GameState


def set_difficulty(difficulty: str) -> int:
    """
    Convertit une difficulté en max_errors.
    Si difficulté inconnue, MOYEN par défaut.
    """
    if difficulty not in MAX_ERRORS_BY_DIFFICULTY:
        difficulty = "MOYEN"
    return int(MAX_ERRORS_BY_DIFFICULTY[difficulty])


def compute_score(game_state: GameState, difficulty: str, elapsed_seconds: int) -> int:
    """
    Calcul du score (comme dans notrez pseudo-code).

    - points_lettres = nb_lettres_trouvées * 10
    - penalite = nb_erreurs * 5
    - bonus difficulté : FACILE 0 / MOYEN 10 / DIFFICILE 20
    - bonus temps : <60s +15 / <120s +8 / sinon 0
    - score >= 0
    """
    nb_found = len(game_state.guessed_letters)
    nb_wrong = len(game_state.wrong_letters)

    points_lettres = nb_found * 10
    penalite = nb_wrong * 5

    if difficulty == "FACILE":
        bonus_diff = 0
    elif difficulty == "MOYEN":
        bonus_diff = 10
    else:
        bonus_diff = 20

    if elapsed_seconds < 60:
        bonus_time = 15
    elif elapsed_seconds < 120:
        bonus_time = 8
    else:
        bonus_time = 0

    score = points_lettres - penalite + bonus_diff + bonus_time
    if score < 0:
        score = 0
    return int(score)


def format_game_result(score: int, elapsed_seconds: int, status: str) -> str:
    """
    Phrase affichable type :
    - "Victoire ! Score: 120 | Temps: 01:34"
    - "Défaite... Score: 40 | Temps: 02:10"
    """
    prefix = "Victoire !" if status == "won" else "Défaite..."
    mm = max(0, int(elapsed_seconds)) // 60
    ss = max(0, int(elapsed_seconds)) % 60
    return f"{prefix} Score: {score} | Temps: {mm:02d}:{ss:02d}"
