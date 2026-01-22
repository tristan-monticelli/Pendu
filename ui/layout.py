"""
BUT DU FICHIER
- Aider à placer des éléments (boutons / champs) sans refaire des calculs partout.

RÈGLES
- Ici on fait juste des calculs de positions.
- Pas de logique de jeu, pas d'event, pas de dessin.
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
    Renvoie un rectangle centré dans la fenêtre.

    Paramètres :
    - window_w, window_h : taille de la fenêtre
    - rect_w, rect_h : taille du rectangle à créer
    - y_offset : décalage vertical (ex: -100 pour le remonter)

    Exemple :
    rect = center_rect(WINDOW_WIDTH, WINDOW_HEIGHT, 400, 50, y_offset=-100)
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
    Crée une liste de rectangles alignés verticalement.

    Paramètres :
    - start_x, start_y : position du premier rectangle (en haut)
    - rect_w, rect_h : taille de chaque rectangle
    - count : nombre de rectangles à créer
    - gap : espace entre chaque rectangle

    Exemple :
    rects = vertical_stack(100, 200, 300, 50, 3, 15)
    -> rects[0], rects[1], rects[2]
    """
    rects: List[pygame.Rect] = []

    for i in range(count):
        x = start_x
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
    Place un rectangle juste en dessous d'un autre.

    Paramètres :
    - rect_above : rectangle de référence
    - rect_w, rect_h : taille du nouveau rectangle
    - gap : espace vertical entre les deux

    Exemple :
    rect2 = place_under(rect1, 300, 50, gap=15)
    """
    x = rect_above.x
    y = rect_above.y + rect_above.height + gap
    return pygame.Rect(x, y, rect_w, rect_h)


def center_x(rect: pygame.Rect, window_w: int) -> pygame.Rect:
    """
    Centre un rectangle horizontalement dans la fenêtre (sans changer y).

    Paramètres :
    - rect : rectangle à déplacer
    - window_w : largeur de la fenêtre

    Retour :
    - un nouveau rect (copie) centré
    """
    new_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height)
    new_rect.x = (window_w - rect.width) // 2
    return new_rect
