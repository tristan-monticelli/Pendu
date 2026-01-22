"""
BUT DE LA SCÈNE
- Afficher la fin de partie (victoire / défaite).
- Afficher :
    - mot à trouver
    - difficulté
    - temps
    - score
- Mettre à jour le classement (leaderboard) :
    - update_player_after_game
    - save_leaderboard
    - recalculer last_player_summary (pour le menu)

NAVIGATION
- Bouton "Rejouer" : relance une partie avec la même difficulté
- Bouton "Menu" : retour menu
- ESC : retour menu

PAYLOAD ATTENDU (depuis game_scene.py)
- status : "won" / "lost"
- score : int
- elapsed_seconds : int
- difficulty : str
- secret_word : str
- wrong_letters : list[str]
"""

from __future__ import annotations

from datetime import datetime, timezone

import pygame

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BTN_W,
    BTN_H,
    LEADERBOARD_PATH,
)

from core.leaderboard_io import (
    update_player_after_game,
    save_leaderboard,
    get_last_player_summary,
)

from ui.draw_helpers import clear_screen, draw_title, draw_text_lines, format_duration, draw_hint_bottom
from ui.widgets import make_button, handle_button_event, draw_button, show_toast
from ui.layout import vertical_stack


class GameOverScene:
    """
    Scène de fin : affiche les résultats et sauvegarde le classement.
    """

    def __init__(self, manager, shared, runtime_state, payload):
        """
        Constructeur.

        Paramètres :
        - manager : SceneManager (navigation)
        - shared : ressources (fonts)
        - runtime_state : état global (pseudo, leaderboard_cache, toast_manager)
        - payload : résultats de la partie (voir docstring en haut)
        """
        self.manager = manager
        self.shared = shared
        self.runtime_state = runtime_state
        self.payload = payload

        self.fonts = self.shared["fonts"]

        # Boutons
        self.btn_retry = None
        self.btn_menu = None

        # Texte à afficher
        self.lines = []

        # Pour éviter de sauvegarder deux fois si on revient sur la scène
        self._saved = False

    def on_enter(self):
        """
        Appelé quand on arrive sur la scène.

        Étapes :
        1) construire les lignes à afficher
        2) sauvegarder le score dans le leaderboard (1 seule fois)
        3) créer les boutons
        """
        self.lines = self._build_result_lines()

        # On sauvegarde tout de suite en arrivant sur la scène
        self._save_result_once()

        # Boutons centrés (Rejouer / Menu)
        rects = vertical_stack(
            start_x=(WINDOW_WIDTH - BTN_W) // 2,
            start_y=(WINDOW_HEIGHT // 2) + 120,
            rect_w=BTN_W,
            rect_h=BTN_H,
            count=2,
            gap=16,
        )

        def action_retry():
            # Rejouer avec la même difficulté
            diff = self.payload.get("difficulty", "MOYEN")
            self.manager.go_to("game", payload={"difficulty": diff})

        def action_menu():
            self.manager.go_to("menu")

        self.btn_retry = make_button(rects[0], "Rejouer", action_retry)
        self.btn_menu = make_button(rects[1], "Menu", action_menu)

    def _build_result_lines(self):
        """
        Construit les lignes affichées (résumé de fin de partie).
        """
        status = self.payload.get("status", "lost")
        score = int(self.payload.get("score", 0))
        elapsed_seconds = int(self.payload.get("elapsed_seconds", 0))
        difficulty = self.payload.get("difficulty", "MOYEN")
        secret_word = self.payload.get("secret_word", "—")

        if status == "won":
            title_line = "VICTOIRE !"
        else:
            title_line = "DÉFAITE..."

        return [
            title_line,
            f"Mot : {secret_word}",
            f"Difficulté : {difficulty}",
            f"Temps : {format_duration(elapsed_seconds)}",
            f"Score : {score}",
        ]

    def _save_result_once(self):
        """
        Met à jour le leaderboard et sauvegarde.

        Important :
        - On utilise runtime_state["leaderboard_cache"] pour garder un cache.
        - On réécrit le fichier leaderboard.txt.
        - On met à jour runtime_state["last_player_summary"] pour le menu.
        """
        if self._saved:
            return

        pseudo = self.runtime_state.get("active_pseudo")
        if not pseudo:
            # Normalement impossible (pseudo obligatoire), mais on sécurise
            show_toast(self.runtime_state["toast_manager"], "Pseudo manquant : score non sauvegardé", 2.0)
            self._saved = True
            return

        score = int(self.payload.get("score", 0))
        elapsed_seconds = int(self.payload.get("elapsed_seconds", 0))

        # Date ISO simple (triable et propre)
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        leaderboard = self.runtime_state.get("leaderboard_cache", {})

        # 1) Update en mémoire
        update_player_after_game(
            leaderboard=leaderboard,
            pseudo=pseudo,
            score=score,
            elapsed_seconds=elapsed_seconds,
            now_iso=now_iso,
        )

        # 2) Sauvegarde sur disque
        save_leaderboard(LEADERBOARD_PATH, leaderboard)

        # 3) Mettre à jour le résumé "dernier joueur"
        self.runtime_state["last_player_summary"] = get_last_player_summary(leaderboard)

        # Message utilisateur
        show_toast(self.runtime_state["toast_manager"], "Score sauvegardé", 1.2)

        self._saved = True

    def handle_event(self, event):
        """
        Gestion des events.

        Règles :
        - ESC -> menu
        - clic boutons -> actions
        """
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.go_to("menu")
            return

        mouse_pos = pygame.mouse.get_pos()
        handle_button_event(self.btn_retry, event, mouse_pos)
        handle_button_event(self.btn_menu, event, mouse_pos)

    def update(self, dt):
        """
        Pas d'animation spéciale.
        """
        return

    def draw(self, screen):
        """
        Dessin :
        - fond
        - titre (Game Over)
        - lignes résultat
        - boutons
        """
        clear_screen(screen)
        draw_title(screen, self.fonts, "FIN DE PARTIE")

        # Afficher le résultat (un bloc de lignes)
        draw_text_lines(
            screen=screen,
            fonts=self.fonts,
            lines=self.lines,
            x=60,
            y=150,
            small=False,
        )

        # Boutons
        draw_button(screen, self.btn_retry, self.fonts)
        draw_button(screen, self.btn_menu, self.fonts)

        draw_hint_bottom(screen, self.fonts, "ESC pour revenir au menu")
