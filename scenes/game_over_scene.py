"""
game_over_scene.py — Scène de fin de partie (victoire / défaite)

Rôle
- Afficher un écran de résultats après une partie :
  - état (VICTOIRE / DÉFAITE)
  - mot à trouver, difficulté, temps, score
  - visage de Trump adapté (happy si gagné, dead si perdu)
- Sauvegarder le résultat dans le leaderboard (une seule fois).
- Proposer deux actions principales : REJOUER ou revenir au MENU.

Données attendues (payload)
- score : score final de la partie
- elapsed_seconds : durée de la partie (en secondes)
- secret_word : le mot à deviner (affiché en fin)
- difficulty : difficulté jouée
- status : "won" ou "lost" (sert à décider victoire/défaite)

Données utilisées côté runtime_state
- active_pseudo : pseudo du joueur (obligatoire pour sauvegarder)
- leaderboard_cache : classement en mémoire (mis à jour ici)
- toast_manager : pour afficher un petit message de confirmation
"""

from __future__ import annotations

from datetime import datetime, timezone
import pygame

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    COLORS,
    BUTTON_SIZES,
    LEADERBOARD_PATH,
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
    show_toast,
)

from core.leaderboard_io import (
    update_player_after_game,
    save_leaderboard,
    get_last_player_summary,
)


class GameOverScene:
    """
    Scène de fin de partie (style Simpson).

    Ce que fait la scène
    - À l'entrée : déterminer victoire/défaite + sauvegarder le résultat.
    - Affichage : une card centrale avec image Trump, titre, infos et boutons.
    - Interactions :
      - ESC -> menu
      - ENTREE -> rejouer (même difficulté)
      - clic sur REJOUER / MENU

    Important
    - La sauvegarde ne doit pas être faite à chaque frame : on la fait une seule fois
      grâce au flag self._saved.
    """

    def __init__(self, manager, shared, runtime_state, payload):
        """
        Constructeur standard des scènes.

        On stocke les références utiles, puis on initialise des attributs simples.
        L'UI est construite dans on_enter() pour être cohérente quand on revient sur la scène.
        """
        self.manager = manager
        self.shared = shared
        self.runtime_state = runtime_state
        self.payload = payload

        self.fonts = self.shared["fonts"]
        self.assets = self.shared["assets"]

        # Boutons (créés dans _create_buttons)
        self.btn_retry = None
        self.btn_menu = None

        # Statut victoire/défaite (calculé dans on_enter)
        self.is_victory = False

        # Flag de sauvegarde : empêche d'écrire plusieurs fois le même résultat
        self._saved = False

    def on_enter(self):
        """
        Appelé à l'entrée dans la scène.

        Ici on :
        - lit le payload pour savoir si on a gagné ou perdu
        - sauvegarde le résultat dans le leaderboard (une seule fois)
        - crée les boutons de navigation
        """
        self.is_victory = self.payload.get("status", "lost") == "won"
        self._save_result_once()
        self._create_buttons()

    def _save_result_once(self):
        """
        Sauvegarde les résultats dans le classement, mais une seule fois.

        Étapes
        - Récupérer le pseudo (si absent : on ne sauvegarde pas).
        - Lire score et temps depuis le payload.
        - Mettre à jour leaderboard_cache en mémoire.
        - Écrire sur disque (save_leaderboard).
        - Mettre à jour last_player_summary (utile pour le menu).
        - Afficher un toast "Score sauvegardé" pour feedback joueur.

        Remarque
        - now_iso est stocké en UTC pour avoir un format stable.
        """
        if self._saved:
            return

        pseudo = self.runtime_state.get("active_pseudo")
        if not pseudo:
            self._saved = True
            return

        score = int(self.payload.get("score", 0))
        elapsed_seconds = int(self.payload.get("elapsed_seconds", 0))
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        leaderboard = self.runtime_state.get("leaderboard_cache", {})

        update_player_after_game(
            leaderboard=leaderboard,
            pseudo=pseudo,
            score=score,
            elapsed_seconds=elapsed_seconds,
            now_iso=now_iso,
        )

        save_leaderboard(LEADERBOARD_PATH, leaderboard)
        self.runtime_state["last_player_summary"] = get_last_player_summary(leaderboard)

        show_toast(self.runtime_state["toast_manager"], "Score sauvegardé !", 1.5)
        self._saved = True

    def _create_buttons(self):
        """
        Crée les boutons REJOUER et MENU (placés dans la card).

        Détail placement
        - On recalcule ici les coordonnées de la card pour placer les boutons au bon endroit.
        - Les boutons sont côte à côte, en bas de la card, avec un gap fixe.
        """
        btn_width = 220
        btn_height = 55

        # Dimensions de la card (doivent rester cohérentes avec draw)
        card_width = 750
        card_height = 620
        card_x = (WINDOW_WIDTH - card_width) // 2
        card_y = (WINDOW_HEIGHT - card_height) // 2 - 10

        gap = 30
        total_width = btn_width * 2 + gap
        start_x = card_x + (card_width - total_width) // 2
        btn_y = card_y + card_height - 85

        def action_retry():
            # On rejoue en gardant la difficulté si elle est fournie
            diff = self.payload.get("difficulty", "MOYEN")
            self.manager.go_to("game", payload={"difficulty": diff})

        def action_menu():
            self.manager.go_to("menu")

        self.btn_retry = make_button(
            rect=pygame.Rect(start_x, btn_y, btn_width, btn_height),
            text="REJOUER",
            action=action_retry,
            color=COLORS["btn_green_pale"],
        )

        self.btn_menu = make_button(
            rect=pygame.Rect(start_x + btn_width + gap, btn_y, btn_width, btn_height),
            text="MENU",
            action=action_menu,
            color=COLORS["btn_yellow_pale"],
        )

    def handle_event(self, event):
        """
        Gestion des events Pygame sur l'écran de fin.

        Raccourcis clavier
        - ESC : retour menu
        - ENTREE : rejouer direct (même difficulté)

        Souris
        - On relaye l'event aux deux boutons.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.go_to("menu")
                return
            if event.key == pygame.K_RETURN:
                diff = self.payload.get("difficulty", "MOYEN")
                self.manager.go_to("game", payload={"difficulty": diff})
                return

        mouse_pos = pygame.mouse.get_pos()
        self.btn_retry.handle_event(event, mouse_pos)
        self.btn_menu.handle_event(event, mouse_pos)

    def update(self, dt):
        """
        Mise à jour frame.

        Ici il n'y a pas d'animation ni de timer à gérer, donc on laisse vide.
        """
        pass

    def draw(self, screen):
        """
        Dessine l'écran de fin.

        Structure visuelle
        - Fond Simpson
        - Card centrale
        - Image Trump (happy ou dead)
        - Titre (VICTOIRE / DÉFAITE)
        - Infos de partie (mot, difficulté, temps, score)
        - Boutons (rejouer / menu)
        - Astuce en bas (style menu)
        """
        # Fond
        draw_simpson_background(screen)

        # Card principale
        card_width = 750
        card_height = 620
        card_rect = pygame.Rect(
            (WINDOW_WIDTH - card_width) // 2,
            (WINDOW_HEIGHT - card_height) // 2 - 10,
            card_width,
            card_height
        )

        draw_cartoon_card(screen, card_rect, bg_color=COLORS["bg_card"])

        # Visage Trump
        trump_key = "trump_happy" if self.is_victory else "trump_dead"
        trump_bottom = card_rect.top + 40

        if trump_key in self.assets:
            trump_img = self.assets[trump_key]
            trump_rect = trump_img.get_rect(
                centerx=card_rect.centerx,
                top=card_rect.top + 20
            )
            screen.blit(trump_img, trump_rect)
            trump_bottom = trump_rect.bottom

        # Titre victoire/défaite (couleur bien visible)
        if self.is_victory:
            title_text = "VICTOIRE !"
            title_color = (34, 139, 34)  # vert foncé
        else:
            title_text = "DÉFAITE..."
            title_color = (178, 34, 34)  # rouge foncé

        title_y = trump_bottom + 20

        draw_outlined_text(
            screen,
            title_text,
            (card_rect.centerx, title_y),
            self.fonts["huge"],
            color=title_color,
            outline_color=COLORS["border_black"],
            outline_width=4,
            centered=True,
        )

        # Infos de partie
        secret_word = self.payload.get("secret_word", "—").upper()
        difficulty = self.payload.get("difficulty", "MOYEN")
        elapsed_seconds = int(self.payload.get("elapsed_seconds", 0))
        score = int(self.payload.get("score", 0))

        info_start_y = title_y + 80
        line_height = 45
        text_color = COLORS["text_black"]

        draw_text_with_shadow(
            screen,
            f"Le mot était : {secret_word}",
            (card_rect.centerx, info_start_y),
            self.fonts["body"],
            color=text_color,
            shadow_color=(100, 100, 100),
            shadow_offset=(2, 2),
            centered=True,
        )

        draw_text_with_shadow(
            screen,
            f"Difficulté : {difficulty}",
            (card_rect.centerx, info_start_y + line_height),
            self.fonts["body"],
            color=text_color,
            shadow_color=(100, 100, 100),
            shadow_offset=(1, 1),
            centered=True,
        )

        draw_text_with_shadow(
            screen,
            f"Temps : {format_duration(elapsed_seconds)}",
            (card_rect.centerx, info_start_y + line_height * 2),
            self.fonts["body"],
            color=text_color,
            shadow_color=(100, 100, 100),
            shadow_offset=(1, 1),
            centered=True,
        )

        # Score (un peu mis en valeur)
        score_y = info_start_y + line_height * 3 + 15
        draw_outlined_text(
            screen,
            f"Score : {score}",
            (card_rect.centerx, score_y),
            self.fonts["large"],
            color=COLORS["simpson_yellow"],
            outline_color=COLORS["border_black"],
            outline_width=3,
            centered=True,
        )

        # Boutons
        self.btn_retry.draw(screen, self.fonts["body"])
        self.btn_menu.draw(screen, self.fonts["body"])

        # Hint bas d'écran
        draw_outlined_text(
            screen,
            "ASTUCE :  ESC = menu  |  ENTRÉE = rejouer",
            (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 35),
            self.fonts["body"],
            color=COLORS["simpson_yellow"],
            outline_color=COLORS["border_black"],
            outline_width=3,
            centered=True,
        )
