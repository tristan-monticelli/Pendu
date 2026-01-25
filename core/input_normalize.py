"""
Objectif
- Transformer un événement clavier (KEYDOWN) en une lettre exploitable par le jeu.
- Ignorer tout le reste : ENTER, SHIFT, CTRL, flèches, etc.
- Normaliser en minuscule.
- Par défaut, retirer les accents ("é" -> "e") pour éviter les problèmes de comparaison
  et garder un comportement simple dans le pendu.

Pourquoi on a ce fichier
- Dans Pygame, un event KEYDOWN contient beaucoup d'informations (key, unicode, mod...).
  Dans notre jeu, on a juste besoin d'une lettre propre.
- En isolant ça ici :
  - la scène de jeu reste plus lisible
  - on peut tester facilement la validation/normalisation sans toucher à l'UI

Conventions
- Les fonctions retournent None si l'entrée ne correspond pas à une lettre utilisable.
- Le code reste "tolérant" : si Pygame n'est pas importable, on garde une valeur par défaut
  pour KEYDOWN afin d'éviter que le module casse (utile pour certains tests/outils).
"""

from __future__ import annotations

import unicodedata
from typing import Any, Optional

# Gestion souple de pygame.KEYDOWN
try:  # pragma: no cover
    import pygame  # type: ignore

    _KEYDOWN = pygame.KEYDOWN
except Exception:  # pragma: no cover
    # Valeur la plus courante pour KEYDOWN dans pygame.
    # On s'en sert comme fallback si pygame n'est pas disponible.
    _KEYDOWN = 768


def is_valid_letter_event(event: Any) -> bool:
    """
    Vérifie si un event correspond à une lettre utilisable par le jeu.

    Conditions minimales
    - event n'est pas None
    - event.type == KEYDOWN (donc c'est bien une frappe clavier)
    - event.unicode existe et est une string de longueur 1
      (ça évite les touches "spéciales" et les séquences)
    - le caractère est une lettre (isalpha)

    Exemple
    - Appuyer sur "A" -> True
    - Appuyer sur "Enter" -> False (unicode vide ou non lettre)
    - Appuyer sur "1" -> False (pas une lettre)
    """
    if event is None:
        return False

    # getattr évite un crash si on reçoit un objet qui n'a pas d'attribut "type"
    ev_type = getattr(event, "type", None)
    if ev_type != _KEYDOWN:
        return False

    # unicode = caractère réellement tapé (plus pratique que event.key pour gérer AZERTY, etc.)
    ch = getattr(event, "unicode", "")
    if not isinstance(ch, str) or len(ch) != 1:
        return False

    if not ch.isalpha():
        return False

    return True


def normalize_letter_input(event: Any) -> Optional[str]:
    """
    Convertit un event clavier en lettre normalisée.

    Retour
    - une lettre (str) si l'événement est valide
    - None si l'événement ne correspond pas à une lettre

    Normalisations appliquées
    - passage en minuscule
    - suppression des accents (si activée) pour harmoniser les comparaisons
      avec les mots du fichier (souvent stockés sans accents dans ce type de jeu)
    """
    if not is_valid_letter_event(event):
        return None

    ch = event.unicode.lower()
    ch = normalize_accents_if_enabled(ch)
    return ch


def normalize_accents_if_enabled(ch: str) -> str:
    """
    Normalise les accents : transforme par exemple "é" en "e".

    Pourquoi c'est utile
    - Simplifie la logique du pendu : une lettre avec accent reste traitée comme sa base.
    - Évite certains soucis de polices / rendu ou de comparaison selon les fichiers.

    Méthode utilisée
    - NFD : décomposition Unicode (ex: "é" -> "e" + accent séparé)
    - suppression des diacritiques (catégorie Mn)
    - reconstruction de la chaîne "sans accents"

    Note
    - Si un jour on veut désactiver cette règle (gérer les accents "vraiment"),
      il suffit de renvoyer directement ch au début de la fonction.
    """
    # Si un jour vous voulez désactiver : return ch
    decomposed = unicodedata.normalize("NFD", ch)
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return stripped
