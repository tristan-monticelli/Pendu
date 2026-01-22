"""
BUT DU FICHIER
- Mettre 3-4 fonctions d'affichage très simples pour éviter de recopier du code
  dans toutes les scènes.

RÈGLES
- Ici on fait seulement du dessin (pas de logique de jeu).
- Les scènes appellent ces fonctions, c'est tout.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pygame

from settings import COLOR_BG, COLOR_TEXT, COLOR_MUTED, COLOR_BTN, COLOR_INPUT_BORDER


def clear_screen(screen: pygame.Surface) -> None:
    """
    Efface l'écran avec la couleur de fond.
    """
    screen.fill(COLOR_BG)


def draw_title(screen: pygame.Surface, fonts: Dict[str, Any], text: str) -> None:
    """
    Affiche un titre centré en haut.
    - On utilise fonts["title"].
    """
    font = fonts["title"]
    surface = font.render(text, True, COLOR_TEXT)

    x = screen.get_width() // 2
    y = 50  # position fixe 
    rect = surface.get_rect(center=(x, y))

    screen.blit(surface, rect)


def format_duration(seconds: int) -> str:
    """
    Convertit un temps en secondes vers un format "MM:SS".

    Exemple :
    - 95 secondes -> "01:35"
    """
    if seconds is None:
        seconds = 0

    seconds = int(seconds)
    if seconds < 0:
        seconds = 0

    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes:02d}:{sec:02d}"


def draw_text_lines(
    screen: pygame.Surface,
    fonts: Dict[str, Any],
    lines: List[str],
    x: int,
    y: int,
    small: bool = False,
) -> None:
    """
    Affiche plusieurs lignes de texte les unes sous les autres.

    Paramètres :
    - lines : liste de lignes (str)
    - x, y : position de départ
    - small : si True -> utilise fonts["small"], sinon fonts["body"]

    Exemple d'utilisation :
    draw_text_lines(screen, fonts, ["Ligne 1", "Ligne 2"], 60, 140)
    """
    font = fonts["small"] if small else fonts["body"]

    current_y = y
    for line in lines:
        surface = font.render(str(line), True, COLOR_TEXT)
        screen.blit(surface, (x, current_y))
        current_y += surface.get_height() + 8  # espacement simple


def draw_table(
    screen: pygame.Surface,
    fonts: Dict[str, Any],
    headers: List[str],
    rows: List[List[str]],
    x: int,
    y: int,
) -> None:
    """
    Dessine un tableau très simple (utile pour le classement).

    Règles de simplicité :
    - largeur colonne fixe
    - police small pour headers, body pour rows
    - pas de calcul compliqué

    Paramètres :
    - headers : titres des colonnes
    - rows : lignes (list de cellules)
    - x, y : position du coin haut gauche du tableau
    """
    header_font = fonts["small"]
    row_font = fonts["body"]

    col_width = 180
    row_height = 36

    # 1) Fond du tableau (un grand rectangle)
    table_w = col_width * len(headers)
    table_h = row_height * (1 + len(rows))  # +1 pour les headers
    pygame.draw.rect(screen, COLOR_BTN, pygame.Rect(x, y, table_w, table_h), border_radius=10)

    # 2) Headers
    for i, head in enumerate(headers):
        sx = x + i * col_width + 10
        sy = y + 8
        surface = header_font.render(str(head), True, COLOR_TEXT)
        screen.blit(surface, (sx, sy))

    # Ligne séparatrice sous headers
    pygame.draw.line(
        screen,
        COLOR_INPUT_BORDER,
        (x, y + row_height),
        (x + table_w, y + row_height),
        2,
    )

    # 3) Rows
    for r_index, row in enumerate(rows):
        for c_index, cell in enumerate(row):
            sx = x + c_index * col_width + 10
            sy = y + row_height + r_index * row_height + 8
            surface = row_font.render(str(cell), True, COLOR_MUTED)
            screen.blit(surface, (sx, sy))


def draw_hint_bottom(screen: pygame.Surface, fonts: Dict[str, Any], text: str) -> None:
    """
    Affiche une indication simple en bas de l'écran (ex: "ESC pour revenir").
    """
    font = fonts["small"]
    surface = font.render(text, True, COLOR_MUTED)

    x = screen.get_width() // 2
    y = screen.get_height() - 20
    rect = surface.get_rect(center=(x, y))

    screen.blit(surface, rect)
