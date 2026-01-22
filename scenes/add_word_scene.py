"""
BUT DE LA SCÈNE
- Permettre d'ajouter un mot dans data/mots.txt.
- Interface simple :
    - un champ texte
    - un bouton "Valider"
    - un bouton "Retour"
- Afficher un message (toast) pour dire si le mot a été ajouté ou refusé.

RÈGLES IMPORTANTES
- La validation / ajout du mot est faite dans core/words_io.py (add_word).
- Cette scène ne fait pas de logique de jeu.
- Navigation :
    - ESC -> menu
    - bouton Retour -> menu

DÉPENDANCES
- words_io.add_word : ajout + validation
- widgets.py : TextInput, Buttons, Toast
- draw_helpers.py : clear_screen, draw_title, draw_text_lines
- layout.py : placement simple
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
    WORDS_PATH,
)

from core.words_io import add_word

from ui.widgets import (
    make_text_input,
    handle_text_input_event,
    draw_text_input,
    make_button,
    handle_button_event,
    draw_button,
    show_toast,
)

from ui.draw_helpers import clear_screen, draw_title, draw_text_lines
from ui.layout import center_rect, vertical_stack


class AddWordScene:
    """
    Scène Ajout de mot.
    """

    def __init__(self, manager, shared, runtime_state, payload):
        """
        Constructeur.

        Paramètres :
        - manager : SceneManager (pour naviguer)
        - shared : ressources (fonts)
        - runtime_state : état global (toast_manager, etc.)
        - payload : pas utilisé ici
        """
        self.manager = manager
        self.shared = shared
        self.runtime_state = runtime_state
        self.payload = payload

        self.fonts = self.shared["fonts"]

        # Widgets (créés dans on_enter)
        self.word_input = None
        self.btn_validate = None
        self.btn_back = None

        # Petite phrase d'aide
        self.help_lines = [
            "Règles : 1 mot par ligne, sans espaces, sans ';'.",
            "Astuce : pas besoin d'accent (ex: 'eleve' au lieu de 'élève').",
        ]


    def on_enter(self):
        """
        Création des widgets.

        Étapes :
        1) champ texte centré
        2) boutons en dessous (Valider / Retour)
        """
        # 1) Champ texte
        rect_input = center_rect(WINDOW_WIDTH, WINDOW_HEIGHT, INPUT_W, INPUT_H, y_offset=-80)
        self.word_input = make_text_input(rect_input, "Entrer un mot", max_len=32)

        # 2) Boutons (vertical)
        rects = vertical_stack(
            start_x=(WINDOW_WIDTH - BTN_W) // 2,
            start_y=(WINDOW_HEIGHT // 2) + 20,
            rect_w=BTN_W,
            rect_h=BTN_H,
            count=2,
            gap=16,
        )


        def action_validate():
            """
            Action bouton Valider :
            - tente d'ajouter le mot
            - affiche le résultat en toast
            """
            ok, msg = add_word(WORDS_PATH, self.word_input.text)
            show_toast(self.runtime_state["toast_manager"], msg, 2.0)

            # Si ajout OK -> on vide le champ pour pouvoir entrer un nouveau mot
            if ok:
                self.word_input.text = ""


        def action_back():
            self.manager.go_to("menu")

        self.btn_validate = make_button(rects[0], "Valider", action_validate)
        self.btn_back = make_button(rects[1], "Retour", action_back)


    def handle_event(self, event):
        """
        Gestion des events.

        Règles :
        - ESC -> menu
        - ENTER dans l'input -> valider
        - clic sur boutons -> actions
        """
        # 1) Quitter avec ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.go_to("menu")
            return

        mouse_pos = pygame.mouse.get_pos()

        # 2) Gestion du champ texte
        result = handle_text_input_event(self.word_input, event)

        # Si l'utilisateur appuie sur ENTER dans l'input, on valide directement
        if result["submitted"]:
            self.btn_validate.action()

        # 3) Gestion des boutons
        handle_button_event(self.btn_validate, event, mouse_pos)
        handle_button_event(self.btn_back, event, mouse_pos)


    def update(self, dt):
        """
        Pas d'animation.
        """
        return


    def draw(self, screen):
        """
        Dessin.

        Ordre :
        1) fond
        2) titre
        3) texte d'aide
        4) input
        5) boutons
        """
        clear_screen(screen)
        draw_title(screen, self.fonts, "AJOUTER UN MOT")

        draw_text_lines(
            screen=screen,
            fonts=self.fonts,
            lines=self.help_lines,
            x=60,
            y=130,
            small=True,
        )

        draw_text_input(screen, self.word_input, self.fonts)
        draw_button(screen, self.btn_validate, self.fonts)
        draw_button(screen, self.btn_back, self.fonts)
