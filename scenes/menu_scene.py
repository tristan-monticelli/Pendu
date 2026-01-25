"""
Rôle de la scène
- Afficher l'écran d'accueil du jeu.
- Demander un pseudo (obligatoire) et contrôler qu'il est valide.
- Permettre de choisir une difficulté (cycle FACILE -> MOYEN -> DIFFICILE).
- Donner accès aux autres écrans : Ajouter un mot, Classement, Quitter.
- Afficher un petit résumé du dernier joueur (si on a des données).

Ce que la scène ne fait pas
- Elle ne contient pas la logique du pendu.
- Elle ne gère pas le leaderboard directement (elle lit juste le cache runtime_state).
- Elle ne sauvegarde rien : elle prépare juste les infos et lance la scène "game".
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
    DIFFICULTIES,
    DEFAULT_DIFFICULTY,
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
    TextInput,
    make_button,
    make_text_input,
    show_toast,
)


def validate_pseudo(pseudo_text: str) -> tuple[bool, str, str]:
    """
    Valide le pseudo saisi dans le menu.

    Règles choisies ici
    - Obligatoire (pas vide)
    - Maximum 9 caractères (pour que ça rentre bien dans l'UI + leaderboard)
    - Lettres uniquement (pas de chiffres, pas d'espaces, pas de ponctuation)

    Retour
    - ok : True si valide
    - normalized : pseudo "nettoyé" (strip + casse conservée ici)
    - message : message court utilisé dans l'UI (validation_message ou toast)
    """
    pseudo = pseudo_text.strip()

    if not pseudo:
        return False, "", "Entrer un pseudo"

    # On limite volontairement à 9 pour éviter les débordements visuels.
    if len(pseudo) > 9:
        return False, "", "9 caracteres max"

    # On bloque tout sauf les lettres : simplifie le parsing et évite des cas tordus.
    if not pseudo.isalpha():
        return False, "", "Lettres uniquement"

    return True, pseudo, "Pseudo valide"


class MenuScene:
    """
    Scène du menu principal.

    Ce qu'on gère ici
    - Un champ TextInput pour le pseudo.
    - Une liste de boutons (Play, difficulté, ajout mot, classement, quitter).
    - L'affichage des infos "dernier joueur" (lues depuis runtime_state).

    Données importantes dans runtime_state
    - active_pseudo : pseudo validé (sert ensuite dans la partie)
    - selected_difficulty : difficulté courante
    - leaderboard_cache / last_player_summary : infos déjà chargées au lancement
    - toast_manager : messages temporaires (erreurs, infos)
    - should_quit : flag pour quitter la boucle principale
    """

    def __init__(self, manager, shared, runtime_state, payload):
        """
        Constructeur : on stocke juste les références.

        Important
        - On ne construit pas toute l'UI ici pour garder une logique claire :
          l'UI est créée dans on_enter(), appelé à chaque entrée dans la scène.
        - payload n'est pas utilisé ici, mais on le garde pour rester compatible
          avec la signature des autres scènes.
        """
        self.manager = manager
        self.shared = shared
        self.runtime_state = runtime_state
        self.payload = payload

        self.fonts = self.shared["fonts"]

        # Composants UI (créés dans on_enter)
        self.pseudo_input = None
        self.buttons = []
        self.play_button = None
        self.diff_button = None

        # Texte d'affichage "dernier joueur"
        self.last_player_lines = []

    def on_enter(self):
        """
        Appelé quand on arrive sur le menu.

        Ici on (re)construit l'UI :
        - champ pseudo
        - difficulté par défaut si besoin
        - infos dernier joueur
        - boutons + callbacks
        - validation initiale pour activer/désactiver "JOUER"
        """
        # Champ de saisie pseudo (centré, un peu au-dessus des boutons)
        input_width, input_height = 500, 70
        input_x = (WINDOW_WIDTH - input_width) // 2
        input_y = WINDOW_HEIGHT // 2 - 200

        input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
        self.pseudo_input = make_text_input(
            rect=input_rect,
            placeholder="Entrer un pseudo",
            max_len=9,
            letters_only=True,
        )

        # Si on a déjà un pseudo dans l'état global, on le remet dans le champ
        if self.runtime_state.get("active_pseudo"):
            self.pseudo_input.text = self.runtime_state["active_pseudo"]

        # Difficulté en mémoire (si pas encore définie)
        if "selected_difficulty" not in self.runtime_state:
            self.runtime_state["selected_difficulty"] = DEFAULT_DIFFICULTY

        # Infos "dernier joueur" (affichées dans la card)
        self.last_player_lines = self._build_last_player_lines()

        # Création des boutons (avec leurs actions)
        self._create_buttons()

        # Active/désactive le bouton JOUER en fonction du pseudo actuel
        self._refresh_play_enabled()

    def _create_buttons(self):
        """
        Crée tous les boutons du menu.

        Note
        - Les callbacks sont définis ici pour garder le code "menu" au même endroit.
        - On stocke les boutons dans self.buttons pour pouvoir les parcourir facilement
          dans handle_event() et draw().
        """
        btn_width, btn_height = BUTTON_SIZES["large"]

        # Zone de départ des boutons (colonne au centre)
        start_x = (WINDOW_WIDTH - btn_width) // 2
        start_y = WINDOW_HEIGHT // 2 - 50

        # Actions (callbacks) 
        def action_play():
            """Valide le pseudo, prépare les infos utiles, puis lance la scène game."""
            ok, normalized, msg = validate_pseudo(self.pseudo_input.text)
            if not ok:
                show_toast(self.runtime_state["toast_manager"], msg, 2.0)
                return

            self.runtime_state["active_pseudo"] = normalized

            # Difficulté choisie (stockée dans runtime_state)
            diff = self.runtime_state.get("selected_difficulty", DEFAULT_DIFFICULTY)

            # Détection nouveau joueur : utile pour déclencher un tuto si on veut
            leaderboard = self.runtime_state.get("leaderboard_cache", {})
            is_new_player = normalized not in leaderboard

            # Transition vers la scène de jeu (payload = infos ponctuelles)
            self.manager.go_to(
                "game",
                payload={
                    "difficulty": diff,
                    "show_tutorial": is_new_player,
                }
            )

        def action_change_difficulty():
            """Passe à la difficulté suivante et adapte le texte + la couleur du bouton."""
            current = self.runtime_state.get("selected_difficulty", DEFAULT_DIFFICULTY)
            if current not in DIFFICULTIES:
                current = DEFAULT_DIFFICULTY

            idx = DIFFICULTIES.index(current)
            idx = (idx + 1) % len(DIFFICULTIES)
            new_diff = DIFFICULTIES[idx]

            self.runtime_state["selected_difficulty"] = new_diff
            self.diff_button.text = f"NIV : {new_diff}"

            # Feedback visuel simple : une couleur par difficulté
            if new_diff == "FACILE":
                self.diff_button.color = COLORS["btn_blue_pale"]
            elif new_diff == "MOYEN":
                self.diff_button.color = COLORS["btn_orange_pale"]
            else:  # DIFFICILE
                self.diff_button.color = COLORS["btn_red_pale"]

        def action_add_word():
            """Va vers l'écran d'ajout de mot."""
            self.manager.go_to("add_word")

        def action_leaderboard():
            """Va vers l'écran du classement."""
            self.manager.go_to("leaderboard")

        def action_quit():
            """Demande l'arrêt de la boucle principale."""
            self.runtime_state["should_quit"] = True

        # --- Création des boutons ---

        # Bouton JOUER : désactivé tant que le pseudo n'est pas valide
        self.play_button = make_button(
            rect=pygame.Rect(start_x, start_y, btn_width, btn_height),
            text="JOUER",
            action=action_play,
            color=COLORS["btn_green_pale"],
            enabled=False,
        )

        # Bouton difficulté : couleur dépend de la difficulté actuelle
        current_diff = self.runtime_state.get("selected_difficulty", DEFAULT_DIFFICULTY)

        if current_diff == "FACILE":
            diff_color = COLORS["btn_blue_pale"]
        elif current_diff == "MOYEN":
            diff_color = COLORS["btn_orange_pale"]
        else:
            diff_color = COLORS["btn_red_pale"]

        self.diff_button = make_button(
            rect=pygame.Rect(start_x, start_y + btn_height + GAP_BUTTONS, btn_width, btn_height),
            text=f"NIV : {current_diff}",
            action=action_change_difficulty,
            color=diff_color,
        )

        # Ajout mot
        btn_add_word = make_button(
            rect=pygame.Rect(start_x, start_y + 2 * (btn_height + GAP_BUTTONS), btn_width, btn_height),
            text="Ajouter un mot",
            action=action_add_word,
            color=COLORS["btn_yellow_pale"],
        )

        # Classement
        btn_leaderboard = make_button(
            rect=pygame.Rect(start_x, start_y + 3 * (btn_height + GAP_BUTTONS), btn_width, btn_height),
            text="Classement",
            action=action_leaderboard,
            color=COLORS["btn_yellow_pale"],
        )

        # Quitter : petit bouton en bas à droite (plus discret)
        small_width, small_height = BUTTON_SIZES["small"]
        btn_quit = make_button(
            rect=pygame.Rect(
                WINDOW_WIDTH - MARGIN_SCREEN - small_width,
                WINDOW_HEIGHT - MARGIN_SCREEN - small_height,
                small_width,
                small_height
            ),
            text="Quitter",
            action=action_quit,
            color=COLORS["btn_yellow_pale"],
        )

        self.buttons = [
            self.play_button,
            self.diff_button,
            btn_add_word,
            btn_leaderboard,
            btn_quit,
        ]

    def _build_last_player_lines(self):
        """
        Prépare les lignes affichées dans la card "stats joueur".

        On lit runtime_state["last_player_summary"] (rempli au lancement du jeu).
        Si on n'a rien, on affiche juste une phrase simple.
        """
        summary = self.runtime_state.get("last_player_summary", {})
        if not summary:
            return ["Aucun joueur enregistre"]

        pseudo = summary.get("pseudo", "—")
        total_s = int(summary.get("total_play_time_seconds", 0))
        best_score = int(summary.get("best_score", 0))
        best_time_s = int(summary.get("best_score_time_seconds", 0))

        return [
            f"Pseudo : {pseudo}",
            f"Temps total : {format_duration(total_s)}",
            f"Score max : {best_score}",
            f"Temps record : {format_duration(best_time_s)}",
        ]

    def _refresh_play_enabled(self):
        """
        Revalide le pseudo et met à jour l'UI.

        Effets
        - Met un message d'erreur dans le champ (validation_message) si besoin.
        - Active/désactive le bouton "JOUER".
        - Si c'est valide, on stocke aussi active_pseudo dans runtime_state pour garder la valeur.
        """
        ok, normalized, msg = validate_pseudo(self.pseudo_input.text)
        self.pseudo_input.validation_message = msg if not ok else ""
        self.play_button.enabled = ok

        if ok:
            self.runtime_state["active_pseudo"] = normalized

    def handle_event(self, event):
        """
        Gère les événements Pygame pour le menu.

        Déroulé
        - On laisse d'abord le TextInput gérer clics + saisie clavier.
        - Si le texte change : on revalide pour activer le bouton Jouer.
        - Si Entrée est pressée : on lance direct si le pseudo est valide.
        - Ensuite on envoie l'event à chaque bouton (hover + clic).
        """
        mouse_pos = pygame.mouse.get_pos()

        # Champ pseudo
        result = self.pseudo_input.handle_event(event)

        if result["changed"]:
            self._refresh_play_enabled()

        if result["submitted"]:
            ok, _, msg = validate_pseudo(self.pseudo_input.text)
            if ok:
                self.play_button.action()
            else:
                show_toast(self.runtime_state["toast_manager"], msg, 1.5)

        # Boutons
        for btn in self.buttons:
            btn.handle_event(event, mouse_pos)

    def update(self, dt):
        """
        Mise à jour (frame).

        Ici, le menu n'a pas beaucoup de logique :
        - on met surtout à jour le champ de saisie (curseur clignotant).
        """
        self.pseudo_input.update(dt)

    def draw(self, screen):
        """
        Affichage complet du menu.

        Ordre global
        1) Fond (ciel/herbe ou background)
        2) Titres (LE PENDU + sous-titre)
        3) Card stats joueur
        4) Champ pseudo
        5) Boutons
        6) Astuce en bas (Entrée pour jouer)
        """
        # Fond
        draw_simpson_background(screen)

        # Titre principal
        title_y = 100
        draw_outlined_text(
            screen,
            "LE PENDU",
            (WINDOW_WIDTH // 2, title_y),
            self.fonts["huge"],
            color=COLORS["simpson_yellow"],
            outline_color=COLORS["border_black"],
            outline_width=6,
            centered=True,
        )

        # Sous-titre
        subtitle_y = title_y + 120
        draw_text_with_shadow(
            screen,
            "Simpson Edition",
            (WINDOW_WIDTH // 2, subtitle_y),
            self.fonts["large"],
            color=COLORS["text_white"],
            centered=True,
        )

        # Card stats (haut gauche)
        info_card_rect = pygame.Rect(
            MARGIN_SCREEN,
            MARGIN_SCREEN + 50,
            450,
            240
        )

        # Card sans titre intégré : on gère le titre manuellement pour mieux le placer
        draw_cartoon_card(
            screen,
            info_card_rect,
            bg_color=COLORS["bg_card"],
        )

        # Titre de la card (plus petit pour que ça reste propre)
        title_y = info_card_rect.y + 28
        draw_text_with_shadow(
            screen,
            "STATS JOUEUR",
            (info_card_rect.centerx, title_y),
            self.fonts["body"],
            color=COLORS["text_black"],
            shadow_color=(150, 150, 150),
            shadow_offset=(2, 2),
            centered=True,
        )

        # Ligne séparatrice
        line_y = info_card_rect.y + 60
        pygame.draw.line(
            screen,
            COLORS["border_black"],
            (info_card_rect.x + 20, line_y),
            (info_card_rect.x + info_card_rect.width - 20, line_y),
            3
        )

        # Lignes de stats
        stats_start_y = line_y + 20
        line_height = 35

        for i, line in enumerate(self.last_player_lines):
            y_pos = stats_start_y + (i * line_height)
            draw_text_with_shadow(
                screen,
                line,
                (info_card_rect.x + 25, y_pos),
                self.fonts["small"],
                color=COLORS["text_black"],
                shadow_color=(150, 150, 150),
                shadow_offset=(1, 1),
            )

        # Champ pseudo + boutons
        self.pseudo_input.draw(screen, self.fonts["body"])

        for btn in self.buttons:
            btn.draw(screen, self.fonts["body"])

        # Astuce bas d'écran (outline pour bien voir sur le fond)
        hint_text = "ASTUCE :  Appuie sur ENTREE pour valider et jouer"
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
