"""
Objectif
- Gérer le classement multi-joueurs sauvegardé dans un fichier texte (data/leaderboard.txt).
- Fournir des fonctions simples pour :
  - valider un pseudo
  - charger / sauvegarder le fichier
  - trier les joueurs
  - mettre à jour un profil après une partie
  - récupérer un "résumé" du dernier joueur (affiché dans le menu)

Format du fichier (1 joueur par ligne)
pseudo;best_score;best_score_time_s;total_play_time_s;games_played;last_played_iso
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from core.models import PlayerProfile
from settings import PSEUDO_MIN_LEN, PSEUDO_MAX_LEN, PSEUDO_FORBIDDEN_CHARS


def validate_pseudo(raw_pseudo: str) -> Tuple[bool, str, str]:
    """
    Valide un pseudo (obligatoire avant de jouer).

    Règles (définies dans settings.py)
    - longueur minimale : PSEUDO_MIN_LEN
    - longueur maximale : PSEUDO_MAX_LEN
    - certains caractères sont interdits (liste PSEUDO_FORBIDDEN_CHARS)

    Retour
    - ok : True si le pseudo est valide
    - normalized : pseudo "nettoyé" (strip), mais sans forcer la casse
    - message : message court prévu pour l'UI (toast / message sous champ)

    Note
    - Ici on n'interdit pas explicitement les chiffres : seules les règles settings comptent.
    - On ne met pas en minuscule car on veut garder le pseudo tel que l'utilisateur l'a entré.
    """
    if raw_pseudo is None:
        return False, "", "Pseudo requis"

    pseudo = str(raw_pseudo).strip()

    if len(pseudo) < PSEUDO_MIN_LEN:
        return False, "", "Entrer un pseudo"

    if len(pseudo) > PSEUDO_MAX_LEN:
        return False, "", "Pseudo trop long (max 16)"

    # Vérification caractère par caractère : simple et suffisant pour un projet de jeu
    for bad in PSEUDO_FORBIDDEN_CHARS:
        if bad in pseudo:
            return False, "", "Caractère interdit dans pseudo"

    return True, pseudo, "Pseudo OK"


def load_leaderboard(path: str) -> Dict[str, PlayerProfile]:
    """
    Charge le classement depuis un fichier texte.

    Principe
    - On lit toutes les lignes.
    - On parse selon le format attendu (6 colonnes séparées par ';').
    - Les lignes invalides sont ignorées (pour ne pas casser le jeu si un fichier est abîmé).

    Retour
    - Dictionnaire : pseudo -> PlayerProfile

    Remarque
    - Si le fichier n'existe pas : on renvoie un dict vide.
      (Ça permet au jeu de démarrer "sans classement" sans planter.)
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
            # Ligne corrompue -> on ignore
            continue

        pseudo = parts[0]
        try:
            best_score = int(parts[1])
            best_time = int(parts[2])
            total_time = int(parts[3])
            games_played = int(parts[4])
            last_iso = parts[5]
        except Exception:
            # Si conversion impossible, on ignore la ligne
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
    Sauvegarde le classement dans le fichier.

    Choix simple
    - On réécrit tout le fichier à chaque sauvegarde.
      (C'est suffisant vu la taille très petite du classement.)

    Remarque
    - L'ordre dépend de l'ordre du dict (insertion order).
      Le tri pour affichage est fait ailleurs via sort_leaderboard().
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
    Trie les joueurs pour l'affichage (best_score décroissant).

    Retour
    - Liste de PlayerProfile triée

    Note
    - En cas d'égalité, le tri ne départage pas sur le temps.
      Si on veut départager : on pourrait trier sur (best_score, -best_score_time_seconds) etc.
      Mais ici on garde simple.
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
    Met à jour le profil d'un joueur après une partie (modifie leaderboard en place).

    Cas gérés
    - Joueur inconnu : on crée un profil avec des valeurs initiales.
    - Joueur existant : on incrémente ses stats.

    Ce qu'on met à jour à chaque partie
    - games_played : +1
    - total_play_time_seconds : + elapsed_seconds (on protège contre les valeurs négatives)
    - last_played_iso : date/heure de la partie

    Ce qu'on met à jour uniquement si nouveau record
    - best_score
    - best_score_time_seconds (temps associé au meilleur score)

    Remarque
    - La logique de "score plus grand = record" est volontairement simple.
    - elapsed_seconds est clampé à >= 0 pour éviter des corruptions de stats.
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

    # Stats cumulées
    p.games_played += 1
    p.total_play_time_seconds += max(0, int(elapsed_seconds))
    p.last_played_iso = now_iso

    # Record : uniquement si le score est strictement meilleur
    if int(score) > p.best_score:
        p.best_score = int(score)
        p.best_score_time_seconds = max(0, int(elapsed_seconds))


def get_last_player_summary(leaderboard: Dict[str, PlayerProfile]) -> Dict[str, int | str]:
    """
    Récupère un résumé du joueur le plus "récent" via last_played_iso.

    Retour
    - {} si le classement est vide
    - sinon un dict contenant juste ce qui est utile pour l'affichage du menu :
      pseudo, total_play_time_seconds, best_score, best_score_time_seconds

    Détail important
    - On utilise max(..., key=last_played_iso)
      -> ça marche car un timestamp ISO "bien formé" est comparable lexicalement.
    """
    if not leaderboard:
        return {}

    last_profile = max(leaderboard.values(), key=lambda p: p.last_played_iso)

    return {
        "pseudo": last_profile.pseudo,
        "total_play_time_seconds": last_profile.total_play_time_seconds,
        "best_score": last_profile.best_score,
        "best_score_time_seconds": last_profile.best_score_time_seconds,
    }


def format_last_player_stats(summary: Dict[str, int | str]) -> List[str]:
    """
    Transforme le résumé du dernier joueur en lignes prêtes à afficher.

    Pourquoi cette fonction existe
    - Pour éviter que la scène menu fasse du "formatage" à la main.
    - On garde les textes cohérents au même endroit.

    Note
    - Ici on laisse les secondes en "Xs" (brut).
      Le format MM:SS est géré côté UI (format_duration dans simpson_theme).
    """
    if not summary:
        return ["Aucun joueur enregistré"]

    return [
        f"Dernier joueur : {summary['pseudo']}",
        f"Temps total : {summary['total_play_time_seconds']}s",
        f"Meilleur score : {summary['best_score']}",
        f"Temps du record : {summary['best_score_time_seconds']}s",
    ]
