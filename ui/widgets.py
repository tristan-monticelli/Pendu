"""Widgets UI - Boutons et champs de saisie"""

import pygame
from ui.layout import COLORS

#--------------------------------------Button--------------------------------------#

class Button:
    """Bouton cliquable"""

    def __init__(self, rect: pygame.Rect, text: str = "", texture=None,
                 font_size: int = 24, color: tuple = None, hover_color: tuple = None):
        """
        Args:
            rect: Rectangle du bouton (x, y, width, height)
            text: Texte affiche (si pas de texture)
            texture: Surface pygame (optionnel)
            font_size: Taille de la police
            color: Couleur de fond
            hover_color: Couleur au survol
        """
        self.rect = pygame.Rect(rect)
        self.text = text
        self.texture = texture
        self.font_size = font_size
        self.color = color or COLORS["button_normal"]
        self.hover_color = hover_color or COLORS["button_hover"]
        self.hovered = False
        self.enabled = True
        self.on_click = None

    def handle_event(self, event) -> bool:
        """
        Gere un evenement

        Returns:
            True si le bouton a ete clique
        """
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True

        return False

    def draw(self, screen):
        """Dessine le bouton"""
        if self.texture:
            screen.blit(self.texture, self.rect.topleft)
        else:
            color = self.hover_color if self.hovered else self.color
            pygame.draw.rect(screen, color, self.rect, border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=5)

            if self.text:
                font = pygame.font.Font(None, self.font_size)
                text_surf = font.render(self.text, True, (255, 255, 255))
                text_rect = text_surf.get_rect(center=self.rect.center)
                screen.blit(text_surf, text_rect)

#--------------------------------------TextInput--------------------------------------#

class TextInput:
    """Champ de saisie de texte"""

    def __init__(self, rect: pygame.Rect, placeholder: str = "",
                 max_length: int = 20, font_size: int = 24):
        """
        Args:
            rect: Rectangle du champ
            placeholder: Texte d'exemple
            max_length: Longueur maximale
            font_size: Taille de la police
        """
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.max_length = max_length
        self.font_size = font_size
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event) -> bool:
        """
        Gere un evenement

        Returns:
            True si Enter est presse
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length:
                # Accepter lettres, chiffres et quelques caracteres
                if event.unicode.isprintable():
                    self.text += event.unicode

        return False

    def update(self):
        """Met a jour le curseur clignotant"""
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        """Dessine le champ de saisie"""
        # Fond
        bg_color = COLORS["input_bg"]
        border_color = (50, 150, 255) if self.active else COLORS["input_border"]

        pygame.draw.rect(screen, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)

        # Texte
        font = pygame.font.Font(None, self.font_size)

        if self.text:
            text_surf = font.render(self.text, True, COLORS["text_black"])
        else:
            text_surf = font.render(self.placeholder, True, (150, 150, 150))

        text_rect = text_surf.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        screen.blit(text_surf, text_rect)

        # Curseur
        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 2
            cursor_y1 = self.rect.centery - 10
            cursor_y2 = self.rect.centery + 10
            pygame.draw.line(screen, COLORS["text_black"], (cursor_x, cursor_y1),
                            (cursor_x, cursor_y2), 2)

    def clear(self):
        """Vide le champ"""
        self.text = ""

    def get_value(self) -> str:
        """Retourne le texte saisi"""
        return self.text.strip()

#--------------------------------------VirtualKeyboard--------------------------------------#

class VirtualKeyboard:
    """Clavier virtuel pour saisir des lettres"""

    LAYOUT = [
        "AZERTYUIOP",
        "QSDFGHJKLM",
        "WXCVBN"
    ]

    def __init__(self, start_pos: tuple, key_size: int = 40, spacing: int = 5):
        """
        Args:
            start_pos: Position (x, y) du coin superieur gauche
            key_size: Taille d'une touche
            spacing: Espacement entre touches
        """
        self.start_pos = start_pos
        self.key_size = key_size
        self.spacing = spacing
        self.disabled_keys = set()
        self.keys = self._create_keys()

    def _create_keys(self) -> dict:
        """Cree les rectangles des touches"""
        keys = {}
        x, y = self.start_pos

        for row_idx, row in enumerate(self.LAYOUT):
            # Centrage des rangees
            row_width = len(row) * (self.key_size + self.spacing) - self.spacing
            row_x = x + (10 * (self.key_size + self.spacing) - row_width) // 2

            for col_idx, letter in enumerate(row):
                key_x = row_x + col_idx * (self.key_size + self.spacing)
                key_y = y + row_idx * (self.key_size + self.spacing)
                keys[letter] = pygame.Rect(key_x, key_y, self.key_size, self.key_size)

            y += self.key_size + self.spacing

        return keys

    def disable_key(self, letter: str):
        """Desactive une touche"""
        self.disabled_keys.add(letter.upper())

    def reset(self):
        """Reactive toutes les touches"""
        self.disabled_keys.clear()

    def handle_event(self, event) -> str:
        """
        Gere un clic

        Returns:
            Lettre cliquee ou ""
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for letter, rect in self.keys.items():
                if rect.collidepoint(event.pos) and letter not in self.disabled_keys:
                    return letter
        return ""

    def draw(self, screen):
        """Dessine le clavier"""
        font = pygame.font.Font(None, 28)

        for letter, rect in self.keys.items():
            disabled = letter in self.disabled_keys

            # Couleur
            if disabled:
                bg_color = (80, 80, 80)
                text_color = (120, 120, 120)
            else:
                bg_color = (100, 100, 180)
                text_color = (255, 255, 255)

            # Fond
            pygame.draw.rect(screen, bg_color, rect, border_radius=5)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1, border_radius=5)

            # Lettre
            text_surf = font.render(letter, True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)
