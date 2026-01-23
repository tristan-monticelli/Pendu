"""Scene de fin de partie"""

import pygame
from scene_manager import Scene
from ui.draw_helpers import (
    VisualState, draw_character, draw_text_centered, draw_button,
    show_toast, draw_toast, get_textures
)
from ui.layout import POSITIONS, SIZES
from core.leaderboard_io import update_player_after_game
from core.scoring import format_time
from settings import MAX_ERRORS_NORMAL, MAX_ERRORS_HARD

#--------------------------------------GameOverScene--------------------------------------#

class GameOverScene(Scene):
    """Ecran de fin de partie"""

    def __init__(self, manager):
        super().__init__(manager)

    def enter(self):
        """Initialise l'ecran"""
        # Recuperer les donnees
        self.won = self.manager.shared_data.get("last_won", False)
        self.word = self.manager.shared_data.get("last_word", "")
        self.elapsed = self.manager.shared_data.get("last_time", 0)
        self.scores = self.manager.shared_data.get("scores", [0])
        self.names = self.manager.shared_data.get("player_names", ["Joueur"])
        self.num_players = self.manager.shared_data.get("num_players", 1)
        self.difficulty = self.manager.shared_data.get("difficulty", "normal")

        # Configurer VisualState pour afficher Trump completement
        VisualState.difficulty = self.difficulty
        VisualState.max_errors = MAX_ERRORS_NORMAL if self.difficulty == "normal" else MAX_ERRORS_HARD

        if self.won:
            VisualState.current_mood = 0  # Happy
            VisualState.errors = 0
        else:
            VisualState.current_mood = 3  # Dead
            VisualState.errors = VisualState.max_errors  # Afficher tout le corps

        # Sauvegarder les scores dans le leaderboard
        for i in range(self.num_players):
            if i < len(self.names) and self.names[i]:
                score = self.scores[i] if i < len(self.scores) else 0
                update_player_after_game(self.names[i], score, int(self.elapsed))

    def handle_events(self, events):
        """Gere les evenements"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Bouton Menu
                if self._is_click_on_button(event.pos, POSITIONS["button1"], SIZES["compact_button"]):
                    self.manager.go_to("menu")
                # Bouton Rejouer
                elif self._is_click_on_button(event.pos, POSITIONS["button2"], SIZES["compact_button"]):
                    self._replay()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.manager.go_to("menu")
                elif event.key == pygame.K_RETURN:
                    self._replay()

    def _is_click_on_button(self, click_pos, button_pos, button_size):
        """Verifie si le clic est sur un bouton"""
        rect = pygame.Rect(button_pos, button_size)
        return rect.collidepoint(click_pos)

    def _replay(self):
        """Rejouer avec les memes joueurs"""
        self.manager.shared_data["current_player_index"] = 0
        self.manager.shared_data["scores"] = [0] * self.num_players
        self.manager.go_to("game")

    def update(self):
        pass

    def draw(self, screen):
        """Dessine l'ecran de fin"""
        # Pendu et personnage (show_all=True pour afficher Trump completement)
        draw_character(screen, show_all=True)

        # Titre
        title = "VICTOIRE!" if self.won else "PERDU!"
        color = (50, 255, 50) if self.won else (255, 50, 50)
        draw_text_centered(screen, title, (400, 50), font_size=56, color=color)

        # Mot
        draw_text_centered(screen, f"Le mot: {self.word}", (400, 110),
                          font_size=32, color=(255, 255, 255))

        # Temps
        time_str = format_time(int(self.elapsed))
        draw_text_centered(screen, f"Temps: {time_str}", (400, 150),
                          font_size=24, color=(200, 200, 200))

        # Scores
        y = 200
        if self.num_players > 1:
            draw_text_centered(screen, "SCORES", (150, y), font_size=32, color=(255, 255, 0))
            y += 40

            for i in range(self.num_players):
                name = self.names[i] if i < len(self.names) else f"Joueur {i + 1}"
                score = self.scores[i] if i < len(self.scores) else 0
                text = f"{name}: {score}"
                draw_text_centered(screen, text, (150, y), font_size=24)
                y += 35

            # Gagnant
            if self.scores:
                best_idx = self.scores.index(max(self.scores))
                best_name = self.names[best_idx] if best_idx < len(self.names) else f"Joueur {best_idx + 1}"
                draw_text_centered(screen, f"Gagnant: {best_name}!", (150, y + 20),
                                  font_size=28, color=(255, 215, 0))
        else:
            score = self.scores[0] if self.scores else 0
            draw_text_centered(screen, f"Score: {score}", (150, y), font_size=36, color=(255, 255, 0))

        # Boutons
        draw_button(screen, "menu", POSITIONS["button1"])
        draw_button(screen, "rejouer", POSITIONS["button2"])

        draw_toast(screen)
