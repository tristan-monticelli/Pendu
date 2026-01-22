"""
Objectif :
- Lire et écrire data/mots.txt (1 mot par ligne)

Fonctions :
- load_words(path) -> list[str]
- validate_word(raw_word) -> (ok, normalized_word, message)
- add_word(path, raw_word) -> (ok, message)

Règles :
- pas d'espaces
- pas de ';'
- minuscule
"""

from __future__ import annotations

from typing import List, Tuple


def load_words(path: str) -> List[str]:
    """
    Charger les mots disponibles.

    - Si fichier absent : []
    - Nettoyage : strip + lower
    - Ignore lignes vides
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []

    words: List[str] = []
    for line in lines:
        w = line.strip().lower()
        if not w:
            continue
        words.append(w)
    return words


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

    if not any(ch.isalpha() for ch in word):
        return False, "", "Le mot doit contenir des lettres"

    return True, word, "Mot valide"


def add_word(path: str, raw_word: str) -> Tuple[bool, str]:
    """
    Ajouter un mot dans mots.txt si valide et non-dup.

    Retour :
    - ok, message
    """
    ok, word, msg = validate_word(raw_word)
    if not ok:
        return False, msg

    existing = load_words(path)
    if word in existing:
        return False, "Mot déjà présent"

    # Append propre : on ajoute une newline avant si le fichier existe et ne finit pas par \n
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
            f.write(word + "\n")

    except OSError:
        return False, "Erreur lors de l'écriture du fichier mots.txt"

    return True, "Mot ajouté"
