"""
BUT DE LA SCÈNE
- Gérer une partie de pendu (interface + appels à la logique).
- Afficher :
    - pseudo
    - difficulté
    - temps de partie
    - mot masqué
    - lettres fausses
    - erreurs restantes
    - message de feedback (bonne/mauvaise lettre, déjà joué, etc.)

RÈGLES IMPORTANTES
- La logique du jeu (victoire/défaite + gestion lettres) est dans game_state.py
- Le score est calculé dans scoring.py
- Le temps est géré avec time_tracker.py
- L'entrée clavier est normalisée avec input_normalize.py
- Les mots viennent de words_io.py (data/mots.txt)

NAVIGATION
- ESC : retour menu (abandon simple)
- Quand victoire ou défaite : aller sur "game_over" avec un payload

PAYLOAD ATTENDU EN ENTRÉE
- payload["difficulty"] : "FACILE" / "MOYEN" / "DIFFICILE" (sinon MOYEN)
"""

from __future__ import annotations

import pygame

from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WORDS_PATH, BTN_W, BTN_H

from core.words_io import load_words
from core.game_state import start_game, apply_guess, build_masked_word
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
        """
        Constructeur.

        Paramètres :
        - manager : SceneManager (navigation)
        - shared : ressources partagées (fonts)
        - runtime_state : état global (pseudo, toast_manager, etc.)
        - payload : infos de démarrage (difficulty)
        """
        self.manager = manager
        self.shared = shared
        self.runtime_state = runtime_state
        self.payload = payload

        self.fonts = self.shared["fonts"]

        # Données partie
        self.difficulty = "MOYEN"
        self.max_errors = 6
        self.state = None  # GameState

        # Timer
        self.start_ticks = 0

        # Message à afficher après une tentative (feedback)
        self.feedback_line = ""

        # Bouton abandon (retour menu)
        self.btn_menu = None

    def on_enter(self):
        """
        Appelé à l'entrée de la scène.

        Étapes :
        1) vérifier pseudo (obligatoire)
        2) récupérer difficulté + max_errors
        3) charger les mots
        4) démarrer la partie
        5) démarrer le timer
        6) créer bouton "Menu"
        """
        # 1) Pseudo obligatoire
        pseudo = self.runtime_state.get("active_pseudo")
        if not pseudo:
            show_toast(self.runtime_state["toast_manager"], "Entrer un pseudo avant de jouer", 2.0)
            self.manager.go_to("menu")
            return

        # 2) Difficulté
        diff = self.payload.get("difficulty", "MOYEN")
        if diff not in ("FACILE", "MOYEN", "DIFFICILE"):
            diff = "MOYEN"
        self.difficulty = diff
        self.max_errors = set_difficulty(self.difficulty)

        # 3) Charger mots
        words = load_words(WORDS_PATH)
        if not words:
            # Cas simple : pas de mots => retour menu
            show_toast(self.runtime_state["toast_manager"], "Aucun mot trouvé dans mots.txt", 2.0)
            self.manager.go_to("menu")
            return

        # 4) Démarrer game state
        self.state = start_game(words, self.max_errors)

        # 5) Démarrer timer (ticks pygame)
        self.start_ticks = start_session_timer(pygame.time.get_ticks)

        # 6) Bouton "Menu" (abandon)
        rect = pygame.Rect(WINDOW_WIDTH - BTN_W - 40, WINDOW_HEIGHT - BTN_H - 30, BTN_W, BTN_H)

        def action_menu():
            # Abandon simple : retour menu
            show_toast(self.runtime_state["toast_manager"], "Partie quittée", 1.2)
            self.manager.go_to("menu")

        self.btn_menu = make_button(rect, "Menu", action_menu)

        # Feedback au début
        self.feedback_line = "Deviner une lettre au clavier"

    def handle_event(self, event):
        """
        Gestion des événements Pygame.

        Règles :
        - ESC : abandon -> menu
        - clic bouton Menu : abandon -> menu
        - KEYDOWN lettre : tentative de lettre
        """
        # Sécurité si la scène a été stoppée
        if self.state is None:
            return

        # 1) ESC -> menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.btn_menu.action()
            return

        # 2) Bouton menu
        mouse_pos = pygame.mouse.get_pos()
        handle_button_event(self.btn_menu, event, mouse_pos)

        # 3) Tentative lettre (normalisée)
        letter = normalize_letter_input(event)
        if letter is None:
            return

        # Appliquer la tentative
        self.state, guess_result = apply_guess(self.state, letter)
        self.feedback_line = guess_result.message

        # Si fin de partie -> calcul score + aller sur game_over
        if self.state.status in ("won", "lost"):
            elapsed_s = stop_session_timer(self.start_ticks, pygame.time.get_ticks)
            score = compute_score(self.state, self.difficulty, elapsed_s)

            payload = {
                "status": self.state.status,                # "won" / "lost"
                "score": score,                              # int
                "elapsed_seconds": elapsed_s,               # int
                "difficulty": self.difficulty,              # str
                "secret_word": self.state.secret_word,      # str (utile pour afficher)
                "wrong_letters": sorted(list(self.state.wrong_letters)),
            }
            self.manager.go_to("game_over", payload=payload)

    def update(self, dt):
        """
        Pas d'animation complexe ici.
        (La scène existe quand même pour respecter le contrat.)
        """
        return

    def draw(self, screen):
        """
        Dessin de la scène de jeu.

        Affiche :
        - titre
        - pseudo/difficulté/temps
        - mot masqué
        - lettres fausses + erreurs restantes
        - feedback
        - bouton menu
        """
        if self.state is None:
            return

        clear_screen(screen)
        draw_title(screen, self.fonts, "PARTIE")

        # Temps en cours
        elapsed_s = get_elapsed_seconds(self.start_ticks, pygame.time.get_ticks)

        pseudo = self.runtime_state.get("active_pseudo", "—")
        wrong_count = len(self.state.wrong_letters)
        remaining = max(0, self.state.max_errors - wrong_count)

        # 1) Infos générales
        info_lines = [
            f"Pseudo : {pseudo}",
            f"Difficulté : {self.difficulty}",
            f"Temps : {format_duration(elapsed_s)}",
        ]
        draw_text_lines(screen, self.fonts, info_lines, x=60, y=120, small=True)

        # 2) Mot masqué (affichage plus visible)
        masked = build_masked_word(self.state.secret_word, self.state.guessed_letters)
        # On réutilise draw_text_lines pour rester simple
        draw_text_lines(screen, self.fonts, ["Mot :", masked], x=60, y=200, small=False)

        # 3) Lettres fausses + erreurs restantes
        wrong_letters = sorted(list(self.state.wrong_letters))
        wrong_str = ", ".join(wrong_letters) if wrong_letters else "Aucune"

        stats_lines = [
            f"Lettres fausses : {wrong_str}",
            f"Erreurs restantes : {remaining} / {self.state.max_errors}",
        ]
        draw_text_lines(screen, self.fonts, stats_lines, x=60, y=320, small=False)

        # 4) Feedback (bonne/mauvaise lettre, etc.)
        if self.feedback_line:
            draw_text_lines(screen, self.fonts, [f"Info : {self.feedback_line}"], x=60, y=420, small=True)

        # 5) Bouton Menu
        draw_button(screen, self.btn_menu, self.fonts)

        # 6) Hint bas
        draw_hint_bottom(screen, self.fonts, "Taper une lettre | ESC = menu")
