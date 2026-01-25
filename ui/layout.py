"""
But du fichier
- Éviter de refaire des calculs de positions dans chaque scène.
- Donner des helpers simples pour placer des boutons / champs / zones UI.

Ce fichier fait uniquement du "layout"
- Il renvoie des pygame.Rect (positions + tailles).
- Il ne dessine rien.
- Il ne gère aucun event.
- Il ne contient pas de logique de jeu.

Pourquoi on utilise pygame.Rect
- C’est l’objet standard de Pygame pour représenter une zone cliquable/affichable.
- Il sert autant pour le placement (x, y, width, height) que pour la collision (collidepoint).
"""

from __future__ import annotations

from typing import List, Tuple

import pygame


def center_rect(
    window_w: int,
    window_h: int,
    rect_w: int,
    rect_h: int,
    y_offset: int = 0,
) -> pygame.Rect:
    """
    Crée un rectangle centré dans la fenêtre.

    Usage typique
    - Centrer un bouton principal, un titre, un champ de saisie, etc.
    - Ajuster légèrement la position verticale avec y_offset (ex: pour remonter un titre).

    Paramètres
    - window_w, window_h : dimensions de la fenêtre (en pixels)
    - rect_w, rect_h : dimensions du rectangle à créer (en pixels)
    - y_offset : décalage vertical ajouté au centrage
      (négatif = on remonte, positif = on descend)

    Retour
    - pygame.Rect positionné au centre (avec le décalage demandé)
    """
    x = (window_w - rect_w) // 2
    y = (window_h - rect_h) // 2 + y_offset
    return pygame.Rect(x, y, rect_w, rect_h)


def vertical_stack(
    start_x: int,
    start_y: int,
    rect_w: int,
    rect_h: int,
    count: int,
    gap: int,
) -> List[pygame.Rect]:
    """
    Crée une colonne de rectangles alignés verticalement (stack).

    Idée
    - On place le premier rectangle en (start_x, start_y).
    - Chaque rectangle suivant est placé en dessous, avec un espacement constant (gap).

    Paramètres
    - start_x, start_y : position du premier rectangle (coin supérieur gauche)
    - rect_w, rect_h : taille de chaque rectangle
    - count : nombre de rectangles à générer
    - gap : espace vertical entre deux rectangles

    Retour
    - Liste de pygame.Rect, dans l'ordre de haut en bas.
    """
    rects: List[pygame.Rect] = []

    for i in range(count):
        x = start_x
        # Chaque rectangle descend d'un "pas" : hauteur + gap
        y = start_y + i * (rect_h + gap)
        rects.append(pygame.Rect(x, y, rect_w, rect_h))

    return rects


def place_under(
    rect_above: pygame.Rect,
    rect_w: int,
    rect_h: int,
    gap: int = 10,
) -> pygame.Rect:
    """
    Crée un rectangle placé juste sous un autre rectangle (même x).

    Usage typique
    - Mettre un champ sous un titre.
    - Mettre un bouton "Retour" sous une card.
    - Enchaîner des éléments sans recalculer "à la main".

    Paramètres
    - rect_above : rectangle de référence (celui du dessus)
    - rect_w, rect_h : dimensions du nouveau rectangle
    - gap : espace vertical entre les deux

    Retour
    - pygame.Rect positionné juste en dessous du rect_above.
    """
    x = rect_above.x
    y = rect_above.y + rect_above.height + gap
    return pygame.Rect(x, y, rect_w, rect_h)


def center_x(rect: pygame.Rect, window_w: int) -> pygame.Rect:
    """
    Centre un rectangle horizontalement (sans changer sa position verticale).

    Différence avec center_rect
    - center_rect crée un nouveau rect à partir de dimensions.
    - center_x part d'un rect existant et ne modifie que x.

    Paramètres
    - rect : rectangle à centrer
    - window_w : largeur de la fenêtre

    Retour
    - Une copie du rect, centrée sur l'axe X.
      (On renvoie une copie pour éviter de modifier le rect original par surprise.)
    """
    new_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height)
    new_rect.x = (window_w - rect.width) // 2
    return new_rect
