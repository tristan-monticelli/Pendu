"""
add_word_scene.py — Scène "Ajouter un mot" (DA Simpson)

But
- Permettre au joueur d'ajouter un mot au dictionnaire du jeu.
- Le mot est ajouté dans le fichier des mots (WORDS_PATH) via core/words_io.py.
- Le niveau choisi ici est volontairement "MOYEN" (choix simple pour le projet).

Ce que la scène gère
- Une saisie de texte (TextInput) pour le mot.
- Deux boutons : VALIDER (ajout) et RETOUR (menu).
- Des règles simples rappelées à l'écran, pour éviter les erreurs.

Ce que la scène ne fait pas
- Elle ne vérifie pas elle-même le fichier en détail : la vraie validation est dans add_word(...)
  (doublons, caractères interdits, etc.).
- Elle ne gère pas la difficulté : l'ajout est fait en MOYEN pour rester cohérent et simple.
"""

from __future__ import annotations

import pygame

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    COLORS,
    BUTTON_SIZES,
    MARGIN_SCREEN,
    GAP_BUTTONS,
    WORDS_PATH,
)

from ui.simpson_theme import (
    draw_simpson_background,
    draw_cartoon_card,
    draw_text_with_shadow,
    draw_outlined_text,
)

from ui.simpson_components import (
    SimpsonButton,
    TextInput,
    make_button,
    make_text_input,
    show_toast,
)

from core.words_io import add_word


class AddWordScene:
    """
    Scène d'ajout de mot.

    Idée générale
    - Le joueur tape un mot dans un champ.
    - Il valide avec le bouton VALIDER ou la touche Entrée.
    - On affiche un message (toast) pour dire si l'ajout a réussi ou non.

    Rappels des règles (affichées dans la card)
    - 1 seul mot (pas d'espaces)
    - Lettres uniquement (pas de chiffres / symboles)
    - Ajout au niveau MOYEN (choix du projet)

    Données utilisées
    - runtime_state["toast_manager"] : pour afficher les messages temporaires.
    """

    def __init__(self, manager, shared, runtime_state, payload):
        """
        Initialise la scène.

        Paramètres
        - manager : SceneManager (sert à revenir au menu).
        - shared : ressources partagées (au minimum les fonts).
        - runtime_state : état global (toast_manager, etc.).
        - payload : non utilisé ici, mais conservé pour respecter le contrat des scènes.
        """
        self.manager = manager
        self.shared = shared
        self.runtime_state = runtime_state
        self.payload = payload

        self.fonts = self.shared["fonts"]

        # Composants UI (créés dans on_enter)
        self.word_input = None
        self.btn_validate = None
        self.btn_back = None

        # Texte d'aide volontairement court pour rester lisible dans la card
        self.help_lines = [
            "1 mot sans espace",
            "Lettres uniquement",
            "Niveau MOYEN",
        ]

    def on_enter(self):
        """
        Appelé quand on arrive sur la scène.

        Ici on crée l'interface :
        - champ de saisie centré
        - boutons (VALIDER / RETOUR)

        Remarque
        - On recrée l'UI à chaque entrée pour être sûr d'avoir un état propre.
        """
        # Champ de saisie (centré horizontalement)
        input_width, input_height = 500, 70
        input_x = (WINDOW_WIDTH - input_width) // 2
        input_y = WINDOW_HEIGHT // 2 - 120

        input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
        self.word_input = make_text_input(
            rect=input_rect,
            placeholder="Entrer un nouveau mot",
            max_len=32,         # limite large : assez pour la plupart des mots
            letters_only=True,  # on bloque déjà les symboles / espaces au clavier
        )

        # Boutons (créés à part pour garder on_enter lisible)
        self._create_buttons()

    def _create_buttons(self):
        """
        Crée les boutons de la scène.

        Logique
        - VALIDER : appelle add_word(...) avec le contenu du champ.
          -> add_word renvoie (ok, msg) : ok bool, msg string à afficher.
        - RETOUR : revient au menu principal.

        Note
        - On place les boutons au centre (colonne) pour garder un écran simple.
        """
        btn_width, btn_height = BUTTON_SIZES["normal"]

        start_x = (WINDOW_WIDTH - btn_width) // 2
        start_y = WINDOW_HEIGHT // 2

        def action_validate():
            """Valide et tente d'ajouter le mot dans le fichier."""
            ok, msg = add_word(WORDS_PATH, self.word_input.text)

            # On affiche toujours un message : soit "ajout ok", soit raison du refus
            show_toast(self.runtime_state["toast_manager"], msg, 2.0)

            # Si ajout réussi : vider le champ pour permettre un nouvel ajout
            if ok:
                self.word_input.text = ""

        def action_back():
            """Retour au menu."""
            self.manager.go_to("menu")

        # Bouton VALIDER : vert pâle pour rester cohérent avec le bouton JOUER
        self.btn_validate = make_button(
            rect=pygame.Rect(start_x, start_y, btn_width, btn_height),
            text="VALIDER",
            action=action_validate,
            color=COLORS["btn_green_pale"],
        )

        # Bouton RETOUR : jaune pâle (couleur "neutre" du projet)
        self.btn_back = make_button(
            rect=pygame.Rect(start_x, start_y + btn_height + GAP_BUTTONS, btn_width, btn_height),
            text="RETOUR",
            action=action_back,
            color=COLORS["btn_yellow_pale"],
        )

    def handle_event(self, event):
        """
        Gestion des événements Pygame.

        Raccourcis
        - ESC : retour au menu
        - ENTREE : valider directement (comme cliquer sur VALIDER)

        Déroulé
        - On laisse d'abord le champ gérer la saisie.
        - Si submitted : on déclenche l'action du bouton VALIDER.
        - Puis on relaye l'event aux boutons (hover + clic).
        """
        # ESC -> retour menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.go_to("menu")
            return

        # Champ de saisie
        result = self.word_input.handle_event(event)

        # Entrée dans le champ : comportement identique au bouton "VALIDER"
        if result["submitted"]:
            self.btn_validate.action()

        # Boutons
        mouse_pos = pygame.mouse.get_pos()
        self.btn_validate.handle_event(event, mouse_pos)
        self.btn_back.handle_event(event, mouse_pos)

    def update(self, dt):
        """
        Mise à jour frame.

        Ici on met surtout à jour :
        - le clignotement du curseur dans le champ de saisie
        """
        self.word_input.update(dt)

    def draw(self, screen):
        """
        Dessine l'écran "Ajouter un mot".

        Ordre
        1) Fond Simpson
        2) Titre
        3) Card "REGLES" (rappels)
        4) Champ de saisie
        5) Boutons
        6) Hint en bas (entrer/esc)
        """
        draw_simpson_background(screen)

        # Titre
        title_y = 80
        draw_outlined_text(
            screen,
            "AJOUTER UN MOT",
            (WINDOW_WIDTH // 2, title_y),
            self.fonts["title"],
            color=COLORS["simpson_yellow"],
            outline_color=COLORS["border_black"],
            outline_width=6,
            centered=True,
        )

        # Card règles (même format que les cards d'autres scènes pour rester cohérent)
        help_card_rect = pygame.Rect(
            MARGIN_SCREEN,
            160,
            450,
            240
        )

        draw_cartoon_card(
            screen,
            help_card_rect,
            bg_color=COLORS["bg_card"],
        )

        # Titre de la card
        draw_text_with_shadow(
            screen,
            "REGLES",
            (help_card_rect.centerx, help_card_rect.y + 28),
            self.fonts["body"],
            color=COLORS["text_black"],
            shadow_color=(150, 150, 150),
            shadow_offset=(2, 2),
            centered=True,
        )

        # Ligne séparatrice
        line_y = help_card_rect.y + 60
        pygame.draw.line(
            screen,
            COLORS["border_black"],
            (help_card_rect.x + 20, line_y),
            (help_card_rect.x + help_card_rect.width - 20, line_y),
            3
        )

        # Lignes de règles (format court volontairement)
        rules_start_y = line_y + 20
        line_height = 35

        for i, line in enumerate(self.help_lines):
            y_pos = rules_start_y + (i * line_height)
            draw_text_with_shadow(
                screen,
                line,
                (help_card_rect.x + 30, y_pos),
                self.fonts["small"],
                color=COLORS["text_black"],
                shadow_color=(150, 150, 150),
                shadow_offset=(1, 1),
            )

        # Champ de saisie
        self.word_input.draw(screen, self.fonts["body"])

        # Boutons
        self.btn_validate.draw(screen, self.fonts["body"])
        self.btn_back.draw(screen, self.fonts["body"])

        # Hint bas de l'écran
        hint_text = "ENTREE pour valider   |   ESC pour revenir"
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
