"""
Objectif :
- Gérer le classement multi-joueurs dans data/leaderboard.txt

Format (1 joueur / ligne) :
pseudo;best_score;best_score_time_s;total_play_time_s;games_played;last_played_iso

Fonctions :
- validate_pseudo
- load_leaderboard
- save_leaderboard
- sort_leaderboard
- update_player_after_game
- get_last_player_summary
- format_last_player_stats
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from core.models import PlayerProfile

from settings import PSEUDO_MIN_LEN, PSEUDO_MAX_LEN, PSEUDO_FORBIDDEN_CHARS


def validate_pseudo(raw_pseudo: str) -> Tuple[bool, str, str]:
    """
    Valide un pseudo (obligatoire avant de jouer).

    Retour :
    - ok, normalized, message
    """
    if raw_pseudo is None:
        return False, "", "Pseudo requis"

    pseudo = str(raw_pseudo).strip()

    if len(pseudo) < PSEUDO_MIN_LEN:
        return False, "", "Entrer un pseudo"

    if len(pseudo) > PSEUDO_MAX_LEN:
        return False, "", "Pseudo trop long (max 16)"

    for bad in PSEUDO_FORBIDDEN_CHARS:
        if bad in pseudo:
            return False, "", "Caractère interdit dans pseudo"

    return True, pseudo, "Pseudo OK"


def load_leaderboard(path: str) -> Dict[str, PlayerProfile]:
    """
    Charge le classement depuis le fichier.

    Retour :
    - dict pseudo -> PlayerProfile
    """
    leaderboard: Dict[str, PlayerProfile] = {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return leaderboard

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split(";")
        if len(parts) != 6:
            # Ligne corrompue => ignorée
            continue

        pseudo = parts[0]
        try:
            best_score = int(parts[1])
            best_time = int(parts[2])
            total_time = int(parts[3])
            games_played = int(parts[4])
            last_iso = parts[5]
        except Exception:
            continue

        leaderboard[pseudo] = PlayerProfile(
            pseudo=pseudo,
            best_score=best_score,
            best_score_time_seconds=best_time,
            total_play_time_seconds=total_time,
            games_played=games_played,
            last_played_iso=last_iso,
        )

    return leaderboard


def save_leaderboard(path: str, leaderboard: Dict[str, PlayerProfile]) -> None:
    """
    Réécrit entièrement le classement dans le fichier.
    """
    with open(path, "w", encoding="utf-8") as f:
        for pseudo, profile in leaderboard.items():
            line = (
                f"{profile.pseudo};"
                f"{profile.best_score};"
                f"{profile.best_score_time_seconds};"
                f"{profile.total_play_time_seconds};"
                f"{profile.games_played};"
                f"{profile.last_played_iso}"
            )
            f.write(line + "\n")


def sort_leaderboard(leaderboard: Dict[str, PlayerProfile]) -> List[PlayerProfile]:
    """
    Trie les joueurs par best_score décroissant.
    """
    profiles = list(leaderboard.values())
    profiles.sort(key=lambda p: p.best_score, reverse=True)
    return profiles


def update_player_after_game(
    leaderboard: Dict[str, PlayerProfile],
    pseudo: str,
    score: int,
    elapsed_seconds: int,
    now_iso: str,
) -> None:
    """
    Met à jour ou crée un joueur après une partie (modifie leaderboard en place).
    """
    if pseudo not in leaderboard:
        leaderboard[pseudo] = PlayerProfile(
            pseudo=pseudo,
            best_score=0,
            best_score_time_seconds=0,
            total_play_time_seconds=0,
            games_played=0,
            last_played_iso=now_iso,
        )

    p = leaderboard[pseudo]
    p.games_played += 1
    p.total_play_time_seconds += max(0, int(elapsed_seconds))
    p.last_played_iso = now_iso

    if int(score) > p.best_score:
        p.best_score = int(score)
        p.best_score_time_seconds = max(0, int(elapsed_seconds))


def get_last_player_summary(leaderboard: Dict[str, PlayerProfile]) -> Dict[str, int | str]:
    """
    Récupère le joueur le plus récent via last_played_iso.

    Retour :
    - {} si vide
    - sinon dict :
      pseudo, total_play_time_seconds, best_score, best_score_time_seconds
    """
    if not leaderboard:
        return {}

    # ISO sortable lexicalement si bien formé
    last_profile = max(leaderboard.values(), key=lambda p: p.last_played_iso)

    return {
        "pseudo": last_profile.pseudo,
        "total_play_time_seconds": last_profile.total_play_time_seconds,
        "best_score": last_profile.best_score,
        "best_score_time_seconds": last_profile.best_score_time_seconds,
    }


def format_last_player_stats(summary: Dict[str, int | str]) -> List[str]:
    """
    Convertit le résumé en lignes affichables.
    (Le format MM:SS est géré côté UI avec format_duration)
    """
    if not summary:
        return ["Aucun joueur enregistré"]

    return [
        f"Dernier joueur : {summary['pseudo']}",
        f"Temps total : {summary['total_play_time_seconds']}s",
        f"Meilleur score : {summary['best_score']}",
        f"Temps du record : {summary['best_score_time_seconds']}s",
    ]
