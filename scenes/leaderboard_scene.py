"""Scene du classement"""

import pygame
from scene_manager import Scene
from ui.draw_helpers import (
    draw_text_centered, draw_text, draw_button, draw_toast, get_textures, load_font
)
from ui.layout import POSITIONS, SIZES
from core.leaderboard_io import load_leaderboard, sort_leaderboard
from core.scoring import format_time

#--------------------------------------LeaderboardScene--------------------------------------#

class LeaderboardScene(Scene):
    """Ecran du classement"""

    def __init__(self, manager):
        super().__init__(manager)
        self.leaderboard_data = []
        self.scroll_offset = 0

    def enter(self):
        """Charge le classement"""
        self._load_leaderboard()
        self.scroll_offset = 0

    def _load_leaderboard(self):
        """Charge et formate le classement"""
        players = load_leaderboard()
        sorted_players = sort_leaderboard(players)

        self.leaderboard_data = [
            {
                "rank": i + 1,
                "pseudo": p.pseudo,
                "best_score": p.best_score,
                "best_time": p.best_score_time_seconds,
                "total_time": p.total_play_time_seconds,
                "games": p.games_played
            }
            for i, p in enumerate(sorted_players)
        ]

    def handle_events(self, events):
        """Gere les evenements"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Bouton Retour
                if self._is_click_on_button(event.pos, POSITIONS["button4"], SIZES["compact_button"]):
                    self.manager.go_to("menu")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.manager.go_to("menu")

            # Scroll avec la molette
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y * 35
                max_scroll = max(0, len(self.leaderboard_data) * 35 - 250)
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    def _is_click_on_button(self, click_pos, button_pos, button_size):
        """Verifie si le clic est sur un bouton"""
        rect = pygame.Rect(button_pos, button_size)
        return rect.collidepoint(click_pos)

    def update(self):
        pass

    def draw(self, screen):
        """Dessine le classement"""
        textures = get_textures()

        # Titre en haut
        draw_text_centered(screen, "CLASSEMENT", (400, 40), font_size=52, color=(255, 255, 0))

        # Frame Leader au centre
        frame_width, frame_height = SIZES["leader"]
        frame_x = (800 - frame_width) // 2
        frame_y = 80
        screen.blit(textures["frame"]["leader"], (frame_x, frame_y))

        # Zone interieure du frame (avec marge) - centré
        inner_margin_x = 90  # +20% marge horizontale
        inner_margin_top = 80
        inner_margin_bottom = 50
        inner_x = frame_x + inner_margin_x
        inner_y = frame_y + inner_margin_top
        inner_width = frame_width - 2 * inner_margin_x
        inner_height = frame_height - inner_margin_top - inner_margin_bottom

        # En-tetes du tableau - centré horizontalement
        header_y = inner_y + 20
        col_x = [inner_x + 5, inner_x + 40, inner_x + 130, inner_x + 200, inner_x + 270]

        font_header = load_font(18)
        headers = ["#", "Pseudo", "Score", "Temps", "Parties"]
        header_colors = (255, 230, 150)  # Jaune clair visible

        for i, header in enumerate(headers):
            surf = font_header.render(header, True, header_colors)
            screen.blit(surf, (col_x[i], header_y))

        # Ligne de separation
        pygame.draw.line(screen, header_colors,
                        (inner_x + 5, header_y + 25),
                        (inner_x + inner_width - 10, header_y + 25), 2)

        # Zone scrollable pour les donnees
        data_y = header_y + 40
        data_height = inner_height - 70

        # Clip rect pour le scroll
        clip_rect = pygame.Rect(inner_x, data_y, inner_width, data_height)
        screen.set_clip(clip_rect)

        line_height = 32
        font_data = load_font(20)

        for i, entry in enumerate(self.leaderboard_data):
            line_y = data_y + i * line_height - self.scroll_offset

            if line_y < data_y - line_height or line_y > data_y + data_height:
                continue

            # Couleur selon rang (visible sur fond marron)
            if entry["rank"] == 1:
                color = (255, 215, 0)  # Or
            elif entry["rank"] == 2:
                color = (220, 220, 230)  # Argent
            elif entry["rank"] == 3:
                color = (255, 180, 100)  # Bronze clair
            else:
                color = (255, 255, 200)  # Jaune clair

            # Donnees
            data = [
                str(entry["rank"]),
                entry["pseudo"][:8],
                str(entry["best_score"]),
                format_time(entry["best_time"]),
                str(entry["games"])
            ]

            for j, val in enumerate(data):
                surf = font_data.render(val, True, color)
                screen.blit(surf, (col_x[j], line_y))

        screen.set_clip(None)

        # Message si vide
        if not self.leaderboard_data:
            draw_text_centered(screen, "Aucun score", (400, 280),
                              font_size=28, color=(100, 80, 60))

        # Bouton retour
        draw_button(screen, "retour", POSITIONS["button4"])

        # Instructions scroll
        if len(self.leaderboard_data) > 7:
            draw_text_centered(screen, "Molette pour defiler", (400, 520),
                              font_size=16, color=(150, 150, 150))

        draw_toast(screen)
