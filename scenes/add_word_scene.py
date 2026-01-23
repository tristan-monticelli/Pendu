"""Scene d'ajout de mot"""

import pygame
from scene_manager import Scene
from ui.draw_helpers import draw_text_centered, draw_button, draw_chat_frame, show_toast, draw_toast
from ui.layout import POSITIONS, SIZES
from core.words_io import add_word, validate_word, load_words

#--------------------------------------AddWordScene--------------------------------------#

class AddWordScene(Scene):
    """Ecran pour ajouter un nouveau mot"""

    def __init__(self, manager):
        super().__init__(manager)
        self.word_input = ""
        self.recent_words = []
        self.message = ""
        self.message_color = (255, 255, 255)
        self.cursor_visible = True
        self.cursor_timer = 0

    def enter(self):
        """Initialise l'ecran"""
        self.word_input = ""
        self.message = ""

        # Charger les derniers mots
        words = load_words()
        self.recent_words = words[-8:] if len(words) > 8 else words
        self.recent_words.reverse()

    def handle_events(self, events):
        """Gere les evenements"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Bouton Ajouter
                if self._is_click_on_button(event.pos, POSITIONS["button1"], SIZES["compact_button"]):
                    self._try_add_word()
                # Bouton Retour
                elif self._is_click_on_button(event.pos, POSITIONS["button4"], SIZES["compact_button"]):
                    self.manager.go_to("menu")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._try_add_word()
                elif event.key == pygame.K_BACKSPACE:
                    self.word_input = self.word_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.manager.go_to("menu")
                elif len(self.word_input) < 30:
                    char = event.unicode.upper()
                    if char and char.isalpha():
                        self.word_input += char

    def _is_click_on_button(self, click_pos, button_pos, button_size):
        """Verifie si le clic est sur un bouton"""
        rect = pygame.Rect(button_pos, button_size)
        return rect.collidepoint(click_pos)

    def _try_add_word(self):
        """Tente d'ajouter le mot"""
        word = self.word_input.strip()

        if not word:
            self.message = "Entrez un mot"
            self.message_color = (255, 100, 100)
            return

        # Validation
        valid, error = validate_word(word)
        if not valid:
            self.message = error
            self.message_color = (255, 100, 100)
            show_toast(error, 1.5)
            return

        # Ajout
        success, msg = add_word(word)

        if success:
            self.message = f"'{word}' ajoute!"
            self.message_color = (100, 255, 100)
            show_toast(f"Mot ajoute: {word}", 2.0)

            # Mettre a jour la liste
            self.recent_words.insert(0, word.upper())
            if len(self.recent_words) > 8:
                self.recent_words.pop()

            # Vider l'input
            self.word_input = ""
        else:
            self.message = msg
            self.message_color = (255, 100, 100)
            show_toast(msg, 1.5)

    def update(self):
        """Met a jour le curseur"""
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        """Dessine l'ecran"""
        # Titre
        draw_text_centered(screen, "AJOUTER UN MOT", (400, 80), font_size=48, color=(255, 255, 0))

        # Instructions
        draw_text_centered(screen, "Entrez un mot (2-30 lettres)", (400, 140), font_size=24, color=(200, 200, 200))

        # Chat frame avec le mot
        display_text = self.word_input
        if self.cursor_visible:
            display_text += "|"
        draw_chat_frame(screen, display_text)

        # Message
        if self.message:
            draw_text_centered(screen, self.message, (400, 520), font_size=24, color=self.message_color)

        # Boutons
        draw_button(screen, "ajouter", POSITIONS["button1"])
        draw_button(screen, "retour", POSITIONS["button4"])

        # Liste des derniers mots
        from ui.draw_helpers import draw_text
        draw_text(screen, "Derniers mots:", (50, 200), font_size=22, color=(200, 200, 200))

        y = 230
        for i, word in enumerate(self.recent_words[:8]):
            draw_text(screen, f"- {word}", (60, y + i * 25), font_size=18)

        draw_toast(screen)
