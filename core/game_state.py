"""
Idée
- Ce fichier contient les règles du jeu, sans dépendre de Pygame et sans faire d'affichage.
- Les scènes (menu/game) l'appellent pour :
  - créer une nouvelle partie (GameState)
  - appliquer une tentative (apply_guess)
  - savoir si la partie est gagnée/perdue
  - construire le mot masqué à afficher ("_ a _ _ e")

Fonctions disponibles
- start_game(words_list, max_errors) -> GameState
  Démarre une partie en choisissant un mot au hasard dans une liste.

- start_game_from_word(secret_word, max_errors) -> GameState
  Démarre une partie à partir d'un mot déjà choisi (utile quand on filtre par difficulté).

- apply_guess(game_state, letter) -> (GameState, GuessResult)
  Applique une tentative de lettre (bonne/mauvaise/déjà jouée/invalide).

- build_masked_word(secret_word, guessed_letters) -> str
  Construit une chaîne affichable du mot avec des '_' et des espaces.

- check_end_condition(game_state) -> GameState
  Met à jour le status ("playing", "won", "lost") selon l'état de la partie.
"""

from __future__ import annotations

import random
from typing import List, Set, Tuple

from core.models import GameState, GuessResult


# Liste blanche de status autorisés.
# On s'en sert comme "sécurité" au cas où le status serait modifié ailleurs par erreur.
_ALLOWED_STATUS = {"playing", "won", "lost"}


def start_game(words_list: List[str], max_errors: int) -> GameState:
    """
    Démarre une nouvelle partie à partir d'une liste de mots.

    Préconditions (contrat de la fonction)
    - words_list doit contenir au moins un mot.
    - max_errors doit être >= 1 (sinon on ne peut jamais perdre).

    Fonctionnement
    - Choisit un mot au hasard.
    - Initialise guessed_letters et wrong_letters comme des sets vides.
      -> set = pratique car pas de doublons et recherche rapide.
    - Met status à "playing".

    Args:
        words_list: liste de mots possibles (déjà normalisés idéalement)
        max_errors: nombre d'erreurs autorisées

    Returns:
        Un GameState prêt à être joué.
    """
    if not words_list:
        raise ValueError("Aucun mot disponible")

    if max_errors < 1:
        raise ValueError("max_errors doit être >= 1")

    # Choix aléatoire du mot secret.
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


def start_game_from_word(secret_word: str, max_errors: int) -> GameState:
    """
    Démarre une nouvelle partie à partir d'un mot déjà choisi.

    Pourquoi cette fonction existe
    - Dans le projet, les mots sont filtrés par difficulté avant d'arriver ici.
      Donc le mot est déjà déterminé dans la scène/ailleurs.
    - On évite de re-faire un random.choice ici, et on garde un point d'entrée propre.

    Préconditions
    - secret_word doit être non vide.
    - max_errors >= 1.

    Args:
        secret_word: mot à deviner (normalisé idéalement : minuscule, lettres)
        max_errors: nombre d'erreurs autorisées

    Returns:
        Un GameState prêt à être joué.
    """
    if not secret_word:
        raise ValueError("secret_word vide")

    if max_errors < 1:
        raise ValueError("max_errors doit être >= 1")

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
    Applique une tentative de lettre au GameState.

    Règles gérées ici
    - Si la partie est finie (status != "playing") : on refuse la tentative.
    - Si la lettre n'est pas valide (pas une seule lettre alpha) : on refuse.
    - Si la lettre a déjà été tentée (bonne ou mauvaise) : on refuse (result "already").
    - Sinon :
      - si la lettre est dans le mot : on l'ajoute à guessed_letters (result "good")
      - sinon : on l'ajoute à wrong_letters (result "bad")
    - Après la tentative : on appelle check_end_condition pour mettre à jour won/lost/playing.

    Préconditions attendues côté appelant
    - letter est une str de longueur 1
    - letter est une lettre (alphabétique)
    - letter est déjà normalisée (minuscule, accents normalisés)

    Args:
        game_state: état courant de la partie
        letter: lettre tentée

    Returns:
        (game_state, result)
        - game_state: mis à jour en place (sets modifiés) + status recalculé
        - result: GuessResult qui décrit ce qu'il s'est passé (pour feedback UI)
    """
    # Si on n'est plus en train de jouer, on n'accepte plus de tentative.
    if game_state.status != "playing":
        return game_state, GuessResult("invalid", "La partie est terminée")

    # Validation "safe" : on refuse tout ce qui n'est pas une lettre simple.
    if not isinstance(letter, str) or len(letter) != 1 or not letter.isalpha():
        return game_state, GuessResult("invalid", "Lettre invalide")

    # Déjà joué : on ne compte pas de nouvelle erreur, on renvoie juste un message.
    if letter in game_state.guessed_letters or letter in game_state.wrong_letters:
        return game_state, GuessResult("already", "Lettre déjà jouée")

    # Bonne ou mauvaise lettre
    if letter in game_state.secret_word:
        game_state.guessed_letters.add(letter)
        result = GuessResult("good", "Bonne lettre !")
    else:
        game_state.wrong_letters.add(letter)
        result = GuessResult("bad", "Mauvaise lettre...")

    # Après avoir modifié guessed/wrong, on vérifie si on a gagné ou perdu.
    game_state = check_end_condition(game_state)
    return game_state, result


def build_masked_word(secret_word: str, guessed_letters: Set[str]) -> str:
    """
    Construit une version "affichable" du mot secret.

    Principe
    - Pour chaque caractère du mot :
      - si c'est une lettre et qu'elle a été trouvée : on l'affiche
      - sinon : on affiche "_"
    - On met des espaces entre les caractères pour que ce soit plus lisible à l'écran.

    Exemple
    - secret_word = "banane"
    - guessed_letters = {"a", "n"}
    -> "_ a n a n _"

    Args:
        secret_word: mot complet
        guessed_letters: lettres correctes trouvées

    Returns:
        Chaîne avec underscores + lettres trouvées, séparées par des espaces.
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
    Met à jour game_state.status selon l'état actuel.

    Conditions de victoire
    - Toutes les lettres uniques du mot (alphabétiques) doivent être trouvées.
      Exemple : pour "banane", il faut {"b","a","n","e"} (pas besoin de "a" deux fois).

    Conditions de défaite
    - len(wrong_letters) >= max_errors

    Sinon
    - status reste "playing"

    Note importante
    - On ne modifie pas guessed_letters / wrong_letters ici.
      Cette fonction ne fait que décider du status.

    Returns:
        game_state (modifié sur son champ status)
    """
    # Sécurité : si un status bizarre arrive, on le remet en "playing".
    if game_state.status not in _ALLOWED_STATUS:
        game_state.status = "playing"

    # Ensemble des lettres "à deviner" (uniques).
    letters_in_word = {c for c in game_state.secret_word if c.isalpha()}

    # Victoire : toutes les lettres du mot sont incluses dans guessed_letters.
    if letters_in_word.issubset(game_state.guessed_letters):
        game_state.status = "won"
        return game_state

    # Défaite : trop d'erreurs.
    if len(game_state.wrong_letters) >= game_state.max_errors:
        game_state.status = "lost"
        return game_state

    # Sinon, la partie continue.
    game_state.status = "playing"
    return game_state
