"""
BUT DE LA SCÈNE
- Écran d'accueil du jeu.
- L'utilisateur doit entrer un pseudo avant de jouer (ergonomique).
- Afficher les infos du dernier joueur :
    - temps de jeu total
    - meilleur score
    - temps lors de ce meilleur score
- Permettre d'aller :
    - Jouer
    - Modifier difficulté
    - Ajouter un mot
    - Classement
    - Quitter
"""

from __future__ import annotations

import pygame

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    INPUT_W,
    INPUT_H,
    BTN_W,
    BTN_H,
    DIFFICULTIES,
    DEFAULT_DIFFICULTY,
)

from ui.widgets import (
    make_button,
    handle_button_event,
    draw_button,
    make_text_input,
    handle_text_input_event,
    draw_text_input,
    show_toast,
)

from ui.draw_helpers import clear_screen, draw_title, draw_text_lines, format_duration
from ui.layout import center_rect, vertical_stack
from core.leaderboard_io import validate_pseudo


class MenuScene:
    """
    Scène Menu : pseudo + boutons + infos dernier joueur.
    """

    def __init__(self, manager, shared, runtime_state, payload):
        self.manager = manager
        self.shared = shared
        self.runtime_state = runtime_state
        self.payload = payload

        self.fonts = self.shared["fonts"]

        self.pseudo_input = None
        self.buttons = []
        self.play_button = None

        # Nouveau : bouton difficulté
        self.diff_button = None

        self.last_player_lines = []


    def on_enter(self):
        """
        Créer l'UI (input + boutons) + infos du dernier joueur.
        """
        rect_input = center_rect(WINDOW_WIDTH, WINDOW_HEIGHT, INPUT_W, INPUT_H, y_offset=-170)
        self.pseudo_input = make_text_input(rect_input, "Entrer un pseudo", max_len=16)

        if self.runtime_state.get("active_pseudo"):
            self.pseudo_input.text = self.runtime_state["active_pseudo"]

        # On stocke la difficulté choisie dans runtime_state (simple)
        if "selected_difficulty" not in self.runtime_state:
            self.runtime_state["selected_difficulty"] = DEFAULT_DIFFICULTY

        self.last_player_lines = self._build_last_player_lines()

        rects = vertical_stack(
            start_x=(WINDOW_WIDTH - BTN_W) // 2,
            start_y=(WINDOW_HEIGHT // 2) - 20,
            rect_w=BTN_W,
            rect_h=BTN_H,
            count=5,
            gap=14,
        )


        def action_play():
            ok, normalized, msg = validate_pseudo(self.pseudo_input.text)
            if not ok:
                show_toast(self.runtime_state["toast_manager"], msg, 2.0)
                return

            self.runtime_state["active_pseudo"] = normalized

            diff = self.runtime_state.get("selected_difficulty", DEFAULT_DIFFICULTY)
            self.manager.go_to("game", payload={"difficulty": diff})


        def action_change_difficulty():
            """
            Cycle la difficulté : FACILE -> MOYEN -> DIFFICILE -> FACILE ...
            """
            current = self.runtime_state.get("selected_difficulty", DEFAULT_DIFFICULTY)
            if current not in DIFFICULTIES:
                current = DEFAULT_DIFFICULTY

            idx = DIFFICULTIES.index(current)
            idx = (idx + 1) % len(DIFFICULTIES)
            new_diff = DIFFICULTIES[idx]

            self.runtime_state["selected_difficulty"] = new_diff
            self.diff_button.label = f"Difficulté : {new_diff}"


        def action_add_word():
            self.manager.go_to("add_word")


        def action_leaderboard():
            self.manager.go_to("leaderboard")


        def action_quit():
            self.runtime_state["should_quit"] = True

        self.play_button = make_button(rects[0], "Jouer", action_play, enabled=False)

        current_diff = self.runtime_state.get("selected_difficulty", DEFAULT_DIFFICULTY)
        self.diff_button = make_button(rects[1], f"Difficulté : {current_diff}", action_change_difficulty)

        self.buttons = [
            self.play_button,
            self.diff_button,
            make_button(rects[2], "Ajouter un mot", action_add_word),
            make_button(rects[3], "Classement", action_leaderboard),
            make_button(rects[4], "Quitter", action_quit),
        ]

        self._refresh_play_enabled()


    def _build_last_player_lines(self):
        summary = self.runtime_state.get("last_player_summary", {})
        if not summary:
            return ["Aucun joueur enregistré"]

        pseudo = summary.get("pseudo", "—")
        total_s = int(summary.get("total_play_time_seconds", 0))
        best_score = int(summary.get("best_score", 0))
        best_time_s = int(summary.get("best_score_time_seconds", 0))

        return [
            f"Dernier joueur : {pseudo}",
            f"Temps total : {format_duration(total_s)}",
            f"Meilleur score : {best_score}",
            f"Temps du record : {format_duration(best_time_s)}",
        ]

    def _refresh_play_enabled(self):
        ok, normalized, msg = validate_pseudo(self.pseudo_input.text)
        self.pseudo_input.validation_message = msg if not ok else ""
        self.play_button.enabled = ok
        if ok:
            self.runtime_state["active_pseudo"] = normalized


    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        result = handle_text_input_event(self.pseudo_input, event)

        if result["changed"]:
            self._refresh_play_enabled()

        if result["submitted"]:
            ok, _, msg = validate_pseudo(self.pseudo_input.text)
            show_toast(self.runtime_state["toast_manager"], "Pseudo validé" if ok else msg, 1.5)
            self._refresh_play_enabled()

        for btn in self.buttons:
            handle_button_event(btn, event, mouse_pos)


    def update(self, dt):
        return


    def draw(self, screen):
        clear_screen(screen)
        draw_title(screen, self.fonts, "PENDU")

        draw_text_lines(
            screen=screen,
            fonts=self.fonts,
            lines=self.last_player_lines,
            x=60,
            y=130,
            small=False,
        )

        draw_text_input(screen, self.pseudo_input, self.fonts)

        for btn in self.buttons:
            draw_button(screen, btn, self.fonts)

        draw_text_lines(
            screen=screen,
            fonts=self.fonts,
            lines=["Astuce : appuyer sur Entrée pour valider le pseudo"],
            x=60,
            y=WINDOW_HEIGHT - 50,
            small=True,
        )
