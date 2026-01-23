"""Scene du menu principal"""

import pygame
from scene_manager import Scene
from ui.draw_helpers import (
    VisualState, draw_text_centered, draw_button, draw_chat_frame,
    get_textures, show_toast, draw_toast, load_font
)
from ui.layout import POSITIONS, SIZES
from settings import PSEUDO_MAX_LENGTH, PSEUDO_FORBIDDEN_CHARS

#--------------------------------------MenuScene--------------------------------------#

class MenuScene(Scene):
    """Ecran du menu principal"""

    # Etats du menu
    STATE_MAIN = "main"           # Boutons Normal/Difficile/Leader
    STATE_PLAYERS = "players"     # Boutons 1J/2J/3J
    STATE_PSEUDO = "pseudo"       # Saisie du pseudo

    def __init__(self, manager):
        super().__init__(manager)
        self.state = self.STATE_MAIN
        self.difficulty = "normal"
        self.num_players = 1
        self.current_player_input = 0
        self.player_names = ["", "", ""]
        self.pseudo_input = ""
        self.cursor_visible = True
        self.cursor_timer = 0

    def enter(self):
        """Initialise le menu"""
        self.state = self.STATE_MAIN
        self.difficulty = "normal"
        self.pseudo_input = ""
        self.player_names = ["", "", ""]
        self.current_player_input = 0

    def handle_events(self, events):
        """Gere les evenements"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

            if event.type == pygame.KEYDOWN:
                self._handle_key(event)

    def _handle_click(self, pos):
        """Gere les clics souris"""
        if self.state == self.STATE_MAIN:
            # Boutons principaux (large_button)
            if self._is_click_on_button(pos, POSITIONS["button1"], SIZES["large_button"]):
                self.difficulty = "normal"
                self.state = self.STATE_PLAYERS
            elif self._is_click_on_button(pos, POSITIONS["button2"], SIZES["large_button"]):
                self.difficulty = "difficile"
                self.state = self.STATE_PLAYERS
            elif self._is_click_on_button(pos, POSITIONS["button3"], SIZES["large_button"]):
                self.manager.go_to("leaderboard")
            elif self._is_click_on_button(pos, POSITIONS["button4"], SIZES["compact_button"]):
                pygame.quit()
                exit()

        elif self.state == self.STATE_PLAYERS:
            # Boutons joueurs (meme taille que menu principal)
            if self._is_click_on_button(pos, POSITIONS["button1"], SIZES["large_button"]):
                self.num_players = 1
                self.state = self.STATE_PSEUDO
                self.current_player_input = 0
            elif self._is_click_on_button(pos, POSITIONS["button2"], SIZES["large_button"]):
                self.num_players = 2
                self.state = self.STATE_PSEUDO
                self.current_player_input = 0
            elif self._is_click_on_button(pos, POSITIONS["button3"], SIZES["large_button"]):
                self.num_players = 3
                self.state = self.STATE_PSEUDO
                self.current_player_input = 0
            elif self._is_click_on_button(pos, POSITIONS["button4"], SIZES["compact_button"]):
                self.state = self.STATE_MAIN

        elif self.state == self.STATE_PSEUDO:
            if self._is_click_on_button(pos, POSITIONS["button4"], SIZES["compact_button"]):
                self.state = self.STATE_PLAYERS

    def _handle_key(self, event):
        """Gere les touches clavier"""
        if self.state == self.STATE_PSEUDO:
            if event.key == pygame.K_RETURN:
                self._validate_pseudo()
            elif event.key == pygame.K_BACKSPACE:
                self.pseudo_input = self.pseudo_input[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.state = self.STATE_PLAYERS
            elif len(self.pseudo_input) < PSEUDO_MAX_LENGTH:
                char = event.unicode
                if char and char.isprintable() and char not in PSEUDO_FORBIDDEN_CHARS:
                    self.pseudo_input += char
        elif self.state == self.STATE_PLAYERS:
            if event.key == pygame.K_ESCAPE:
                self.state = self.STATE_MAIN
            elif event.key == pygame.K_1:
                self.num_players = 1
                self.state = self.STATE_PSEUDO
                self.current_player_input = 0
            elif event.key == pygame.K_2:
                self.num_players = 2
                self.state = self.STATE_PSEUDO
                self.current_player_input = 0
            elif event.key == pygame.K_3:
                self.num_players = 3
                self.state = self.STATE_PSEUDO
                self.current_player_input = 0

    def _validate_pseudo(self):
        """Valide le pseudo et passe au joueur suivant ou lance le jeu"""
        pseudo = self.pseudo_input.strip()
        if not pseudo:
            show_toast("Entrez un pseudo!", 1.5)
            return

        self.player_names[self.current_player_input] = pseudo
        self.current_player_input += 1

        if self.current_player_input < self.num_players:
            self.pseudo_input = ""
            show_toast(f"Joueur {self.current_player_input + 1}", 1.0)
        else:
            self._start_game()

    def _start_game(self):
        """Demarre une partie"""
        self.manager.shared_data["player_names"] = self.player_names[:self.num_players]
        self.manager.shared_data["num_players"] = self.num_players
        self.manager.shared_data["current_player_index"] = 0
        self.manager.shared_data["difficulty"] = self.difficulty
        self.manager.shared_data["scores"] = [0] * self.num_players
        self.manager.go_to("game")

    def _is_click_on_button(self, click_pos, button_pos, button_size):
        """Verifie si le clic est sur un bouton"""
        rect = pygame.Rect(button_pos, button_size)
        return rect.collidepoint(click_pos)

    def update(self):
        """Met a jour le curseur"""
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        """Dessine le menu"""
        if self.state == self.STATE_MAIN:
            self._draw_main_menu(screen)
        elif self.state == self.STATE_PLAYERS:
            self._draw_players_menu(screen)
        elif self.state == self.STATE_PSEUDO:
            self._draw_pseudo_input(screen)

        draw_toast(screen)

    def _draw_main_menu(self, screen):
        """Dessine le menu principal"""
        draw_text_centered(screen, "LE PENDU", (400, 100), font_size=72, color=(255, 255, 0))

        draw_button(screen, "normal", POSITIONS["button1"])
        draw_button(screen, "difficile", POSITIONS["button2"])
        draw_button(screen, "leader", POSITIONS["button3"])
        draw_button(screen, "quitter", POSITIONS["button4"])

    def _draw_players_menu(self, screen):
        """Dessine le menu de selection des joueurs"""
        mode_text = "MODE NORMAL" if self.difficulty == "normal" else "MODE DIFFICILE"
        color = (255, 255, 0) if self.difficulty == "normal" else (200, 200, 200)
        draw_text_centered(screen, mode_text, (400, 80), font_size=48, color=color)

        draw_text_centered(screen, "Nombre de joueurs", (400, 150), font_size=32)
        draw_text_centered(screen, "(ou appuyez 1, 2, 3)", (400, 180), font_size=20, color=(180, 180, 180))

        draw_button(screen, "1joueur", POSITIONS["button1"])
        draw_button(screen, "2joueurs", POSITIONS["button2"])
        draw_button(screen, "3joueurs", POSITIONS["button3"])
        draw_button(screen, "retour", POSITIONS["button4"])

    def _draw_pseudo_input(self, screen):
        """Dessine l'ecran de saisie du pseudo"""
        player_num = self.current_player_input + 1
        draw_text_centered(screen, f"JOUEUR {player_num}", (400, 100), font_size=52, color=(255, 255, 0))

        draw_text_centered(screen, "Entrez votre pseudo", (400, 160), font_size=28)

        # Afficher le pseudo dans le chat frame
        display_text = self.pseudo_input
        if self.cursor_visible:
            display_text += "|"
        draw_chat_frame(screen, display_text)

        draw_button(screen, "retour", POSITIONS["button4"])

        draw_text_centered(screen, "Appuyez Entree pour valider", (400, 560), font_size=18, color=(180, 180, 180))
