"""
main.py

Point d'entrée principal du jeu.
Structure refactorisée avec une classe Game pour éviter les if/else imbriqués.
"""
import pygame
import random
import sys
import json
import traceback
from constants import *
from interface import Interface
import score as score_module

def load_words():
    words = []
    try:
        with open(WORD_FILE, "r", encoding="utf-8") as f:
            words = json.load(f)
            words = [str(w).upper() for w in words]
    except FileNotFoundError:
        print(f"Erreur: {WORD_FILE} introuvable.")
    except json.JSONDecodeError:
        print(f"Erreur: {WORD_FILE} est corrompu.")
    except Exception as e:
        print(f"Erreur inattendue chargement mots: {e}")
    return words

def add_word_to_file(word):
    if not word:
        return False
    try:
        try:
           words = load_words()
        except:
            words = []
        
        new_word = word.upper().strip()
        if new_word and new_word not in words:
            words.append(new_word)
            with open(WORD_FILE, "w", encoding="utf-8") as f:
                json.dump(words, f, indent=4)
            return True
        else:
            return False 
    except Exception as e:
        print(f"Erreur ajout mot: {e}")
        return False

# États du jeu / Game States (Enum-like)
class State:
    MENU = 0
    DIFFICULTY_SELECT = 1
    NB_PLAYERS_INPUT = 2
    PLAYER_NAME_INPUT = 3
    WAIT_NEXT_PLAYER = 4
    GAME = 5
    SCORES = 6
    ADD_WORD = 7

class Game:
    def __init__(self):
        try:
            self.interface = Interface()
        except Exception as e:
            print(f"Erreur initialisation interface: {e}")
            sys.exit(1)
            
        self.running = True
        self.clock = pygame.time.Clock()
        self.current_state = State.MENU
        
        # Multiplayer Data
        self.nb_players = 1
        self.players_list = []
        self.current_player_index = 0
        
        # Game Session Data
        self.available_words = []
        self.target_word = ""
        self.guessed_letters = set()
        self.lives = MAX_LIVES
        self.time_limit = 60
        self.start_time_ticks = 0
        
        # Inputs
        self.input_text = ""
        self.input_message = ""
        
        # Mapping dispatch tables
        self.event_handlers = {
            State.MENU: self.handle_menu_events,
            State.DIFFICULTY_SELECT: self.handle_difficulty_events,
            State.NB_PLAYERS_INPUT: self.handle_nb_players_events,
            State.PLAYER_NAME_INPUT: self.handle_name_input_events,
            State.WAIT_NEXT_PLAYER: self.handle_wait_events,
            State.GAME: self.handle_game_events,
            State.SCORES: self.handle_scores_events,
            State.ADD_WORD: self.handle_add_word_events
        }
        
        self.draw_handlers = {
            State.MENU: self.draw_menu,
            State.DIFFICULTY_SELECT: self.draw_difficulty,
            State.NB_PLAYERS_INPUT: self.draw_nb_players,
            State.PLAYER_NAME_INPUT: self.draw_name_input,
            State.WAIT_NEXT_PLAYER: self.draw_wait,
            State.GAME: self.draw_game,
            State.SCORES: self.draw_scores,
            State.ADD_WORD: self.draw_add_word
        }

    def run(self):
        while self.running:
            try:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
            except Exception as e:
                print(f"Erreur critique dans la boucle: {e}")
                traceback.print_exc()
                self.current_state = State.MENU
                
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # Dispatch to specific handler
            handler = self.event_handlers.get(self.current_state)
            if handler:
                handler(event)

    def update(self):
        if self.current_state == State.GAME:
            self.update_game_logic()

    def draw(self):
        handler = self.draw_handlers.get(self.current_state)
        if handler:
            handler()

    # --- Event Handlers ---

    def handle_menu_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.current_state = State.DIFFICULTY_SELECT
            elif event.key == pygame.K_2:
                self.current_state = State.ADD_WORD
                self.input_text = ""
                self.input_message = ""
            elif event.key == pygame.K_3:
                self.current_state = State.SCORES
            elif event.key == pygame.K_4:
                self.running = False

    def handle_difficulty_events(self, event):
        if event.type == pygame.KEYDOWN:
            self.available_words = load_words()
            if not self.available_words:
                print("Aucun mot disponible.")
                self.current_state = State.MENU
                return

            if event.key == pygame.K_1:
                self.time_limit = DIFFICULTY["NORMAL"]
                self.transition_to_nb_players()
            elif event.key == pygame.K_2:
                self.time_limit = DIFFICULTY["HARD"]
                self.transition_to_nb_players()
            elif event.key == pygame.K_ESCAPE:
                self.current_state = State.MENU

    def transition_to_nb_players(self):
        self.current_state = State.NB_PLAYERS_INPUT
        self.input_text = ""

    def handle_nb_players_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_text.isdigit() and int(self.input_text) > 0:
                    self.nb_players = int(self.input_text)
                    self.players_list = []
                    self.current_state = State.PLAYER_NAME_INPUT
                    self.input_text = ""
                else:
                    self.input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.current_state = State.MENU
            elif event.unicode.isdigit():
                self.input_text += event.unicode

    def handle_name_input_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_text.strip():
                    self.players_list.append(self.input_text.strip())
                    self.input_text = ""
                    if len(self.players_list) == self.nb_players:
                        self.current_player_index = 0
                        self.current_state = State.WAIT_NEXT_PLAYER
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode

    def handle_wait_events(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self.start_new_game_round()

    def start_new_game_round(self):
        self.target_word = random.choice(self.available_words)
        self.guessed_letters = set()
        self.lives = MAX_LIVES
        self.start_time_ticks = pygame.time.get_ticks()
        self.current_state = State.GAME

    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.current_state = State.MENU
            else:
                letter = event.unicode.upper()
                if letter.isalpha() and letter not in self.guessed_letters:
                    self.guessed_letters.add(letter)
                    if letter not in self.target_word:
                        self.lives -= 1

    def handle_scores_events(self, event):
        if event.type == pygame.KEYDOWN:
            self.current_state = State.MENU

    def handle_add_word_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.current_state = State.MENU
            elif event.key == pygame.K_RETURN:
                if add_word_to_file(self.input_text):
                    self.input_message = "Mot ajouté !"
                    self.input_text = ""
                else:
                    self.input_message = "Erreur (existant ?)"
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode

    # --- Logic ---
    
    def update_game_logic(self):
        elapsed_seconds = (pygame.time.get_ticks() - self.start_time_ticks) / 1000
        time_left = max(0, self.time_limit - elapsed_seconds)
        
        game_over = False
        won = False
        
        if time_left <= 0:
            game_over = True
            won = False
        elif self.lives <= 0:
            game_over = True
            won = False
        elif all(l in self.guessed_letters for l in self.target_word):
            game_over = True
            won = True
            
        if game_over:
            # Calculate precise elapsed time for both win and loss
            final_time = self.time_limit - time_left
            score_module.save_score(self.players_list[self.current_player_index], final_time, won)
            
            self.current_player_index += 1
            if self.current_player_index < self.nb_players:
                self.current_state = State.WAIT_NEXT_PLAYER
            else:
                self.current_state = State.SCORES

    # --- Drawers ---

    def draw_menu(self):
        self.interface.draw_menu()

    def draw_difficulty(self):
        self.interface.draw_difficulty_menu()

    def draw_nb_players(self):
        self.interface.draw_nb_players_input(self.input_text)

    def draw_name_input(self):
        current_num = len(self.players_list) + 1
        self.interface.draw_player_name_input(current_num, self.input_text)

    def draw_wait(self):
        self.interface.draw_next_player_wait(self.players_list[self.current_player_index])

    def draw_game(self):
        elapsed = (pygame.time.get_ticks() - self.start_time_ticks) / 1000
        time_left = max(0, self.time_limit - elapsed)
        
        word_display = "".join([l if l in self.guessed_letters else "_" for l in self.target_word])
        wrong_letters = [l for l in self.guessed_letters if l not in self.target_word]
        curr_name = self.players_list[self.current_player_index]
        
        self.interface.draw_game(word_display, self.lives, curr_name, wrong_letters, time_left)

    def draw_scores(self):
        scores = score_module.get_top_scores()
        self.interface.draw_scores(scores)

    def draw_add_word(self):
        self.interface.draw_add_word(self.input_text, self.input_message)

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
