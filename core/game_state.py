"""
Logique pure du pendu, sans UI et sans Pygame.

Fonctions :
- start_game(words_list, max_errors) -> GameState
- apply_guess(game_state, letter) -> (GameState, GuessResult)
- build_masked_word(secret_word, guessed_letters) -> str
- check_end_condition(game_state) -> GameState
"""

from __future__ import annotations

import random
from typing import List, Set, Tuple

from core.models import GameState, GuessResult


_ALLOWED_STATUS = {"playing", "won", "lost"}


def start_game(words_list: List[str], max_errors: int) -> GameState:
    """
    Démarre une nouvelle partie.

    Préconditions :
    - words_list non vide
    - max_errors >= 1
    """
    if not words_list:
        raise ValueError("Aucun mot disponible")

    if max_errors < 1:
        raise ValueError("max_errors doit être >= 1")

    secret_word = random.choice(words_list)

    guessed_letters: Set[str] = set()
    wrong_letters: Set[str] = set()
    status = "playing"

    return GameState(
        secret_word=secret_word,
        guessed_letters=guessed_letters,
        wrong_letters=wrong_letters,
        max_errors=max_errors,
        status=status,
    )


def apply_guess(game_state: GameState, letter: str) -> Tuple[GameState, GuessResult]:
    """
    Applique une tentative de lettre.

    Préconditions :
    - letter est une str de longueur 1
    - letter est une lettre (alphabétique)
    - letter est déjà normalisée (minuscule, accents normalisés)
    """
    if game_state.status != "playing":
        return game_state, GuessResult("invalid", "La partie est terminée")

    if not isinstance(letter, str) or len(letter) != 1 or not letter.isalpha():
        return game_state, GuessResult("invalid", "Lettre invalide")

    if letter in game_state.guessed_letters or letter in game_state.wrong_letters:
        return game_state, GuessResult("already", "Lettre déjà jouée")

    if letter in game_state.secret_word:
        game_state.guessed_letters.add(letter)
        result = GuessResult("good", "Bonne lettre !")
    else:
        game_state.wrong_letters.add(letter)
        result = GuessResult("bad", "Mauvaise lettre...")

    game_state = check_end_condition(game_state)
    return game_state, result


def build_masked_word(secret_word: str, guessed_letters: Set[str]) -> str:
    """
    Construit une chaîne affichable du mot masqué.

    Exemple :
    secret_word="banane", guessed={"a","n"} => "_ a n a n e"
    """
    parts: List[str] = []
    for c in secret_word:
        if c.isalpha() and c in guessed_letters:
            parts.append(c)
        else:
            parts.append("_")
    return " ".join(parts)


def check_end_condition(game_state: GameState) -> GameState:
    """
    Met à jour game_state.status si gagné ou perdu.

    Victoire :
    - toutes les lettres uniques du mot (alphabétiques) sont trouvées

    Défaite :
    - len(wrong_letters) >= max_errors
    """
    # Sécurité sur status
    if game_state.status not in _ALLOWED_STATUS:
        game_state.status = "playing"

    letters_in_word = {c for c in game_state.secret_word if c.isalpha()}

    if letters_in_word.issubset(game_state.guessed_letters):
        game_state.status = "won"
        return game_state

    if len(game_state.wrong_letters) >= game_state.max_errors:
        game_state.status = "lost"
        return game_state

    game_state.status = "playing"
    return game_state
