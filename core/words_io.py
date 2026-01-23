"""
Objectif :
- Lire et écrire data/mots.txt (format par difficulté)

NOUVEAU FORMAT (simple)
- FACILE;mot;indice
- MOYEN;mot
- DIFFICILE;mot

Fonctions :
- load_words(path) -> list[str]                   (compat simple : renvoie tous les mots)
- load_words_by_difficulty(path, difficulty) -> (words, hints)
- validate_word(raw_word) -> (ok, normalized_word, message)
- add_word(path, raw_word) -> (ok, message)       (ajoute en MOYEN par défaut)

Règles :
- pas d'espaces
- pas de ';'
- minuscule
- lettres uniquement pour le mot
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def load_words(path: str) -> List[str]:
    """
    Charger les mots disponibles (tous niveaux mélangés).

    - Si fichier absent : []
    - Supporte l'ancien format (1 mot par ligne)
    - Supporte le nouveau format (DIFFICULTE;mot;indice?)
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []

    words: List[str] = []
    for line in lines:
        raw = line.strip()
        if not raw:
            continue

        # Nouveau format : DIFF;mot;...  -> on récupère la partie "mot"
        if ";" in raw:
            parts = raw.split(";")
            if len(parts) >= 2:
                w = parts[1].strip().lower()
            else:
                continue
        else:
            # Ancien format : mot seul
            w = raw.lower()

        if not w:
            continue
        words.append(w)

    return words


def load_words_by_difficulty(path: str, difficulty: str) -> Tuple[List[str], Dict[str, str]]:
    """
    Charger uniquement les mots d'une difficulté donnée.

    Retour :
    - words : liste de mots (list[str])
    - hints : dictionnaire {mot: indice} (uniquement pour FACILE)
      -> si pas d'indice, le mot n'est pas dans hints
    """
    difficulty = (difficulty or "").strip().upper()

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return [], {}

    words: List[str] = []
    hints: Dict[str, str] = {}

    for line in lines:
        raw = line.strip()
        if not raw:
            continue

        # On ignore les lignes qui ne sont pas au nouveau format
        if ";" not in raw:
            continue

        parts = raw.split(";")
        diff = parts[0].strip().upper()

        # On ne garde que la difficulté demandée
        if diff != difficulty:
            continue

        # On veut au moins DIFF;mot
        if len(parts) < 2:
            continue

        word = parts[1].strip().lower()
        if not word:
            continue

        words.append(word)

        # FACILE;mot;indice
        if diff == "FACILE" and len(parts) >= 3:
            hint = parts[2].strip()
            if hint:
                hints[word] = hint

    return words, hints


def validate_word(raw_word: str) -> Tuple[bool, str, str]:
    """
    Valider un mot saisi.

    Retour :
    - ok, normalized, message
    """
    if raw_word is None:
        return False, "", "Mot vide"

    word = str(raw_word).strip().lower()

    if not word:
        return False, "", "Le mot ne peut pas être vide"

    if " " in word:
        return False, "", "Le mot ne doit pas contenir d'espaces"

    if ";" in word:
        return False, "", "Caractère interdit : ;"

    # Pour notre jeu, on veut un mot "propre" (pas de chiffres, pas de symboles)
    if not word.isalpha():
        return False, "", "Le mot doit contenir uniquement des lettres"

    return True, word, "Mot valide"


def add_word(path: str, raw_word: str) -> Tuple[bool, str]:
    """
    Ajouter un mot dans mots.txt si valide et non-dup.

    IMPORTANT :
    - Pour rester simple, on ajoute en difficulté MOYEN (sans indice).
    - Le format écrit devient : MOYEN;mot
    """
    ok, word, msg = validate_word(raw_word)
    if not ok:
        return False, msg

    # On vérifie les doublons sur tous les mots (toutes difficultés)
    existing = load_words(path)
    if word in existing:
        return False, "Mot déjà présent"

    line_to_write = f"MOYEN;{word}"

    # Append propre : on ajoute une newline avant si nécessaire
    try:
        try:
            with open(path, "rb") as fb:
                fb.seek(0, 2)
                size = fb.tell()
                needs_newline = False
                if size > 0:
                    fb.seek(-1, 2)
                    last = fb.read(1)
                    needs_newline = last != b"\n"
        except FileNotFoundError:
            needs_newline = False

        with open(path, "a", encoding="utf-8") as f:
            if needs_newline:
                f.write("\n")
            f.write(line_to_write + "\n")

    except OSError:
        return False, "Erreur lors de l'écriture du fichier mots.txt"

    return True, "Mot ajouté (niveau MOYEN)"
