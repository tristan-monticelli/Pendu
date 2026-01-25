"""
Objectif du fichier
- Centraliser les règles de score du jeu pour éviter de les disperser dans les scènes.
- Fournir des fonctions courtes et stables :
  - convertir une difficulté en nombre d'erreurs autorisées
  - calculer un score numérique (int) à partir d'un état de jeu
  - formater un message de fin (pour l'écran "Game Over" ou un toast)

Choix importants du projet
- Consigne : peu importe la difficulté, on reste à 7 erreurs maximum.

Pourquoi c'est utile d'avoir un module à part
- Le menu / game_scene peuvent changer l'UI, mais les règles de score restent ici.
- Si on doit ajuster la formule, on ne modifie qu'un seul fichier.
"""

from __future__ import annotations

from core.models import GameState
from settings import MAX_ERRORS_BY_DIFFICULTY


def set_difficulty(difficulty: str) -> int:
    """
    Convertit une difficulté en nombre d'erreurs autorisées (max_errors).

    Consigne appliquée :
    - On limite toujours à 7 erreurs, quelle que soit la difficulté.

    Détails d'implémentation
    - On garde la structure "dictionnaire" (MAX_ERRORS_BY_DIFFICULTY) pour rester simple
      et compatible avec le reste du projet.
    - Si difficulty est invalide, on prend "MOYEN" par défaut (comportement sûr).

    Args:
        difficulty: texte "FACILE" / "MOYEN" / "DIFFICILE" (ou autre)

    Returns:
        max_errors (int) : ici toujours 7 en pratique.
    """
    # On garde la structure existante (simple),
    # mais le dictionnaire vaut 7 partout.
    if difficulty not in MAX_ERRORS_BY_DIFFICULTY:
        difficulty = "MOYEN"
    return int(MAX_ERRORS_BY_DIFFICULTY[difficulty])


def compute_score(game_state: GameState, difficulty: str, elapsed_seconds: int) -> int:
    """
    Calcule un score final à partir de l'état du jeu et du temps.

    Objectif de la formule
    - Rester simple à expliquer et à tester.
    - Avoir un score "stable" : les mêmes actions donnent le même résultat.
    - Récompenser les bonnes lettres, pénaliser les erreurs, et ajouter un petit bonus
      lié à la difficulté + un bonus temps.

    Détail de la formule (résumé)
    - points_lettres = nb_lettres_trouvees * 10
    - penalite       = nb_erreurs * 5
    - bonus_diff     = FACILE 0 / MOYEN 10 / DIFFICILE 20
    - bonus_time     = <60s +15 / <120s +8 / sinon 0
    - score final = points_lettres - penalite + bonus_diff + bonus_time
    - score ne peut pas être négatif (minimum 0)

    Remarque importante sur game_state
    - nb_found = len(game_state.guessed_letters)
      -> ici ça compte les lettres trouvées (ensemble / liste).
    - nb_wrong = len(game_state.wrong_letters)
      -> ici ça compte les tentatives incorrectes.

    Args:
        game_state: état du jeu (lettres trouvées + lettres fausses)
        difficulty: difficulté (sert uniquement au bonus)
        elapsed_seconds: temps total de la partie (en secondes)

    Returns:
        score (int) >= 0
    """
    nb_found = len(game_state.guessed_letters)
    nb_wrong = len(game_state.wrong_letters)

    points_lettres = nb_found * 10
    penalite = nb_wrong * 5

    # Bonus difficulté : simple et lisible.
    if difficulty == "FACILE":
        bonus_diff = 0
    elif difficulty == "MOYEN":
        bonus_diff = 10
    else:
        bonus_diff = 20

    # Bonus temps : encourage à jouer sans traîner,
    # mais reste assez faible pour ne pas écraser le reste.
    if elapsed_seconds < 60:
        bonus_time = 15
    elif elapsed_seconds < 120:
        bonus_time = 8
    else:
        bonus_time = 0

    score = points_lettres - penalite + bonus_diff + bonus_time

    # Sécurité : on ne veut jamais de score négatif.
    if score < 0:
        score = 0

    return int(score)


def format_game_result(score: int, elapsed_seconds: int, status: str) -> str:
    """
    Formate une phrase courte pour afficher le résultat d'une partie.

    Exemples
    - "Victoire ! Score: 120 | Temps: 01:34"
    - "Défaite... Score: 40 | Temps: 02:10"

    Détails
    - status == "won" -> Victoire
    - sinon -> Défaite
    - elapsed_seconds est converti en MM:SS en forçant les valeurs négatives à 0

    Args:
        score: score final (int)
        elapsed_seconds: temps total (en secondes)
        status: "won" ou "lost" (ou autre valeur)

    Returns:
        Chaîne prête à afficher dans l'UI.
    """
    prefix = "Victoire !" if status == "won" else "Défaite..."
    mm = max(0, int(elapsed_seconds)) // 60
    ss = max(0, int(elapsed_seconds)) % 60
    return f"{prefix} Score: {score} | Temps: {mm:02d}:{ss:02d}"
