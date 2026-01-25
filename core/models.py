"""
But du fichier
- Centraliser les "objets" (structures) que le projet manipule partout.
- Éviter les dépendances à Pygame ici : ce sont juste des données.
- Avoir des contrats simples et stables entre core/ (logique) et scenes/ (UI).

Pourquoi on fait ça
- Ça rend le code plus lisible : on sait exactement ce qu'une fonction reçoit / renvoie.
- Ça limite les bugs de "dictionnaires" (clés manquantes, types incohérents, etc.).
- Ça permet d'écrire des fonctions core/ plus propres (elles manipulent des GameState, pas des tuples).

Contrats importants (à respecter dans le reste du projet)
- guessed_letters et wrong_letters ne doivent jamais contenir la même lettre.
- status doit rester dans : "playing", "won", "lost".
- secret_word est stocké en minuscule (normalisé à la création).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Set


@dataclass
class GameState:
    """
    État d'une partie de pendu.

    Cette classe représente "où on en est" dans une partie.
    Elle est créée au début de la partie (start_new_game) puis mise à jour à chaque tentative.

    Attributs
    - secret_word :
        Mot à deviner, en minuscule.
        (Le fait de le stocker en minuscule évite les soucis de comparaison A/a.)
    - guessed_letters :
        Ensemble des lettres correctes déjà trouvées.
        Exemple : {"a", "e", "t"}.
        Un set est utilisé car :
        - pas de doublons
        - recherche rapide (in / not in)
    - wrong_letters :
        Ensemble des lettres déjà tentées mais absentes du mot.
        Même avantage : pas de doublons.
    - max_errors :
        Nombre d'erreurs autorisées avant de perdre.
        Dans notre projet, c'est une valeur stable (consigne : 7).
    - status :
        État global de la partie.
        Valeurs attendues : "playing" / "won" / "lost"

    Invariants (règles internes)
    - Une lettre ne peut pas être à la fois guessed_letters et wrong_letters.
    - Si status != "playing", la partie ne devrait plus accepter de nouvelle lettre.
    """
    secret_word: str
    guessed_letters: Set[str]
    wrong_letters: Set[str]
    max_errors: int
    status: str  # "playing" / "won" / "lost"


@dataclass
class PlayerProfile:
    """
    Profil d'un joueur dans le classement (leaderboard).

    Cette structure correspond à une ligne du fichier leaderboard.txt (ou équivalent),
    donc elle doit rester stable dans le temps.

    Champs
    - pseudo :
        Identifiant joueur (celui entré dans le menu).
    - best_score :
        Meilleur score obtenu sur toutes les parties.
    - best_score_time_seconds :
        Temps associé au meilleur score (utile pour départager si besoin).
    - total_play_time_seconds :
        Temps cumulé de jeu (toutes parties confondues).
    - games_played :
        Nombre total de parties jouées.
    - last_played_iso :
        Date/heure de la dernière partie, au format ISO (ex : 2026-01-25T12:34:56Z).

    Format persisté (1 ligne)
    pseudo;best_score;best_score_time_s;total_play_time_s;games_played;last_played_iso

    Remarque
    - On stocke des ints pour les valeurs numériques pour éviter des conversions partout.
    - last_played_iso est en string car le fichier texte doit rester lisible et portable.
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
    Résultat d'une tentative de lettre (utile pour faire un feedback UI propre).

    L'idée
    - Plutôt que de renvoyer juste True/False, on renvoie un "type" + un message.
    - La scène peut afficher le message tel quel (toast / zone info) sans recoder la logique.

    Champs
    - kind :
        Catégorie de résultat :
        - "good"    : lettre correcte (nouvelle)
        - "bad"     : lettre incorrecte (nouvelle)
        - "already" : lettre déjà jouée auparavant
        - "invalid" : tentative invalide (ex : partie finie, lettre vide, etc.)
    - message :
        Texte prêt à afficher, court, compréhensible.
        (Ex : "Bonne lettre", "Déjà essayé", "Partie terminée"...)

    Note
    - Le choix du message ici permet de garder une UI cohérente.
    - Si un jour on veut internationaliser, ce sera ce fichier (ou un layer au-dessus) à adapter.
    """
    kind: str
    message: str
