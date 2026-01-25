"""
Idée générale
- Ce fichier regroupe des fonctions utilitaires pour dessiner une UI cohérente :
  rectangles cartoon (coins arrondis + contour noir), texte avec effets,
  boutons, cards, bulles de dialogue, lettres d'alphabet, etc.

Pourquoi c’est séparé du reste
- Les scènes (menu, game, leaderboard...) ne devraient pas contenir tout le code
  de dessin bas niveau, sinon elles deviennent illisibles.
- Ici on centralise le "style", comme ça si on change un détail (épaisseur bordure,
  rayon, ombre), on le change une fois et ça impacte tout le jeu.

Important
- Ce module ne gère pas les clics / events : il dessine seulement.
- Les constantes de style viennent de settings.py (couleurs, épaisseurs, rayons...).
"""

from __future__ import annotations

import pygame
import math
from typing import Tuple, Optional, List

from settings import (
    COLORS,
    BORDER_WIDTH_THIN,
    BORDER_WIDTH_NORMAL,
    BORDER_WIDTH_THICK,
    CORNER_RADIUS_SMALL,
    CORNER_RADIUS_NORMAL,
    CORNER_RADIUS_LARGE,
    SHADOW_OFFSET,
    SHADOW_ALPHA,
)

# Police système utilisée en fallback pour certains caractères non supportés par la police Simpson.
# Exemple : le ":" (deux-points) qui peut poser problème selon la fonte.
_fallback_font = None


def _get_fallback_font(size: int = 36) -> pygame.font.Font:
    """
    Renvoie une police système Pygame (fallback).

    On utilise un cache (_fallback_font) pour éviter de recréer la font à chaque appel.
    """
    global _fallback_font
    if _fallback_font is None:
        _fallback_font = pygame.font.Font(None, size)
    return _fallback_font


def normalize_text_for_simpson(text: str) -> str:
    """
    Simplifie le texte pour qu'il passe mieux avec la police Simpson.

    Principe
    - On enlève les accents (é -> e, à -> a, ç -> c, etc.).
    - On garde volontairement ":" car on le gère ensuite avec un rendu fallback.

    Remarque
    - Ça évite les bugs d'affichage ou les caractères "vides" si la police ne contient pas
      certains glyphes.
    """
    import unicodedata

    # Décomposition NFD : sépare lettre et accent
    text = unicodedata.normalize("NFD", text)
    # On supprime les marques d’accents (Mn)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def safe_render(
    font: pygame.font.Font,
    text: str,
    antialias: bool,
    color: Tuple[int, int, int],
) -> pygame.Surface:
    """
    Rendu texte "sécurisé" pour éviter les soucis de caractères avec la police Simpson.

    Ce que ça gère
    - Normalisation des accents.
    - Si le texte contient ":" :
      - on rend le reste avec la police Simpson,
      - on rend ":" avec une police système,
      - puis on assemble tout sur une surface finale.

    Retour
    - Surface Pygame prête à blit.
    """
    text = normalize_text_for_simpson(text)

    # Cas simple : aucun caractère problématique
    if ":" not in text:
        return font.render(text, antialias, color)

    # Cas ":" : rendu par morceaux
    font_size = font.get_height()
    system_font = pygame.font.Font(None, font_size)

    parts = text.split(":")
    total_width = 0
    surfaces = []

    for i, part in enumerate(parts):
        if part:
            part_surface = font.render(part, antialias, color)
            surfaces.append(("text", part_surface))
            total_width += part_surface.get_width()

        if i < len(parts) - 1:
            colon_surface = system_font.render(":", antialias, color)
            surfaces.append(("colon", colon_surface))
            total_width += colon_surface.get_width()

    max_height = font.get_height()
    final_surface = pygame.Surface((total_width, max_height), pygame.SRCALPHA)

    x_offset = 0
    for _, surface in surfaces:
        y_offset = (max_height - surface.get_height()) // 2
        final_surface.blit(surface, (x_offset, y_offset))
        x_offset += surface.get_width()

    return final_surface


# FORMES DE BASE (cartoon)
def draw_cartoon_rect(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fill_color: Tuple[int, int, int],
    border_color: Tuple[int, int, int] = COLORS["border_black"],
    border_width: int = BORDER_WIDTH_NORMAL,
    corner_radius: int = CORNER_RADIUS_NORMAL,
    shadow: bool = True,
) -> None:
    """
    Dessine un rectangle "cartoon" (le bloc de base qu’on réutilise partout).

    Effets
    - Remplissage couleur
    - Contour noir épais
    - Ombre portée (optionnelle) : décalée en bas à droite, avec alpha

    Note
    - L'ombre est dessinée avant le rectangle principal, sinon elle passerait au-dessus.
    """
    if shadow:
        shadow_rect = rect.copy()
        shadow_rect.x += SHADOW_OFFSET
        shadow_rect.y += SHADOW_OFFSET

        shadow_surface = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
        shadow_color = (*COLORS["shadow"], SHADOW_ALPHA)
        pygame.draw.rect(
            shadow_surface,
            shadow_color,
            shadow_surface.get_rect(),
            border_radius=corner_radius,
        )
        surface.blit(shadow_surface, shadow_rect.topleft)

    pygame.draw.rect(surface, fill_color, rect, border_radius=corner_radius)
    pygame.draw.rect(
        surface,
        border_color,
        rect,
        width=border_width,
        border_radius=corner_radius,
    )


def draw_speech_bubble(
    surface: pygame.Surface,
    text: str,
    pos: Tuple[int, int],
    font: pygame.font.Font,
    max_width: int = 500,
    tail_direction: str = "bottom",
    bg_color: Tuple[int, int, int] = COLORS["text_white"],
) -> pygame.Rect:
    """
    Dessine une bulle de dialogue simple (style BD).

    Étapes
    - On découpe le texte en lignes en respectant max_width.
    - On dessine la bulle (rect cartoon) + une petite "queue" (triangle).
    - On rend chaque ligne centrée dans la bulle.

    Retour
    - Le Rect de la bulle (utile si une scène veut aligner autre chose autour).
    """
    padding = 20
    tail_size = 20

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        test_surface = safe_render(font, test_line, True, COLORS["text_black"])

        if test_surface.get_width() > max_width - (2 * padding):
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
        else:
            current_line.append(word)

    if current_line:
        lines.append(" ".join(current_line))

    line_height = font.get_height()
    bubble_width = (
        max(safe_render(font, line, True, COLORS["text_black"]).get_width() for line in lines)
        + (2 * padding)
    )
    bubble_height = len(lines) * line_height + (2 * padding)

    bubble_rect = pygame.Rect(pos[0], pos[1], bubble_width, bubble_height)

    draw_cartoon_rect(
        surface,
        bubble_rect,
        fill_color=bg_color,
        border_width=BORDER_WIDTH_THICK,
        corner_radius=CORNER_RADIUS_LARGE,
        shadow=True,
    )

    tail_points = []
    if tail_direction == "bottom":
        tail_points = [
            (bubble_rect.centerx - tail_size, bubble_rect.bottom),
            (bubble_rect.centerx, bubble_rect.bottom + tail_size),
            (bubble_rect.centerx + tail_size, bubble_rect.bottom),
        ]
    elif tail_direction == "top":
        tail_points = [
            (bubble_rect.centerx - tail_size, bubble_rect.top),
            (bubble_rect.centerx, bubble_rect.top - tail_size),
            (bubble_rect.centerx + tail_size, bubble_rect.top),
        ]

    if tail_points:
        pygame.draw.polygon(surface, bg_color, tail_points)
        pygame.draw.lines(surface, COLORS["border_black"], False, tail_points, BORDER_WIDTH_THICK)

    y_offset = pos[1] + padding
    for line in lines:
        text_surface = safe_render(font, line, True, COLORS["text_black"])
        text_rect = text_surface.get_rect(centerx=bubble_rect.centerx, top=y_offset)
        surface.blit(text_surface, text_rect)
        y_offset += line_height

    return bubble_rect


# BOUTONS (version dessinée, pas "widget" interactif)
def draw_simpson_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    bg_color: Tuple[int, int, int] = COLORS["simpson_yellow"],
    is_hovered: bool = False,
    is_pressed: bool = False,
    enabled: bool = True,
) -> None:
    """
    Dessine un bouton visuel (style Simpson).

    Paramètres d'état
    - hovered : on éclaire légèrement la couleur de fond
    - pressed : on décale un peu le bouton et on enlève l’ombre (effet "enfoncé")
    - enabled False : bouton grisé

    Remarque
    - Le texte est forcé en noir pour la lisibilité.
    - L’ombre du texte est volontairement très légère (gris) pour rester lisible.
    """
    if not enabled:
        bg_color = COLORS["text_gray"]

    if is_hovered and enabled:
        bg_color = tuple(min(c + 30, 255) for c in bg_color)

    draw_rect = rect.copy()
    shadow = True

    if is_pressed and enabled:
        draw_rect.x += SHADOW_OFFSET // 2
        draw_rect.y += SHADOW_OFFSET // 2
        shadow = False

    draw_cartoon_rect(
        surface,
        draw_rect,
        fill_color=bg_color,
        border_width=BORDER_WIDTH_THICK,
        corner_radius=CORNER_RADIUS_NORMAL,
        shadow=shadow,
    )

    text_color = COLORS["text_black"]
    text_surface = safe_render(font, text, True, text_color)
    text_rect = text_surface.get_rect(center=draw_rect.center)

    if enabled:
        shadow_surface = safe_render(font, text, True, (100, 100, 100))
        shadow_rect = shadow_surface.get_rect(center=(draw_rect.centerx + 2, draw_rect.centery + 2))
        surface.blit(shadow_surface, shadow_rect)

    surface.blit(text_surface, text_rect)


# CARDS / CONTAINERS
def draw_cartoon_card(
    surface: pygame.Surface,
    rect: pygame.Rect,
    bg_color: Tuple[int, int, int] = COLORS["bg_card"],
    title: Optional[str] = None,
    title_font: Optional[pygame.font.Font] = None,
) -> pygame.Rect:
    """
    Dessine une card (container) pour regrouper des infos.

    Option
    - Si title + title_font : on affiche un titre et une ligne de séparation.

    Retour
    - Rect "content" = zone utilisable à l'intérieur (pratique pour placer le contenu).
    """
    draw_cartoon_rect(
        surface,
        rect,
        fill_color=bg_color,
        border_width=BORDER_WIDTH_THICK,
        corner_radius=CORNER_RADIUS_LARGE,
        shadow=True,
    )

    content_rect = rect.copy()
    if title and title_font:
        title_height = 50

        title_y = rect.y + 28
        title_surface = safe_render(title_font, title, True, COLORS["text_black"])
        title_text_rect = title_surface.get_rect(center=(rect.centerx, title_y))
        surface.blit(title_surface, title_text_rect)

        line_y = rect.y + title_height
        pygame.draw.line(
            surface,
            COLORS["border_black"],
            (rect.left + 20, line_y),
            (rect.right - 20, line_y),
            BORDER_WIDTH_NORMAL,
        )

        content_rect.y += title_height
        content_rect.height -= title_height

    return content_rect


# ALPHABET (une lettre = une case dessinée)
def draw_alphabet_letter(
    surface: pygame.Surface,
    letter: str,
    pos: Tuple[int, int],
    size: int,
    font: pygame.font.Font,
    state: str = "available",
    is_hovered: bool = False,
) -> pygame.Rect:
    """
    Dessine une case de lettre (alphabet cliquable dans la scène de jeu).

    state
    - available : pas encore jouée
    - correct : lettre trouvée
    - wrong : lettre fausse

    Retour
    - Rect de la case (utile pour détecter un clic dans la scène).
    """
    rect = pygame.Rect(pos[0], pos[1], size, size)

    colors_map = {
        "available": COLORS["letter_available"],
        "correct": COLORS["letter_correct"],
        "wrong": COLORS["letter_wrong"],
    }
    bg_color = colors_map.get(state, COLORS["letter_available"])

    if is_hovered and state == "available":
        bg_color = tuple(min(c + 30, 255) for c in bg_color)

    draw_cartoon_rect(
        surface,
        rect,
        fill_color=bg_color,
        border_width=BORDER_WIDTH_NORMAL,
        corner_radius=CORNER_RADIUS_SMALL,
        shadow=(state == "available"),
    )

    text_surface = safe_render(font, letter, True, COLORS["text_black"])
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

    return rect


# INDICATEURS (coeurs / indices)
def draw_heart_indicator(
    surface: pygame.Surface,
    pos: Tuple[int, int],
    total: int,
    remaining: int,
    heart_full_img: pygame.Surface,
    heart_empty_img: pygame.Surface,
    spacing: int = 10,
) -> None:
    """
    Affiche une rangée de coeurs (vies).

    total = nombre de coeurs affichés
    remaining = combien sont "pleins"
    """
    x_offset = pos[0]
    heart_width = heart_full_img.get_width()

    for i in range(total):
        heart_img = heart_full_img if i < remaining else heart_empty_img
        surface.blit(heart_img, (x_offset, pos[1]))
        x_offset += heart_width + spacing


def draw_hint_indicator(
    surface: pygame.Surface,
    pos: Tuple[int, int],
    total: int,
    remaining: int,
    hint_available_img: pygame.Surface,
    hint_used_img: pygame.Surface,
    spacing: int = 10,
) -> None:
    """
    Affiche une rangée d'icônes d'indices (disponible / utilisé).
    """
    x_offset = pos[0]
    hint_width = hint_available_img.get_width()

    for i in range(total):
        hint_img = hint_available_img if i < remaining else hint_used_img
        surface.blit(hint_img, (x_offset, pos[1]))
        x_offset += hint_width + spacing


# TEXTE (effets simples)
def draw_text_with_shadow(
    surface: pygame.Surface,
    text: str,
    pos: Tuple[int, int],
    font: pygame.font.Font,
    color: Tuple[int, int, int] = COLORS["text_black"],
    shadow_color: Tuple[int, int, int] = COLORS["text_shadow_blue"],
    shadow_offset: Tuple[int, int] = (3, 3),
    centered: bool = False,
) -> pygame.Rect:
    """
    Texte avec ombre portée (effet cartoon).

    centered=True : pos est le centre du texte (pratique pour titres / UI centrée).
    """
    text = normalize_text_for_simpson(text)

    shadow_surface = safe_render(font, text, True, shadow_color)
    shadow_pos = (pos[0] + shadow_offset[0], pos[1] + shadow_offset[1])

    if centered:
        shadow_rect = shadow_surface.get_rect(center=pos)
        shadow_pos = (shadow_rect.x + shadow_offset[0], shadow_rect.y + shadow_offset[1])

    surface.blit(shadow_surface, shadow_pos)

    text_surface = safe_render(font, text, True, color)

    if centered:
        text_rect = text_surface.get_rect(center=pos)
        surface.blit(text_surface, text_rect)
        return text_rect

    surface.blit(text_surface, pos)
    return text_surface.get_rect(topleft=pos)


def draw_outlined_text(
    surface: pygame.Surface,
    text: str,
    pos: Tuple[int, int],
    font: pygame.font.Font,
    color: Tuple[int, int, int] = COLORS["text_white"],
    outline_color: Tuple[int, int, int] = COLORS["border_black"],
    outline_width: int = 2,
    centered: bool = False,
) -> pygame.Rect:
    """
    Texte avec contour (très utile sur des fonds clairs / chargés).

    Technique
    - On redessine le texte plusieurs fois autour (dx/dy), puis le texte principal au-dessus.
    """
    text_surface = safe_render(font, text, True, color)

    if centered:
        text_rect = text_surface.get_rect(center=pos)
        base_pos = text_rect.topleft
    else:
        base_pos = pos

    outline_surface = safe_render(font, text, True, outline_color)

    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                surface.blit(outline_surface, (base_pos[0] + dx, base_pos[1] + dy))

    surface.blit(text_surface, base_pos)
    return text_surface.get_rect(topleft=base_pos)


# PETITS EFFETS
def create_shake_offset(amplitude: int = 5) -> Tuple[int, int]:
    """
    Renvoie un offset aléatoire (effet tremblement).
    Utilisé par exemple quand on veut "secouer" un élément après une erreur.
    """
    import random
    return (random.randint(-amplitude, amplitude), random.randint(-amplitude, amplitude))


def draw_pulse_effect(
    surface: pygame.Surface,
    center: Tuple[int, int],
    max_radius: int,
    color: Tuple[int, int, int],
    pulse_phase: float,
) -> None:
    """
    Effet de pulsation : cercle qui grandit et disparaît.

    pulse_phase est attendu entre 0.0 et 1.0 (piloté par la scène qui anime).
    """
    radius = int(max_radius * pulse_phase)
    alpha = int(255 * (1.0 - pulse_phase))

    if radius > 0:
        temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, (*color, alpha), (radius, radius), radius)
        surface.blit(temp_surface, (center[0] - radius, center[1] - radius))



# FOND + UTILITAIRES
def format_duration(seconds: int) -> str:
    """
    Convertit une durée en secondes vers "MM:SS".

    On sécurise un peu :
    - None -> 0
    - valeurs négatives -> 0
    """
    if seconds is None:
        seconds = 0

    seconds = int(seconds)
    if seconds < 0:
        seconds = 0

    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes:02d}:{sec:02d}"


# Cache du background (chargé une fois puis réutilisé).
_background_image = None


def draw_simpson_background(surface: pygame.Surface) -> None:
    """
    Dessine le fond du jeu.

    Logique
    - On essaie de charger assets/images/background.png.
    - Si ça échoue : fallback "ciel + herbe" (pour éviter un écran noir / crash).

    Note
    - On garde _background_image en global pour ne pas relire le fichier à chaque frame.
    """
    global _background_image

    width, height = surface.get_size()

    if _background_image is None:
        try:
            import os

            bg_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "assets", "images", "background.png"
            )

            if os.path.exists(bg_path):
                _background_image = pygame.image.load(bg_path).convert()
                _background_image = pygame.transform.scale(_background_image, (width, height))
            else:
                bg_path = "assets/images/background.png"
                if os.path.exists(bg_path):
                    _background_image = pygame.image.load(bg_path).convert()
                    _background_image = pygame.transform.scale(_background_image, (width, height))
                else:
                    _background_image = "NOT_FOUND"
        except Exception as e:
            print(f"Erreur chargement fond: {e}")
            _background_image = "NOT_FOUND"

    if _background_image and _background_image != "NOT_FOUND":
        if _background_image.get_size() != (width, height):
            _background_image = pygame.transform.scale(_background_image, (width, height))
        surface.blit(_background_image, (0, 0))
    else:
        sky_height = int(height * 0.66)
        surface.fill(COLORS["bg_sky"], pygame.Rect(0, 0, width, sky_height))
        grass_rect = pygame.Rect(0, sky_height, width, height - sky_height)
        surface.fill(COLORS["bg_grass"], grass_rect)


def draw_simple_cloud(
    surface: pygame.Surface,
    pos: Tuple[int, int],
    size: int = 100,
) -> None:
    """
    Dessine un nuage simple (3 cercles qui se chevauchent).

    C’est volontairement basique : ça sert surtout de décor / background.
    """
    circle_radius = size // 3

    pygame.draw.circle(surface, COLORS["bg_clouds"], (pos[0] - circle_radius, pos[1]), circle_radius)
    pygame.draw.circle(surface, COLORS["border_black"], (pos[0] - circle_radius, pos[1]), circle_radius, BORDER_WIDTH_THIN)

    pygame.draw.circle(surface, COLORS["bg_clouds"], pos, int(circle_radius * 1.3))
    pygame.draw.circle(surface, COLORS["border_black"], pos, int(circle_radius * 1.3), BORDER_WIDTH_THIN)

    pygame.draw.circle(surface, COLORS["bg_clouds"], (pos[0] + circle_radius, pos[1]), circle_radius)
    pygame.draw.circle(surface, COLORS["border_black"], (pos[0] + circle_radius, pos[1]), circle_radius, BORDER_WIDTH_THIN)
