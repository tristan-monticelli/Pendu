"""
Objectif :
- Transformer des événements clavier en lettre utilisable par apply_guess.
- Filtrer ENTER, SHIFT, etc.
- Normaliser en minuscule.
- Par défaut : normaliser les accents (é -> e) pour simplifier.

"""

from __future__ import annotations

import unicodedata
from typing import Any, Optional

# Gestion souple de pygame.KEYDOWN
try:  # pragma: no cover
    import pygame  # type: ignore

    _KEYDOWN = pygame.KEYDOWN
except Exception:  # pragma: no cover
    # Valeur la plus courante pour KEYDOWN dans pygame (mais on reste tolérant)
    _KEYDOWN = 768


def is_valid_letter_event(event: Any) -> bool:
    """
    Vérifie si l'événement correspond à une lettre utilisable.

    Règles :
    - event.type doit correspondre à KEYDOWN
    - event.unicode doit exister, longueur 1
    - le caractère doit être une lettre
    """
    if event is None:
        return False

    ev_type = getattr(event, "type", None)
    if ev_type != _KEYDOWN:
        return False

    ch = getattr(event, "unicode", "")
    if not isinstance(ch, str) or len(ch) != 1:
        return False

    if not ch.isalpha():
        return False

    return True


def normalize_letter_input(event: Any) -> Optional[str]:
    """
    Convertit un event clavier en lettre normalisée.

    Retour :
    - lettre (str) si valide
    - None sinon
    """
    if not is_valid_letter_event(event):
        return None

    ch = event.unicode.lower()
    ch = normalize_accents_if_enabled(ch)
    return ch


def normalize_accents_if_enabled(ch: str) -> str:
    """
    Normalise les accents : "é" -> "e".

    Étapes :
    - NFD : décomposition
    - suppression des diacritiques (catégorie Mn)
    """
    # Si un jour vous voulez désactiver : return ch
    decomposed = unicodedata.normalize("NFD", ch)
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return stripped
