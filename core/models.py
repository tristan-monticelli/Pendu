"""
Structures de données du projet Pendu.

Objectif :
- Centraliser les "objets" manipulés par core/ et scenes/
- Aucune dépendance à Pygame
- Simple, lisible, stable 

Contrats importants :
- GameState.guessed_letters et GameState.wrong_letters ne doivent pas se chevaucher.
- GameState.status ∈ {"playing", "won", "lost"}.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Set


@dataclass
class GameState:
    """
    Stocke l'état d'une partie de pendu.

    Attributs :
    - secret_word : mot à deviner (en minuscule)
    - guessed_letters : lettres correctes déjà trouvées
    - wrong_letters : lettres incorrectes déjà tentées
    - max_errors : nombre d'erreurs autorisées
    - status : "playing" / "won" / "lost"
    """
    secret_word: str
    guessed_letters: Set[str]
    wrong_letters: Set[str]
    max_errors: int
    status: str  # "playing" / "won" / "lost"


@dataclass
class PlayerProfile:
    """
    Profil d'un joueur dans le classement (persisté dans leaderboard.txt)

    Format persisté :
    pseudo;best_score;best_score_time_s;total_play_time_s;games_played;last_played_iso
    """
    pseudo: str
    best_score: int
    best_score_time_seconds: int
    total_play_time_seconds: int
    games_played: int
    last_played_iso: str


@dataclass
class GuessResult:
    """
    Résultat d'une tentative de lettre, utile pour afficher un feedback.

    kind :
    - "good"   : lettre correcte
    - "bad"    : lettre incorrecte
    - "already": lettre déjà jouée
    - "invalid": tentative invalide (partie finie ou lettre non conforme)

    message : texte prêt à afficher
    """
    kind: str
    message: str
