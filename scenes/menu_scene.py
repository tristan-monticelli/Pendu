"""
BUT DE LA SCÈNE
- Écran d'accueil du jeu.
- L'utilisateur doit entrer un pseudo avant de jouer (ergonomique).
- Afficher les infos du dernier joueur :
    - temps de jeu total
    - meilleur score
    - temps lors du meilleur score
- Permettre d'aller :
    - Jouer
    - Ajouter un mot
    - Classement
    - Quitter

RÈGLES IMPORTANTES
- Cette scène ne contient pas la logique du pendu (c'est dans game_state.py).
- Ici on fait juste l'interface + navigation.

DÉPENDANCES
- widgets.py : boutons + champ texte + toasts
- draw_helpers.py : fonctions simples d'affichage
- layout.py : placement des rectangles
- leaderboard_io.py : validation pseudo + récupération stats dernier joueur
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
        """
        Constructeur de la scène.

        Paramètres :
        - manager : SceneManager (pour naviguer)
        - shared : ressources partagées (fonts)
        - runtime_state : état global (pseudo, leaderboard_cache, etc.)
        - payload : données optionnelles (ici pas utile)
        """
        self.manager = manager
        self.shared = shared
        self.runtime_state = runtime_state
        self.payload = payload

        # Fonts (on les utilise souvent)
        self.fonts = self.shared["fonts"]

        # Widgets (créés dans on_enter pour être propre)
        self.pseudo_input = None
        self.buttons = []
        self.play_button = None

        # Lignes affichées pour "dernier joueur"
        self.last_player_lines = []


    def on_enter(self):
        """
        Appelé quand on arrive sur la scène.

        Objectif :
        - Créer l'UI (input + boutons)
        - Préparer les infos du dernier joueur
        """
        # 1) Champ pseudo centré un peu au-dessus du centre
        rect_input = center_rect(WINDOW_WIDTH, WINDOW_HEIGHT, INPUT_W, INPUT_H, y_offset=-160)
        self.pseudo_input = make_text_input(rect_input, "Entrer un pseudo", max_len=16)

        # 2) Pré-remplissage si on a déjà un pseudo actif
        if self.runtime_state.get("active_pseudo"):
            self.pseudo_input.text = self.runtime_state["active_pseudo"]

        # 3) Préparer les lignes du "dernier joueur"
        self.last_player_lines = self._build_last_player_lines()

        # 4) Boutons (alignés verticalement)
        rects = vertical_stack(
            start_x=(WINDOW_WIDTH - BTN_W) // 2,
            start_y=(WINDOW_HEIGHT // 2) - 20,
            rect_w=BTN_W,
            rect_h=BTN_H,
            count=4,
            gap=16,
        )


        # Actions des boutons (fonctions internes simples)
        def action_play():
            # On vérifie encore le pseudo (sécurité)
            ok, normalized, msg = validate_pseudo(self.pseudo_input.text)
            if not ok:
                show_toast(self.runtime_state["toast_manager"], msg, 2.0)
                return

            # On stocke le pseudo globalement
            self.runtime_state["active_pseudo"] = normalized

            # On lance la partie en difficulté MOYEN (choix simple)
            self.manager.go_to("game", payload={"difficulty": "MOYEN"})

        def action_add_word():
            self.manager.go_to("add_word")


        def action_leaderboard():
            self.manager.go_to("leaderboard")


        def action_quit():
            self.runtime_state["should_quit"] = True

        # Bouton "Jouer" désactivé si pseudo invalide
        self.play_button = make_button(rects[0], "Jouer", action_play, enabled=False)

        self.buttons = [
            self.play_button,
            make_button(rects[1], "Ajouter un mot", action_add_word),
            make_button(rects[2], "Classement", action_leaderboard),
            make_button(rects[3], "Quitter", action_quit),
        ]

        # 5) Mettre à jour l'état du bouton Jouer au démarrage
        self._refresh_play_enabled()


    def _build_last_player_lines(self):
        """
        Construit les lignes affichées pour la partie "dernier joueur".

        Retour :
        - liste de chaînes (affichables avec draw_text_lines)

        Source :
        - runtime_state["last_player_summary"] (créé dans main.py)
        """
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
        """
        Active / désactive le bouton "Jouer" selon la validité du pseudo.
        Met aussi un message dans le champ (validation_message).
        """
        ok, normalized, msg = validate_pseudo(self.pseudo_input.text)

        # Message sous l'input (ex: "Pseudo trop long")
        self.pseudo_input.validation_message = msg if not ok else ""

        # Activer le bouton jouer uniquement si ok
        self.play_button.enabled = ok

        # Si ok, on garde le pseudo normalisé dans runtime_state (pratique)
        if ok:
            self.runtime_state["active_pseudo"] = normalized


    def handle_event(self, event):
        """
        Gestion des events Pygame (clavier / souris).

        Étapes :
        1) Gestion de l'input pseudo
        2) Gestion des boutons
        """
        mouse_pos = pygame.mouse.get_pos()

        # 1) Champ pseudo : focus + saisie
        result = handle_text_input_event(self.pseudo_input, event)

        # Si le texte a changé -> on refresh le bouton "Jouer"
        if result["changed"]:
            self._refresh_play_enabled()

        # Si l'utilisateur appuie sur ENTER dans l'input
        if result["submitted"]:
            ok, _, msg = validate_pseudo(self.pseudo_input.text)
            if ok:
                show_toast(self.runtime_state["toast_manager"], "Pseudo validé", 1.2)
            else:
                show_toast(self.runtime_state["toast_manager"], msg, 2.0)
            self._refresh_play_enabled()

        # 2) Boutons
        for btn in self.buttons:
            handle_button_event(btn, event, mouse_pos)


    def update(self, dt):
        """
        Pas d'animation spéciale sur le menu.
        On laisse vide (mais la méthode doit exister).
        """
        return


    def draw(self, screen):
        """
        Dessin du menu.

        Ordre d'affichage :
        1) fond
        2) titre
        3) infos dernier joueur
        4) champ pseudo
        5) boutons
        """
        clear_screen(screen)

        # 1) Titre
        draw_title(screen, self.fonts, "PENDU")

        # 2) Bloc "dernier joueur" (position fixe, simple)
        draw_text_lines(
            screen=screen,
            fonts=self.fonts,
            lines=self.last_player_lines,
            x=60,
            y=130,
            small=False,
        )

        # 3) Champ pseudo
        draw_text_input(screen, self.pseudo_input, self.fonts)

        # 4) Boutons
        for btn in self.buttons:
            draw_button(screen, btn, self.fonts)

        # Petit hint en bas (simple)
        draw_text_lines(
            screen=screen,
            fonts=self.fonts,
            lines=["Astuce : appuyer sur Entrée pour valider le pseudo"],
            x=60,
            y=WINDOW_HEIGHT - 50,
            small=True,
        )
