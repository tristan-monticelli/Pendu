"""Gestion du classement multi-joueurs - A IMPLEMENTER"""

from typing import List, Optional
from core.models import PlayerProfile
from settings import PATHS

#--------------------------------------Chargement--------------------------------------#

def load_leaderboard() -> List[PlayerProfile]:
    """
    Charge tous les joueurs du classement depuis leaderboard.txt
    A IMPLEMENTER: Lire le fichier, parser les lignes
    """
    pass  # TODO: Implementer
    return []

def _create_default_leaderboard(filepath: str):
    """Cree le fichier de classement vide"""
    pass  # TODO: Implementer

#--------------------------------------Sauvegarde--------------------------------------#

def save_leaderboard(players: List[PlayerProfile]):
    """
    Sauvegarde le classement dans leaderboard.txt
    A IMPLEMENTER: Ecrire les joueurs dans le fichier
    """
    pass  # TODO: Implementer

#--------------------------------------Acces joueur--------------------------------------#

def get_or_create_player(pseudo: str) -> PlayerProfile:
    """
    Recupere ou cree un profil joueur
    A IMPLEMENTER: Chercher dans le leaderboard ou creer nouveau
    """
    pass  # TODO: Implementer
    return PlayerProfile(pseudo=pseudo)

def get_last_player() -> Optional[PlayerProfile]:
    """
    Recupere le dernier joueur (pour le menu)
    A IMPLEMENTER: Trier par date, retourner le plus recent
    """
    pass  # TODO: Implementer
    return None

#--------------------------------------Mise a jour--------------------------------------#

def update_player_after_game(pseudo: str, score: int, elapsed_seconds: int):
    """
    Met a jour le profil apres une partie
    A IMPLEMENTER: Incrementer games_played, verifier best_score, sauvegarder
    """
    pass  # TODO: Implementer

#--------------------------------------Tri--------------------------------------#

def sort_leaderboard(players: List[PlayerProfile]) -> List[PlayerProfile]:
    """
    Trie par meilleur score decroissant
    A IMPLEMENTER: sorted() par best_score
    """
    pass  # TODO: Implementer
    return players
