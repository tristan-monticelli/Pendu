"""
Scène Classement - Version Simpson
Affiche le tableau des meilleurs scores
"""

from __future__ import annotations

import pygame

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    COLORS,
    BUTTON_SIZES,
    MARGIN_SCREEN,
)

from ui.simpson_theme import (
    draw_simpson_background,
    draw_cartoon_card,
    draw_text_with_shadow,
    draw_outlined_text,
    format_duration,
)

from ui.simpson_components import (
    SimpsonButton,
    make_button,
)

from core.leaderboard_io import sort_leaderboard


class LeaderboardScene:
    """
    Scène du classement
    
    Affiche un tableau avec :
    - Rang
    - Pseudo
    - Meilleur score
    - Temps du record
    - Temps total de jeu
    - Nombre de parties jouées
    """
    
    def __init__(self, manager, shared, runtime_state, payload):
        """
        Initialise la scène
        
        Args:
            manager: SceneManager
            shared: Ressources partagées (fonts, assets)
            runtime_state: État global
            payload: Données (non utilisé)
        """
        self.manager = manager
        self.shared = shared
        self.runtime_state = runtime_state
        self.payload = payload
        
        self.fonts = self.shared["fonts"]
        
        # Données du tableau
        self.headers = ["#", "Pseudo", "Score", "T record", "T total", "Parties"]
        self.rows = []
        
        # Bouton retour
        self.btn_back = None
        
        # Scroll (si beaucoup de joueurs)
        self.scroll_offset = 0
        self.max_visible_rows = 8
    
    def on_enter(self):
        """
        Appelé lors de l'entrée dans la scène
        Charge et trie le classement
        """
        # Récupération du classement
        leaderboard = self.runtime_state.get("leaderboard_cache", {})
        
        # Tri par meilleur score
        profiles = sort_leaderboard(leaderboard)
        
        # Construction des lignes du tableau (TOP 15 max)
        self.rows = []
        for i, p in enumerate(profiles[:15]):  # ✅ Limité au top 15
            self.rows.append([
                str(i + 1),  # Rang
                p.pseudo,  # ✅ Pas besoin de limiter, géré à la saisie
                str(p.best_score),
                format_duration(p.best_score_time_seconds),
                format_duration(p.total_play_time_seconds),
                str(p.games_played),
            ])
        
        # ✅ Bouton retour - Jaune pâle (comme la DA)
        btn_width, btn_height = BUTTON_SIZES["normal"]
        
        def action_back():
            self.manager.go_to("menu")
        
        self.btn_back = make_button(
            rect=pygame.Rect(
                (WINDOW_WIDTH - btn_width) // 2,
                WINDOW_HEIGHT - MARGIN_SCREEN - btn_height - 30,
                btn_width,
                btn_height
            ),
            text="RETOUR",
            action=action_back,
            color=COLORS["btn_yellow_pale"],  # ✅ Jaune pâle
        )
        
        # Reset scroll
        self.scroll_offset = 0
    
    def handle_event(self, event):
        """
        Gestion des événements
        
        Args:
            event: Événement pygame
        """
        # ESC : retour menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.go_to("menu")
            return
        
        # ✅ Scroll avec flèches haut/bas
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.scroll_offset -= 45
            elif event.key == pygame.K_DOWN:
                self.scroll_offset += 45
        
        # ✅ Scroll avec molette
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * 45
        
        # ✅ Limites du scroll
        row_height = 45
        visible_height = 280  # Hauteur visible dans la card
        max_rows_visible = visible_height // row_height
        total_content_height = len(self.rows) * row_height
        max_scroll = max(0, total_content_height - visible_height)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
        
        # Bouton retour
        mouse_pos = pygame.mouse.get_pos()
        self.btn_back.handle_event(event, mouse_pos)
    
    def update(self, dt):
        """
        Mise à jour de la scène
        
        Args:
            dt: Delta time en secondes
        """
        pass
    
    def draw(self, screen):
        """
        Dessin de la scène
        
        Args:
            screen: Surface pygame
        """
        # Fond Simpson
        draw_simpson_background(screen)
        
        # Titre
        title_y = 70
        draw_outlined_text(
            screen,
            "CLASSEMENT",
            (WINDOW_WIDTH // 2, title_y),
            self.fonts["title"],
            color=COLORS["simpson_yellow"],
            outline_color=COLORS["border_black"],
            outline_width=6,
            centered=True,
        )
        
        # ✅ Card tableau centrée verticalement et horizontalement
        table_width = 1200
        table_height = 450
        table_rect = pygame.Rect(
            (WINDOW_WIDTH - table_width) // 2,
            (WINDOW_HEIGHT - table_height) // 2 - 30,  # ✅ Centré verticalement
            table_width,
            table_height
        )
        
        draw_cartoon_card(
            screen,
            table_rect,
            bg_color=COLORS["bg_card"],
        )
        
        # Affichage du tableau
        if not self.rows:
            # Aucun score
            draw_text_with_shadow(
                screen,
                "Aucun score enregistre",
                (table_rect.centerx, table_rect.centery),
                self.fonts["large"],
                color=COLORS["text_black"],
                centered=True,
            )
        else:
            self._draw_table(screen, table_rect)
        
        # Bouton retour
        self.btn_back.draw(screen, self.fonts["body"])
        
        # ✅ Hint en jaune Simpson avec outline
        if len(self.rows) > 6:
            hint_text = "Molette ou fleches pour defiler   |   ESC pour revenir"
        else:
            hint_text = "ESC pour revenir"
        
        draw_outlined_text(
            screen,
            hint_text,
            (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 35),
            self.fonts["body"],
            color=COLORS["simpson_yellow"],
            outline_color=COLORS["border_black"],
            outline_width=3,
            centered=True,
        )
    
    def _draw_table(self, screen, table_rect):
        """
        Dessine le tableau de scores
        
        Args:
            screen: Surface pygame
            table_rect: Rectangle de la card tableau
        """
        # ✅ Configuration colonnes BIEN espacées
        col_widths = [60, 200, 120, 160, 160, 100]
        col_spacing = 50  # ✅ Espacement entre colonnes
        
        # Calcul position de départ pour centrer le contenu
        total_width = sum(col_widths) + col_spacing * (len(col_widths) - 1)
        start_x = table_rect.x + (table_rect.width - total_width) // 2
        
        col_x_positions = []
        current_x = start_x
        for width in col_widths:
            col_x_positions.append(current_x)
            current_x += width + col_spacing
        
        # ✅ Headers en noir - bien espacés de la ligne
        header_y = table_rect.y + 25  # ✅ Position des headers
        
        # Header "#" aligné avec les numéros
        draw_text_with_shadow(
            screen,
            "#",
            (col_x_positions[0] + 10, header_y),
            self.fonts["body"],
            color=COLORS["text_black"],
            shadow_color=(150, 150, 150),
            shadow_offset=(1, 1),
        )
        
        # Autres headers
        for i in range(1, len(self.headers)):
            draw_text_with_shadow(
                screen,
                self.headers[i],
                (col_x_positions[i], header_y),
                self.fonts["body"],
                color=COLORS["text_black"],
                shadow_color=(150, 150, 150),
                shadow_offset=(1, 1),
            )
        
        # Ligne de séparation - bien espacée des headers
        line_y = header_y + 55  # ✅ Plus d'espace (était 45)
        pygame.draw.line(
            screen,
            COLORS["border_black"],
            (table_rect.x + 40, line_y),
            (table_rect.right - 40, line_y),
            3
        )
        
        # Zone scrollable pour les données
        data_start_y = line_y + 20
        row_height = 45
        
        # Clip rect pour limiter l'affichage
        clip_rect = pygame.Rect(
            table_rect.x,
            data_start_y,
            table_rect.width,
            table_rect.height - (data_start_y - table_rect.y) - 20
        )
        screen.set_clip(clip_rect)
        
        # ✅ Couleurs LISIBLES pour le podium (plus foncées)
        PODIUM_COLORS = {
            0: (180, 140, 0),    # 🥇 Or foncé (lisible sur jaune)
            1: (100, 100, 110),  # 🥈 Argent foncé
            2: (160, 90, 30),    # 🥉 Bronze foncé
        }
        
        # Affichage des lignes
        for row_idx, row in enumerate(self.rows):
            row_y = data_start_y + row_idx * row_height - self.scroll_offset
            
            # Skip si hors de la zone visible
            if row_y < data_start_y - row_height or row_y > clip_rect.bottom:
                continue
            
            # ✅ Couleur selon le rang (top 3 = couleurs foncées lisibles, reste = noir)
            if row_idx in PODIUM_COLORS:
                color = PODIUM_COLORS[row_idx]
                shadow_color = (50, 50, 50)
            else:
                color = COLORS["text_black"]
                shadow_color = (150, 150, 150)
            
            # Affichage des cellules
            for col_idx, cell in enumerate(row):
                draw_text_with_shadow(
                    screen,
                    cell,
                    (col_x_positions[col_idx], row_y),
                    self.fonts["body"],
                    color=color,
                    shadow_color=shadow_color,
                    shadow_offset=(2, 2),
                )
        
        # Retirer le clip
        screen.set_clip(None)
        
        # =============================================
        # ✅ Indicateur de scroll épuré (barre verticale)
        # =============================================
        if len(self.rows) > 6:
            # Calculs pour la scrollbar
            visible_height = clip_rect.height
            total_content_height = len(self.rows) * row_height
            
            if total_content_height > visible_height:
                # Position et taille de la scrollbar
                scrollbar_x = table_rect.right - 25
                scrollbar_track_y = data_start_y
                scrollbar_track_height = visible_height - 10
                
                # Taille du thumb proportionnelle
                thumb_height = max(30, (visible_height / total_content_height) * scrollbar_track_height)
                
                # Position du thumb selon le scroll
                max_scroll = total_content_height - visible_height
                if max_scroll > 0:
                    scroll_ratio = self.scroll_offset / max_scroll
                else:
                    scroll_ratio = 0
                thumb_y = scrollbar_track_y + scroll_ratio * (scrollbar_track_height - thumb_height)
                
                # ✅ Track (fond) - très discret
                track_color = (200, 190, 160)  # Beige discret
                pygame.draw.rect(
                    screen,
                    track_color,
                    (scrollbar_x, scrollbar_track_y, 8, scrollbar_track_height),
                    border_radius=4
                )
                
                # ✅ Thumb (curseur) - légèrement plus foncé
                thumb_color = (160, 140, 100)  # Marron clair
                pygame.draw.rect(
                    screen,
                    thumb_color,
                    (scrollbar_x, thumb_y, 8, thumb_height),
                    border_radius=4
                )
