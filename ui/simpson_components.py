"""
Composants UI réutilisables (style Simpson)

Objectif
- Regrouper des "widgets" simples et réutilisables pour les scènes : boutons, grille de lettres,
  champ de saisie, notifications, indicateurs (vies/indices) et affichage du mot.
- Garder les scènes lisibles : une scène place les éléments, leur passe les events, et appelle draw().

Organisation
- Ce fichier contient surtout de la logique d'interaction (hover/clic/saisie) et l'assemblage.
- Le dessin pur (look Simpson : contours, ombres, couleurs, etc.) est dans ui/simpson_theme.py.
  Ici, on réutilise ces fonctions pour rester cohérent sur tout le jeu.

Important
- Les composants ne connaissent pas les "scènes". Ils reçoivent juste des infos (event, souris, font)
  et renvoient éventuellement un résultat (ex: un clic, un submit).
"""

from __future__ import annotations

import pygame
from typing import Callable, Optional, Tuple, List, Dict
from dataclasses import dataclass

from settings import (
    COLORS,
    BUTTON_SIZES,
    LETTER_BOX_SIZE,
    LETTER_SPACING,
    ALPHABET_LAYOUT,
)

from ui.simpson_theme import (
    draw_simpson_button,
    draw_alphabet_letter,
    draw_heart_indicator,
    draw_hint_indicator,
    draw_cartoon_card,
    draw_speech_bubble,
    safe_render,  # render "sécurisé" (accents + caractères manquants)
)


# BOUTON (interactif)
@dataclass
class SimpsonButton:
    """
    Bouton interactif "haut niveau" (style Simpson).

    Le bouton stocke son état (hovered / pressed / enabled) et sait :
    - détecter un clic gauche dessus (handle_event)
    - se dessiner avec le thème (draw)

    Remarque :
    - L'action est une fonction (callback) fournie par la scène (ex: lancer la partie, aller au classement).
    """

    rect: pygame.Rect
    text: str
    action: Callable[[], None]
    color: Tuple[int, int, int] = COLORS["simpson_yellow"]
    enabled: bool = True
    hovered: bool = False
    pressed: bool = False


    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> bool:
        """
        Met à jour l'état du bouton et déclenche l'action si besoin.

        Paramètres
        - event : event Pygame reçu (clic, relâchement, etc.)
        - mouse_pos : position actuelle de la souris (x, y)

        Retour
        - True uniquement quand on vient de "valider" un clic sur le bouton
          (clic gauche pressé puis relâché sur le bouton).
        """
        if not self.enabled:
            self.hovered = False
            return False

        # Hover = la souris est dans le rectangle du bouton
        self.hovered = self.rect.collidepoint(mouse_pos)

        # On marque "pressed" uniquement si on appuie sur le bouton
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.pressed = True

        # On valide le clic au relâchement, si la souris est toujours dessus
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.hovered:
                self.pressed = False
                if self.action:
                    self.action()
                return True
            self.pressed = False

        return False


    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """
        Dessine le bouton avec le style Simpson.

        La fonction draw_simpson_button gère le rendu (contours, ombre, état hover/pressed, disabled).
        """
        draw_simpson_button(
            surface=surface,
            rect=self.rect,
            text=self.text,
            font=font,
            bg_color=self.color,
            is_hovered=self.hovered,
            is_pressed=self.pressed,
            enabled=self.enabled,
        )


def make_button(
    rect: pygame.Rect,
    text: str,
    action: Callable[[], None],
    color: Tuple[int, int, int] = COLORS["simpson_yellow"],
    enabled: bool = True,
) -> SimpsonButton:
    """
    Helper pour créer un SimpsonButton plus rapidement (évite de répéter les mêmes paramètres).

    La scène peut ensuite appeler :
    - button.handle_event(event, mouse_pos)
    - button.draw(screen, font)
    """
    return SimpsonButton(
        rect=rect,
        text=text,
        action=action,
        color=color,
        enabled=enabled,
    )


# GRILLE D'ALPHABET (affichage + hover)
class AlphabetGrid:
    """
    Grille d'alphabet style Simpson.

    Rôle
    - Afficher les lettres sous forme de cases, en respectant un layout (ALPHABET_LAYOUT).
    - Gérer un survol (hover) pour donner un feedback visuel.
    - Stocker l'état de chaque lettre : "available", "correct", "wrong".

    Note :
    - Ici, la grille n'est pas cliquable : elle sert d'indicateur visuel (choix assumé dans le projet).
      La scène peut décider de la rendre cliquable plus tard si besoin.
    """

    def __init__(
        self,
        pos: Tuple[int, int],
        letter_size: int = LETTER_BOX_SIZE,
        spacing: int = LETTER_SPACING,
    ):
        """
        Paramètres
        - pos : position (x, y) du coin supérieur gauche de la grille
        - letter_size : taille d'une case
        - spacing : espace entre les cases
        """
        self.pos = pos
        self.letter_size = letter_size
        self.spacing = spacing

        # État de chaque lettre (par défaut : disponible)
        self.letter_states: Dict[str, str] = {
            letter: "available" for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        }

        # Rects des lettres (utile pour le hover et éventuellement des clics plus tard)
        self.letter_rects: Dict[str, pygame.Rect] = {}
        self._build_letter_rects()

        self.hovered_letter: Optional[str] = None

    def _build_letter_rects(self) -> None:
        """
        Construit les rectangles de chaque lettre selon ALPHABET_LAYOUT.

        Le layout est une liste de rangées (type clavier). On centre chaque rangée
        par rapport à la rangée la plus large.
        """
        x_start, y_start = self.pos

        for row_idx, row in enumerate(ALPHABET_LAYOUT):
            # Largeur réelle de la rangée (nombre de lettres * taille + espaces)
            row_width = len(row) * (self.letter_size + self.spacing) - self.spacing

            # Largeur max (rangée la plus large du layout)
            total_width = 10 * (self.letter_size + self.spacing) - self.spacing  # ex: "AZERTYUIOP"

            # Décalage pour centrer la rangée
            row_x = x_start + (total_width - row_width) // 2

            for col_idx, letter in enumerate(row):
                x = row_x + col_idx * (self.letter_size + self.spacing)
                y = y_start + row_idx * (self.letter_size + self.spacing)
                self.letter_rects[letter] = pygame.Rect(x, y, self.letter_size, self.letter_size)

    def set_letter_state(self, letter: str, state: str) -> None:
        """
        Change l'état d'une lettre.

        Exemple :
        - set_letter_state("A", "wrong")
        - set_letter_state("E", "correct")
        """
        letter = letter.upper()
        if letter in self.letter_states:
            self.letter_states[letter] = state

    def reset(self) -> None:
        """Remet toutes les lettres à l'état "available"."""
        for letter in self.letter_states:
            self.letter_states[letter] = "available"

    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """
        Met à jour la lettre survolée (feedback visuel).

        Retour
        - None : la grille ne renvoie rien ici (pas de clic géré).
        """
        self.hovered_letter = None
        for letter, rect in self.letter_rects.items():
            if rect.collidepoint(mouse_pos):
                # On ne surligne que les lettres encore disponibles
                if self.letter_states[letter] == "available":
                    self.hovered_letter = letter
                break

        return None

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Dessine toutes les lettres avec leur état et le hover."""
        for letter, rect in self.letter_rects.items():
            state = self.letter_states[letter]
            is_hovered = (letter == self.hovered_letter)

            draw_alphabet_letter(
                surface=surface,
                letter=letter,
                pos=(rect.x, rect.y),
                size=self.letter_size,
                font=font,
                state=state,
                is_hovered=is_hovered,
            )


# CHAMP DE SAISIE (pseudo, ajout de mot, etc.)
@dataclass
class TextInput:
    """
    Champ de saisie de texte, avec un style cohérent Simpson.

    Points gérés
    - Focus au clic (on active / désactive la saisie)
    - Saisie clavier (backspace / enter / caractères)
    - Curseur clignotant
    - Message de validation (affiché sous le champ)
    - Option letters_only : pratique quand on veut interdire chiffres/symboles
    """

    rect: pygame.Rect
    placeholder: str
    max_len: int
    text: str = ""
    focused: bool = False
    cursor_visible: bool = True
    cursor_timer: float = 0.0
    validation_message: str = ""
    letters_only: bool = False


    def handle_event(self, event: pygame.event.Event) -> Dict[str, bool]:
        """
        Gère la souris (focus) et le clavier (édition du texte).

        Retour
        - {"changed": True} quand le contenu a réellement changé
        - {"submitted": True} quand on appuie sur Entrée
        """
        result = {"changed": False, "submitted": False}

        # Focus au clic gauche
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.focused = self.rect.collidepoint(event.pos)

            # Si on récupère le focus, on relance le curseur visible directement
            if self.focused:
                self.cursor_visible = True
                self.cursor_timer = 0.0

        if not self.focused:
            return result

        # Gestion clavier
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.text:
                    self.text = self.text[:-1]
                    result["changed"] = True
                    self.validation_message = ""

            elif event.key == pygame.K_RETURN:
                result["submitted"] = True

            else:
                ch = event.unicode
                if ch and ch.isprintable():
                    # Règles simples de validation
                    if ch.isdigit():
                        self.validation_message = "Chiffres non autorises"
                    elif self.letters_only and not ch.isalpha():
                        self.validation_message = "Lettres uniquement"
                    elif len(self.text) >= self.max_len:
                        self.validation_message = f"{self.max_len} caracteres max"
                    else:
                        # Normaliser les accents (la police Simpson ne les affiche pas toujours)
                        import unicodedata

                        ch_normalized = unicodedata.normalize("NFD", ch)
                        ch_normalized = "".join(
                            c for c in ch_normalized if unicodedata.category(c) != "Mn"
                        )

                        self.text += ch_normalized
                        result["changed"] = True
                        self.validation_message = ""

        return result


    def update(self, dt: float) -> None:
        """
        Met à jour le curseur (clignotement).

        dt = delta time en secondes (fourni par la boucle principale).
        """
        if self.focused:
            self.cursor_timer += dt
            if self.cursor_timer >= 0.5:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0.0

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """
        Dessine le champ, son texte (ou placeholder), le curseur et un message d'erreur éventuel.
        """
        from ui.simpson_theme import draw_cartoon_rect

        # Fond + bordure (bordure bleue si focus)
        bg_color = COLORS["text_white"]
        border_color = COLORS["simpson_blue"] if self.focused else COLORS["border_black"]

        draw_cartoon_rect(
            surface,
            self.rect,
            fill_color=bg_color,
            border_color=border_color,
            border_width=4 if self.focused else 3,
            shadow=self.focused,
        )

        # Texte à afficher (placeholder si vide)
        if self.text:
            display_text = self.text
            text_color = COLORS["text_black"]
        else:
            display_text = self.placeholder
            text_color = (150, 150, 150)

        # Normalisation avant affichage (accents)
        from ui.simpson_theme import normalize_text_for_simpson
        display_text = normalize_text_for_simpson(display_text)

        text_surface = safe_render(font, display_text, True, text_color)
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 20, self.rect.centery))
        surface.blit(text_surface, text_rect)

        # Curseur : petit rectangle noir (plus propre que le caractère "|")
        if self.focused and self.cursor_visible:
            if self.text:
                cursor_x = text_rect.right + 3
            else:
                cursor_x = self.rect.x + 20

            cursor_height = 30
            cursor_y = self.rect.centery - cursor_height // 2
            cursor_rect = pygame.Rect(cursor_x, cursor_y, 3, cursor_height)
            pygame.draw.rect(surface, COLORS["text_black"], cursor_rect)

        # Message de validation (ex: lettres uniquement, max len...)
        if self.validation_message:
            small_font = pygame.font.Font(None, 28)
            msg_surface = safe_render(
                small_font,
                self.validation_message,
                True,
                COLORS["red_error"],
            )
            msg_pos = (self.rect.x + 10, self.rect.bottom + 8)
            surface.blit(msg_surface, msg_pos)


def make_text_input(
    rect: pygame.Rect,
    placeholder: str = "",
    max_len: int = 20,
    letters_only: bool = False,
) -> TextInput:
    """
    Helper pour créer un TextInput.

    La scène garde l'instance et appelle :
    - input.handle_event(event)
    - input.update(dt)
    - input.draw(screen, font)
    """
    return TextInput(
        rect=rect,
        placeholder=placeholder,
        max_len=max_len,
        letters_only=letters_only,
    )


# TOASTS (petites notifications temporaires)
class ToastManager:
    """
    Gestionnaire de "toasts" = messages temporaires affichés par-dessus le jeu.

    Fonctionnement
    - show(message, duration) ajoute un toast avec un temps restant
    - update(dt) décrémente le temps
    - draw() affiche les derniers toasts (ici on limite volontairement à 3)
    """

    def __init__(self):
        self.toasts: List[Dict] = []

    def show(self, message: str, duration: float = 2.0) -> None:
        """Ajoute un nouveau toast (message + durée)."""
        self.toasts.append({
            "message": message,
            "remaining": duration,
        })

    def update(self, dt: float) -> None:
        """Met à jour le temps restant et supprime ceux qui ont expiré."""
        for toast in self.toasts:
            toast["remaining"] -= dt

        self.toasts = [t for t in self.toasts if t["remaining"] > 0]

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """
        Dessine les toasts actifs.

        Choix d'UI :
        - position en bas de l'écran
        - affichage sous forme de bulle de dialogue
        - uniquement les 3 derniers pour éviter de surcharger
        """
        if not self.toasts:
            return

        screen_width = surface.get_width()
        screen_height = surface.get_height()

        y_offset = screen_height - 150

        for toast in self.toasts[-3:]:
            message = toast["message"]

            bubble_pos = (screen_width // 2 - 250, y_offset)
            draw_speech_bubble(
                surface=surface,
                text=message,
                pos=bubble_pos,
                font=font,
                max_width=500,
                tail_direction="bottom",
                bg_color=COLORS["simpson_yellow"],
            )

            y_offset -= 80


def show_toast(toast_manager: ToastManager, message: str, duration: float = 2.0) -> None:
    """
    Helper simple pour afficher un toast (évite d'appeler toast_manager.show partout).
    """
    toast_manager.show(message, duration)


# INDICATEURS : VIES (coeurs) ET INDICES
class LifeIndicator:
    """
    Indicateur de vies sous forme de coeurs.

    La scène met à jour le nombre de vies restantes avec set_lives(),
    puis appelle draw() à chaque frame.
    """

    def __init__(
        self,
        pos: Tuple[int, int],
        max_lives: int,
        heart_full_img: pygame.Surface,
        heart_empty_img: pygame.Surface,
    ):
        self.pos = pos
        self.max_lives = max_lives
        self.current_lives = max_lives
        self.heart_full_img = heart_full_img
        self.heart_empty_img = heart_empty_img


    def set_lives(self, lives: int) -> None:
        """Clamp entre 0 et max_lives pour éviter les valeurs incohérentes."""
        self.current_lives = max(0, min(lives, self.max_lives))


    def draw(self, surface: pygame.Surface) -> None:
        """Dessine les coeurs (pleins / vides) selon current_lives."""
        draw_heart_indicator(
            surface=surface,
            pos=self.pos,
            total=self.max_lives,
            remaining=self.current_lives,
            heart_full_img=self.heart_full_img,
            heart_empty_img=self.heart_empty_img,
            spacing=10,
        )


class HintIndicator:
    """
    Indicateur d'indices (icônes disponible / utilisé).

    Même logique que LifeIndicator, mais avec des images d'indices.
    """

    def __init__(
        self,
        pos: Tuple[int, int],
        max_hints: int,
        hint_available_img: pygame.Surface,
        hint_used_img: pygame.Surface,
    ):
        self.pos = pos
        self.max_hints = max_hints
        self.current_hints = max_hints
        self.hint_available_img = hint_available_img
        self.hint_used_img = hint_used_img


    def set_hints(self, hints: int) -> None:
        """Clamp entre 0 et max_hints."""
        self.current_hints = max(0, min(hints, self.max_hints))


    def draw(self, surface: pygame.Surface) -> None:
        """Dessine les icônes d'indices."""
        draw_hint_indicator(
            surface=surface,
            pos=self.pos,
            total=self.max_hints,
            remaining=self.current_hints,
            hint_available_img=self.hint_available_img,
            hint_used_img=self.hint_used_img,
            spacing=10,
        )


# AFFICHAGE DU MOT (cases + lettres)
class WordDisplay:
    """
    Affichage du mot masqué (ex: "_ A _ _ E") sous forme de petites cases.

    Idée
    - Chaque caractère est représenté par une case carrée.
    - Si la lettre est inconnue : on dessine un "underscore" (ligne).
    - Si la lettre est trouvée : on affiche la lettre centrée (en noir pour la lisibilité).
    """


    def __init__(self, pos: Tuple[int, int], letter_spacing: int = 25):
        """
        Paramètres
        - pos : position centrale (x, y) de la ligne de cases
        - letter_spacing : conservé ici, même si on utilise surtout box_spacing dans draw()
        """
        self.pos = pos
        self.letter_spacing = letter_spacing
        self.masked_word = ""


    def set_word(self, masked_word: str) -> None:
        """Met à jour le mot à afficher (déjà "masqué", donc avec des _ et des espaces)."""
        self.masked_word = masked_word


    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """
        Dessine le mot en cases.

        Détail important :
        - On calcule la largeur totale pour centrer l'ensemble.
        - On utilise une petite taille de police dans les cases pour éviter que ça déborde.
        """
        from ui.simpson_theme import draw_text_with_shadow

        letters = self.masked_word.split()
        if not letters:
            return

        box_size = 38
        box_spacing = 6

        total_width = len(letters) * box_size + (len(letters) - 1) * box_spacing

        x_start = self.pos[0] - total_width // 2
        y_pos = self.pos[1]

        for i, letter in enumerate(letters):
            x = x_start + i * (box_size + box_spacing)

            box_rect = pygame.Rect(x, y_pos, box_size, box_size)

            # Fond + bordure : même esprit que les cards (jaune pâle)
            pygame.draw.rect(surface, COLORS["bg_card"], box_rect, border_radius=5)
            pygame.draw.rect(surface, COLORS["border_black"], box_rect, 2, border_radius=5)

            if letter == "_":
                # Ligne noire (underscore) visible
                line_y = y_pos + box_size - 10
                line_x1 = x + 8
                line_x2 = x + box_size - 8
                pygame.draw.line(
                    surface,
                    COLORS["text_black"],
                    (line_x1, line_y),
                    (line_x2, line_y),
                    3,
                )
            else:
                # Lettre trouvée : texte noir, centré
                small_font = pygame.font.Font(
                    font.get_name() if hasattr(font, "get_name") else None,
                    28,
                )
                try:
                    from ui.simpson_theme import safe_render
                    text_surface = safe_render(small_font, letter.upper(), True, COLORS["text_black"])
                except:
                    text_surface = small_font.render(letter.upper(), True, COLORS["text_black"])

                text_rect = text_surface.get_rect(center=(x + box_size // 2, y_pos + box_size // 2))
                surface.blit(text_surface, text_rect)
