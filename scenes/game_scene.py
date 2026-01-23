"""
BUT DE LA SCÈNE
- Gérer une partie de pendu (interface + appels à la logique).
- Afficher :
    - pseudo
    - difficulté
    - temps de partie
    - mot masqué
    - lettres fausses
    - erreurs restantes (max 7)
    - message de feedback
    - indice (uniquement en FACILE)

NOUVEAU
- La difficulté est modifiable pendant le jeu (touche TAB)
- Les mots viennent de mots.txt avec un format :
  FACILE;mot;indice / MOYEN;mot / DIFFICILE;mot

TUTORIEL
- Si show_tutorial=True (pseudo nouveau), on affiche un overlay
- IMPORTANT : le jeu ne doit PAS réagir tant que le tuto n'est pas fermé
"""

from __future__ import annotations

import random
import pygame

from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WORDS_PATH, BTN_W, BTN_H, DIFFICULTIES, DEFAULT_DIFFICULTY

from core.words_io import load_words_by_difficulty
from core.game_state import start_game_from_word, apply_guess, build_masked_word
from core.input_normalize import normalize_letter_input
from core.time_tracker import start_session_timer, get_elapsed_seconds, stop_session_timer
from core.scoring import set_difficulty, compute_score

from ui.draw_helpers import clear_screen, draw_title, draw_text_lines, draw_hint_bottom, format_duration
from ui.widgets import make_button, handle_button_event, draw_button, show_toast


class GameScene:
    """
    Scène de jeu : pendu en cours.
    """

    def __init__(self, manager, shared, runtime_state, payload):
        self.manager = manager
        self.shared = shared
        self.runtime_state = runtime_state
        self.payload = payload

        self.fonts = self.shared["fonts"]

        self.difficulty = DEFAULT_DIFFICULTY

        # CONSIGNE : 7 erreurs max (fixe)
        self.max_errors = 7

        self.state = None

        self.start_ticks = 0
        self.feedback_line = ""

        # Indice (uniquement utile en FACILE)
        self.current_hint = ""

        self.btn_menu = None

        # Tutoriel sur nouveau joueur
        self.show_tutorial = False
        self.tutorial_closed = False

    def on_enter(self):
        """
        Démarrage d'une partie.

        Étapes :
        1) vérifier pseudo
        2) récupérer difficulté
        3) charger un mot selon difficulté
        4) démarrer GameState + timer
        5) créer bouton menu
        6) initialiser le tutoriel si besoin
        """
        pseudo = self.runtime_state.get("active_pseudo")
        if not pseudo:
            show_toast(self.runtime_state["toast_manager"], "Entrer un pseudo avant de jouer", 2.0)
            self.manager.go_to("menu")
            return

        diff = self.payload.get("difficulty", DEFAULT_DIFFICULTY)
        diff = (diff or "").strip().upper()
        if diff not in DIFFICULTIES:
            diff = DEFAULT_DIFFICULTY
        self.difficulty = diff

        # 7 erreurs max (consigne)
        self.max_errors = set_difficulty(self.difficulty)

        # Démarrer une partie selon difficulté
        ok = self._start_new_game()
        if not ok:
            self.manager.go_to("menu")
            return

        rect = pygame.Rect(WINDOW_WIDTH - BTN_W - 40, WINDOW_HEIGHT - BTN_H - 30, BTN_W, BTN_H)

        def action_menu():
            show_toast(self.runtime_state["toast_manager"], "Partie quittée", 1.2)
            self.manager.go_to("menu")

        self.btn_menu = make_button(rect, "Menu", action_menu)
        self.feedback_line = "Deviner une lettre au clavier (TAB = changer difficulté)"

        # Tutoriel si pseudo nouveau (envoyé par le menu)
        self.show_tutorial = bool(self.payload.get("show_tutorial", False))
        self.tutorial_closed = False

        # IMPORTANT :
        # Si le tutoriel est affiché, on veut que le temps "ne démarre pas vraiment".
        # Donc on remet le timer à 0 ici, et on le relancera quand le tuto sera fermé.
        if self.show_tutorial and not self.tutorial_closed:
            self.start_ticks = start_session_timer(lambda: 0)  # valeur neutre (on reset au vrai tick après)

    def _start_new_game(self) -> bool:
        """
        Démarre une nouvelle partie avec la difficulté actuelle.

        Retour :
        - True si ok
        - False si aucun mot disponible
        """
        words, hints = load_words_by_difficulty(WORDS_PATH, self.difficulty)
        if not words:
            show_toast(self.runtime_state["toast_manager"], f"Aucun mot en {self.difficulty}", 2.0)
            return False

        secret_word = random.choice(words)

        # Indice uniquement en FACILE (si présent)
        if self.difficulty == "FACILE":
            self.current_hint = hints.get(secret_word, "")
        else:
            self.current_hint = ""

        self.state = start_game_from_word(secret_word, self.max_errors)

        # Timer normal : démarre maintenant (sauf si on affiche un tuto, on reset après)
        self.start_ticks = start_session_timer(pygame.time.get_ticks)

        return True

    def _cycle_difficulty(self):
        """
        Change la difficulté pendant le jeu (TAB) et relance une nouvelle partie.
        """
        if self.difficulty not in DIFFICULTIES:
            self.difficulty = DEFAULT_DIFFICULTY

        idx = DIFFICULTIES.index(self.difficulty)
        idx = (idx + 1) % len(DIFFICULTIES)
        self.difficulty = DIFFICULTIES[idx]

        # max_errors reste 7 (consigne)
        self.max_errors = set_difficulty(self.difficulty)

        ok = self._start_new_game()
        if ok:
            self.feedback_line = f"Difficulté changée : {self.difficulty}"
        else:
            self.manager.go_to("menu")

    def handle_event(self, event):
        """
        Events :
        - TUTORIEL (prioritaire) : fermer le tuto
        - ESC : retour menu
        - TAB : changer difficulté + nouvelle partie
        - lettre : tentative
        """
        if self.state is None:
            return

        # ---------------------------------------------------------
        # PRIORITÉ : tutoriel
        # Tant que le tuto n'est pas fermé, le jeu ne doit PAS réagir.
        # On écoute seulement la fermeture (ENTREE / ESPACE / ECHAP).
        # ---------------------------------------------------------
        if self.show_tutorial and not self.tutorial_closed:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                    self.tutorial_closed = True

                    # On démarre le timer "pour de vrai" au moment où le tuto se ferme
                    self.start_ticks = start_session_timer(pygame.time.get_ticks)

                    # Message simple
                    self.feedback_line = "Tutoriel fermé : bonne chance !"
            return

        # Ensuite seulement : le jeu normal

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.btn_menu.action()
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self._cycle_difficulty()
            return

        mouse_pos = pygame.mouse.get_pos()
        handle_button_event(self.btn_menu, event, mouse_pos)

        letter = normalize_letter_input(event)
        if letter is None:
            return

        self.state, guess_result = apply_guess(self.state, letter)
        self.feedback_line = guess_result.message

        if self.state.status in ("won", "lost"):
            elapsed_s = stop_session_timer(self.start_ticks, pygame.time.get_ticks)
            score = compute_score(self.state, self.difficulty, elapsed_s)

            payload = {
                "status": self.state.status,
                "score": score,
                "elapsed_seconds": elapsed_s,
                "difficulty": self.difficulty,
                "secret_word": self.state.secret_word,
                "wrong_letters": sorted(list(self.state.wrong_letters)),
            }
            self.manager.go_to("game_over", payload=payload)

    def update(self, dt):
        return

    def draw(self, screen):
        if self.state is None:
            return

        clear_screen(screen)
        draw_title(screen, self.fonts, "PARTIE")

        # Si tuto affiché : on affiche le temps à 00:00 (puisque la partie n'a pas commencé)
        if self.show_tutorial and not self.tutorial_closed:
            elapsed_s = 0
        else:
            elapsed_s = get_elapsed_seconds(self.start_ticks, pygame.time.get_ticks)

        pseudo = self.runtime_state.get("active_pseudo", "—")
        wrong_count = len(self.state.wrong_letters)
        remaining = max(0, self.state.max_errors - wrong_count)

        info_lines = [
            f"Pseudo : {pseudo}",
            f"Difficulté : {self.difficulty}",
            f"Temps : {format_duration(elapsed_s)}",
        ]
        draw_text_lines(screen, self.fonts, info_lines, x=60, y=120, small=True)

        # Indice en FACILE
        if self.difficulty == "FACILE" and self.current_hint:
            draw_text_lines(screen, self.fonts, [f"Indice : {self.current_hint}"], x=60, y=190, small=True)

        masked = build_masked_word(self.state.secret_word, self.state.guessed_letters)
        draw_text_lines(screen, self.fonts, ["Mot :", masked], x=60, y=240, small=False)

        wrong_letters = sorted(list(self.state.wrong_letters))
        wrong_str = ", ".join(wrong_letters) if wrong_letters else "Aucune"

        stats_lines = [
            f"Lettres fausses : {wrong_str}",
            f"Erreurs restantes : {remaining} / {self.state.max_errors}",
        ]
        draw_text_lines(screen, self.fonts, stats_lines, x=60, y=360, small=False)

        if self.feedback_line:
            draw_text_lines(screen, self.fonts, [f"Info : {self.feedback_line}"], x=60, y=460, small=True)

        draw_button(screen, self.btn_menu, self.fonts)
        draw_hint_bottom(screen, self.fonts, "Lettre | TAB = difficulté | ESC = menu")

        # Overlay tutoriel (par-dessus tout)
        if self.show_tutorial and not self.tutorial_closed:
            self._draw_tutorial_overlay(screen)

    def _draw_tutorial_overlay(self, screen):
        """
        Affiche une fenêtre de tutoriel par-dessus la scène.
        - pas d'image, pas d'animation compliquée
        - texte simple + consignes
        """
        # Fond semi-transparent
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Fenêtre centrale
        box_w, box_h = 720, 360
        box_x = (WINDOW_WIDTH - box_w) // 2
        box_y = (WINDOW_HEIGHT - box_h) // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

        pygame.draw.rect(screen, (40, 40, 40), box_rect, border_radius=12)
        pygame.draw.rect(screen, (120, 120, 120), box_rect, 2, border_radius=12)

        lines = [
            "TUTORIEL - COMMENT JOUER",
            "",
            "- Taper une lettre au clavier pour proposer",
            "- 7 erreurs maximum (peu importe la difficulte)",
            "- FACILE : un indice est affiche",
            "- TAB : changer de difficulte et relancer une nouvelle partie",
            "- ESC : retour menu (apres le tuto)",
            "",
            "Appuyer sur ENTREE / ESPACE / ECHAP pour fermer",
        ]

        # Affichage simple (réutilise votre helper)
        from ui.draw_helpers import draw_text_lines
        draw_text_lines(screen, self.fonts, lines, box_x + 30, box_y + 30, small=True)
