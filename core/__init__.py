"""Module core - Logique metier du jeu du Pendu"""

from core.models import GameState, PlayerProfile, SessionStats
from core.game_state import start_game, apply_guess, build_masked_word, check_end_condition
from core.scoring import compute_score
from core.words_io import load_words, add_word, validate_word
from core.leaderboard_io import (
    load_leaderboard,
    save_leaderboard,
    get_or_create_player,
    update_player_after_game,
    get_last_player,
    sort_leaderboard,
)
from core.time_tracker import TimeTracker
from core.input_normalize import normalize_letter_input, is_valid_letter_event

__all__ = [
    "GameState",
    "PlayerProfile",
    "SessionStats",
    "start_game",
    "apply_guess",
    "build_masked_word",
    "check_end_condition",
    "compute_score",
    "load_words",
    "add_word",
    "validate_word",
    "load_leaderboard",
    "save_leaderboard",
    "get_or_create_player",
    "update_player_after_game",
    "get_last_player",
    "sort_leaderboard",
    "TimeTracker",
    "normalize_letter_input",
    "is_valid_letter_event",
]
