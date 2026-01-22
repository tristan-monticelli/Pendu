"""
Objectif :
- Gérer le temps d'une partie en utilisant une fonction get_ticks_func (ms).
- Typiquement : pygame.time.get_ticks

Fonctions :
- start_session_timer(get_ticks_func) -> int
- get_elapsed_seconds(start_ticks, get_ticks_func) -> int
- stop_session_timer(start_ticks, get_ticks_func) -> int
"""

from __future__ import annotations

from typing import Callable


def start_session_timer(get_ticks_func: Callable[[], int]) -> int:
    """
    Démarre le timer de la partie.

    Retour :
    - start_ticks (ms)
    """
    return int(get_ticks_func())


def get_elapsed_seconds(start_ticks: int, get_ticks_func: Callable[[], int]) -> int:
    """
    Temps écoulé en secondes, partie entière.
    """
    now_ticks = int(get_ticks_func())
    elapsed_ms = now_ticks - int(start_ticks)
    if elapsed_ms < 0:
        elapsed_ms = 0
    return int(elapsed_ms // 1000)


def stop_session_timer(start_ticks: int, get_ticks_func: Callable[[], int]) -> int:
    """
    Stoppe le timer et renvoie la durée totale en secondes.
    """
    return get_elapsed_seconds(start_ticks, get_ticks_func)
