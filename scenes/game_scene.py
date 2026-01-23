"""Scene de jeu principale"""

import pygame
from scene_manager import Scene
from ui.draw_helpers import (
    VisualState, draw_game_ui, draw_button, show_toast, update_mood_from_errors
)
from ui.layout import POSITIONS, SIZES
from core.words_io import load_words
from core.game_state import start_game, apply_guess, build_masked_word, check_end_condition, get_hint
from core.scoring import compute_score
from core.time_tracker import TimeTracker
from core.input_normalize import normalize_letter_input, is_valid_letter_event
from settings import MAX_ERRORS_NORMAL, MAX_ERRORS_HARD, MAX_HINTS

#--------------------------------------GameScene--------------------------------------#

class GameScene(Scene):
    """Ecran de jeu du pendu"""

    def __init__(self, manager):
        super().__init__(manager)
        self.game_state = None
        self.timer = TimeTracker()
        self.hints_used = 0

    def enter(self):
        """Initialise une nouvelle partie"""
        # Recuperer les parametres
        difficulty = self.manager.shared_data["difficulty"]
        player_index = self.manager.shared_data["current_player_index"]
        player_names = self.manager.shared_data["player_names"]
        player_name = player_names[player_index] if player_index < len(player_names) else f"Joueur {player_index + 1}"

        # Charger les mots
        words = load_words()
        if not words:
            show_toast("Aucun mot disponible!", 2.0)
            self.manager.go_to("menu")
            return

        # Demarrer la partie
        max_errors = MAX_ERRORS_NORMAL if difficulty == "normal" else MAX_ERRORS_HARD
        self.game_state = start_game(words, difficulty, player_name)
        self.game_state.max_errors = max_errors

        # Reset UI
        VisualState.current_mood = 0
        VisualState.errors = 0
        VisualState.max_errors = max_errors
        VisualState.hints_remaining = MAX_HINTS
        VisualState.difficulty = difficulty
        VisualState.current_player_name = player_name
        VisualState.guessed_letters = []
        VisualState.wrong_letters = []
        VisualState.word_display = build_masked_word(
            self.game_state.secret_word,
            self.game_state.guessed_letters
        )

        # Timer
        self.timer = TimeTracker()
        self.timer.start()
        self.hints_used = 0

    def handle_events(self, events):
        """Gere les evenements"""
        if not self.game_state or self.game_state.status != "playing":
            return

        for event in events:
            # Clic sur bouton Solution
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._is_click_on_button(event.pos, POSITIONS["button4"], SIZES["compact_button"]):
                    self._use_hint()

            # Clavier physique
            if is_valid_letter_event(event):
                letter = normalize_letter_input(event)
                if letter:
                    self._process_letter(letter)

            # Echap pour quitter
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.go_to("menu")

    def _is_click_on_button(self, click_pos, button_pos, button_size):
        """Verifie si le clic est sur un bouton"""
        rect = pygame.Rect(button_pos, button_size)
        return rect.collidepoint(click_pos)

    def _process_letter(self, letter: str):
        """Traite une lettre jouee"""
        self.game_state, result = apply_guess(self.game_state, letter)

        if result == "already_played":
            show_toast(f"'{letter}' deja jouee!", 1.0)
            return

        if result == "correct":
            show_toast("Bien joue!", 0.8)
            VisualState.guessed_letters = self.game_state.guessed_letters.copy()
        else:
            show_toast("Rate!", 0.8)
            VisualState.wrong_letters = self.game_state.wrong_letters.copy()
            VisualState.errors = len(self.game_state.wrong_letters)

        # Mettre a jour l'affichage
        update_mood_from_errors(VisualState.errors, VisualState.max_errors)
        VisualState.word_display = build_masked_word(
            self.game_state.secret_word,
            self.game_state.guessed_letters
        )

        # Verifier fin de partie
        status = check_end_condition(self.game_state)
        if status != "playing":
            self._end_game(status == "won")

    def _use_hint(self):
        """Utilise un indice"""
        if VisualState.hints_remaining <= 0:
            show_toast("Plus d'indices!", 1.0)
            return

        hint_letter = get_hint(self.game_state)
        if hint_letter:
            VisualState.hints_remaining -= 1
            self.hints_used += 1
            show_toast(f"Indice: {hint_letter}", 1.5)
            self._process_letter(hint_letter)

    def _end_game(self, won: bool):
        """Termine la partie"""
        elapsed = self.timer.stop()
        score = compute_score(self.game_state, elapsed, won)

        # Sauvegarder dans shared_data
        player_index = self.manager.shared_data["current_player_index"]
        self.manager.shared_data["scores"][player_index] = score
        self.manager.shared_data["last_word"] = self.game_state.secret_word
        self.manager.shared_data["last_time"] = elapsed
        self.manager.shared_data["last_won"] = won

        if won:
            show_toast("Victoire!", 2.0)
            VisualState.current_mood = 0
        else:
            show_toast(f"Perdu! Le mot etait: {self.game_state.secret_word}", 3.0)
            VisualState.current_mood = 3

        # Attendre un peu avant de changer de scene
        pygame.time.wait(2000)

        # Passage au joueur suivant ou fin
        self._next_player_or_end()

    def _next_player_or_end(self):
        """Passe au joueur suivant ou termine"""
        current = self.manager.shared_data["current_player_index"]
        num_players = self.manager.shared_data["num_players"]

        if current + 1 < num_players:
            # Joueur suivant
            self.manager.shared_data["current_player_index"] = current + 1
            self.manager.go_to("game")
        else:
            # Fin de la session
            self.manager.go_to("game_over")

    def update(self):
        """Met a jour la scene"""
        if self.game_state and self.game_state.status == "playing":
            VisualState.timer_text = self.timer.get_formatted()

    def draw(self, screen):
        """Dessine la scene de jeu"""
        draw_game_ui(screen)

        # Bouton Solution (indice)
        draw_button(screen, "solution", POSITIONS["button4"])

        # Nom du joueur en haut
        from ui.draw_helpers import draw_text_centered
        draw_text_centered(screen, VisualState.current_player_name, (400, 30),
                          font_size=28, color=(255, 255, 0))
