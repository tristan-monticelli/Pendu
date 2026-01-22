"""
BUT DE LA SCÈNE
- Afficher le classement (plusieurs joueurs possibles).
- Le classement vient de data/leaderboard.txt (chargé dans runtime_state).
- Permettre de revenir au menu facilement.

RÈGLES IMPORTANTES
- Ici on ne calcule pas le score : on affiche juste les données.
- On utilise draw_table() (tableau simple).
- Navigation :
    - ESC -> menu
    - Bouton "Retour" -> menu

DÉPENDANCES
- leaderboard_io.py : tri du classement
- draw_helpers.py : clear_screen, draw_title, draw_table
- widgets.py : bouton retour
"""

from __future__ import annotations

import pygame

from settings import WINDOW_WIDTH, WINDOW_HEIGHT, BTN_W, BTN_H

from core.leaderboard_io import sort_leaderboard

from ui.draw_helpers import clear_screen, draw_title, draw_table, draw_hint_bottom, format_duration
from ui.widgets import make_button, handle_button_event, draw_button


class LeaderboardScene:
    """
    Scène Classement : affiche le tableau des scores.
    """

    def __init__(self, manager, shared, runtime_state, payload):
        """
        Constructeur de la scène.

        Paramètres :
        - manager : SceneManager (pour naviguer)
        - shared : ressources partagées (fonts)
        - runtime_state : état global (leaderboard_cache, etc.)
        - payload : données optionnelles (pas utilisé ici)
        """
        self.manager = manager
        self.shared = shared
        self.runtime_state = runtime_state
        self.payload = payload

        self.fonts = self.shared["fonts"]

        # Données tableau
        self.headers = ["Pseudo", "Best", "T(best)", "T(total)", "Parties"]
        self.rows = []

        # Bouton retour
        self.btn_back = None


    def on_enter(self):
        """
        Appelé quand on arrive sur la scène.

        Étapes :
        1) récupérer le leaderboard depuis runtime_state
        2) trier les profils
        3) construire self.rows (texte prêt à afficher)
        4) créer le bouton retour
        """
        leaderboard = self.runtime_state.get("leaderboard_cache", {})

        # Tri (best_score décroissant)
        profiles = sort_leaderboard(leaderboard)

        # Construire les lignes du tableau
        self.rows = []
        for p in profiles:
            self.rows.append([
                p.pseudo,
                str(p.best_score),
                format_duration(p.best_score_time_seconds),
                format_duration(p.total_play_time_seconds),
                str(p.games_played),
            ])

        # Bouton "Retour" centré en bas
        rect = pygame.Rect((WINDOW_WIDTH - BTN_W) // 2, WINDOW_HEIGHT - 110, BTN_W, BTN_H)


        def action_back():
            self.manager.go_to("menu")

        self.btn_back = make_button(rect, "Retour", action_back)


    def handle_event(self, event):
        """
        Gestion des events.

        Règles :
        - ESC -> menu
        - clic sur bouton retour -> menu
        """
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.go_to("menu")
            return

        mouse_pos = pygame.mouse.get_pos()
        handle_button_event(self.btn_back, event, mouse_pos)


    def update(self, dt):
        """
        Pas d'animation particulière sur le classement.
        """
        return


    def draw(self, screen):
        """
        Dessin de la scène.

        Ordre :
        1) clear
        2) titre
        3) tableau (si vide -> message)
        4) bouton retour
        5) hint bas d'écran
        """
        clear_screen(screen)
        draw_title(screen, self.fonts, "CLASSEMENT")

        if not self.rows:
            # Aucun joueur : message simple
            from ui.draw_helpers import draw_text_lines  # import local pour rester simple
            draw_text_lines(
                screen=screen,
                fonts=self.fonts,
                lines=["Aucun score enregistré pour le moment."],
                x=60,
                y=170,
                small=False,
            )
        else:
            # Tableau : position fixe simple
            draw_table(
                screen=screen,
                fonts=self.fonts,
                headers=self.headers,
                rows=self.rows,
                x=60,
                y=150,
            )

        draw_button(screen, self.btn_back, self.fonts)
        draw_hint_bottom(screen, self.fonts, "ESC pour revenir")
