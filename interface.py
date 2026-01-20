"""
interface.py

Ce module gère l'affichage graphique avec Pygame.
"""
import pygame
from constants import *

class Interface:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Jeu du Pendu")
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

    def draw_text(self, text, font, color, x, y, align="center"):
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if align == "center":
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surface, rect)

    def draw_menu(self):
        self.screen.fill(WHITE)
        self.draw_text("LE PENDU", self.big_font, BLACK, SCREEN_WIDTH // 2, 100)
        self.draw_text("1. Jouer (Play)", self.font, BLACK, SCREEN_WIDTH // 2, 250)
        self.draw_text("2. Insérer un mot (Add Word)", self.font, BLACK, SCREEN_WIDTH // 2, 300)
        self.draw_text("3. Scores", self.font, BLACK, SCREEN_WIDTH // 2, 350)
        self.draw_text("4. Quitter (Quit)", self.font, BLACK, SCREEN_WIDTH // 2, 400)
        pygame.display.flip()

    def draw_difficulty_menu(self):
        self.screen.fill(WHITE)
        self.draw_text("CHOISIR DIFFICULTÉ", self.big_font, BLACK, SCREEN_WIDTH // 2, 100)
        self.draw_text("1. NORMAL (60s)", self.font, GREEN, SCREEN_WIDTH // 2, 250)
        self.draw_text("2. DIFFICILE (30s)", self.font, RED, SCREEN_WIDTH // 2, 350)
        pygame.display.flip()
        
    def draw_nb_players_input(self, current_input):
        self.screen.fill(WHITE)
        self.draw_text("NOMBRE DE JOUEURS", self.big_font, BLACK, SCREEN_WIDTH // 2, 100)
        self.draw_text("Entrez le nombre de joueurs (1-9) :", self.font, BLACK, SCREEN_WIDTH // 2, 250)
        
        pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH//2 - 50, 300, 100, 60), 2)
        self.draw_text(current_input, self.big_font, BLACK, SCREEN_WIDTH // 2, 330)
        
        self.draw_text("Appuyez sur Entrée pour valider", self.font, GRAY, SCREEN_WIDTH // 2, 500)
        pygame.display.flip()

    def draw_player_name_input(self, player_num, current_name):
        self.screen.fill(WHITE)
        self.draw_text(f"NOM DU JOUEUR {player_num}", self.big_font, BLACK, SCREEN_WIDTH // 2, 100)
        
        pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH//2 - 200, 300, 400, 60), 2)
        self.draw_text(current_name, self.font, BLACK, SCREEN_WIDTH // 2, 330)
        
        self.draw_text("Appuyez sur Entrée pour valider", self.font, GRAY, SCREEN_WIDTH // 2, 500)
        pygame.display.flip()
        
    def draw_next_player_wait(self, player_name):
        self.screen.fill(WHITE)
        self.draw_text(f"Au tour de : {player_name}", self.big_font, BLUE, SCREEN_WIDTH // 2, 200)
        self.draw_text("Appuyez sur une touche pour commencer", self.font, BLACK, SCREEN_WIDTH // 2, 400)
        pygame.display.flip()

    def draw_game(self, word_display, lives, player_name, wrong_letters, time_left):
        self.screen.fill(WHITE)
        
        # Afficher le mot caché / Display hidden word
        self.draw_text(word_display, self.big_font, BLACK, SCREEN_WIDTH // 2, 400)
        
        # Afficher les informations / Display info
        self.draw_text(f"Joueur: {player_name}", self.font, BLUE, 150, 50)
        self.draw_text(f"Vies : {lives}", self.font, RED, SCREEN_WIDTH - 150, 50)
        
        # Afficher le temps / Draw Timer
        color_timer = BLACK
        if time_left < 10:
            color_timer = RED
        self.draw_text(f"Temps : {time_left:.1f}s", self.big_font, color_timer, SCREEN_WIDTH // 2, 100)

        # Afficher les lettres incorrectes / Display wrong letters
        wrong_text = "Ratés: " + " ".join(wrong_letters)
        self.draw_text(wrong_text, self.font, RED, SCREEN_WIDTH // 2, 500)

        # Dessiner le pendu / Draw Hangman graphics
        self.draw_hangman(lives)
        
        pygame.display.flip()

    def draw_hangman(self, lives):
        # Logique de dessin du pendu en fonction des vies restantes
        # Max lives = 7
        color = BLACK
        
        # Potence / Gallows
        if lives < 7:
            pygame.draw.line(self.screen, color, (100, 500), (300, 500), 5) # Base
            pygame.draw.line(self.screen, color, (200, 500), (200, 100), 5) # Pole
            pygame.draw.line(self.screen, color, (200, 100), (400, 100), 5) # Top
            pygame.draw.line(self.screen, color, (400, 100), (400, 150), 5) # Rope
            
        # Tête / Head
        if lives < 6:
            pygame.draw.circle(self.screen, color, (400, 180), 30, 3)
            
        # Corps / Body
        if lives < 5:
            pygame.draw.line(self.screen, color, (400, 210), (400, 350), 3)
            
        # Bras Gauche / Left Arm
        if lives < 4:
            pygame.draw.line(self.screen, color, (400, 240), (350, 300), 3)
            
        # Bras Droit / Right Arm
        if lives < 3:
            pygame.draw.line(self.screen, color, (400, 240), (450, 300), 3)
            
        # Jambe Gauche / Left Leg
        if lives < 2:
            pygame.draw.line(self.screen, color, (400, 350), (350, 450), 3)
            
        # Jambe Droite / Right Leg
        if lives < 1:
            pygame.draw.line(self.screen, color, (400, 350), (450, 450), 3)

    def draw_scores(self, scores):
        self.screen.fill(WHITE)
        self.draw_text("TABLEAU DES SCORES", self.big_font, BLACK, SCREEN_WIDTH // 2, 50)
        
        # Header
        self.draw_text("Nom", self.font, BLACK, SCREEN_WIDTH // 2 - 150, 120)
        self.draw_text("Temps/Résultat", self.font, BLACK, SCREEN_WIDTH // 2 + 150, 120)
        pygame.draw.line(self.screen, BLACK, (100, 140), (700, 140), 2)

        y = 160
        for name, result in scores[:10]: # Top 10
            self.draw_text(name, self.font, BLUE, SCREEN_WIDTH // 2 - 150, y)
            
            color = GREEN if "s" in result else RED
            self.draw_text(result, self.font, color, SCREEN_WIDTH // 2 + 150, y)
            
            y += 40
            
        self.draw_text("Appuyez sur une touche pour retourner au menu", self.font, GRAY, SCREEN_WIDTH // 2, 550)
        pygame.display.flip()

    def draw_add_word(self, current_input, message=""):
        self.screen.fill(WHITE)
        self.draw_text("AJOUTER UN MOT", self.big_font, BLACK, SCREEN_WIDTH // 2, 100)
        self.draw_text("Tapez le mot et appuyez sur Entrée:", self.font, BLACK, SCREEN_WIDTH // 2, 200)
        
        # Display input box
        pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH//2 - 200, 280, 400, 50), 2)
        self.draw_text(current_input, self.font, BLACK, SCREEN_WIDTH // 2, 305)
        
        if message:
            self.draw_text(message, self.font, GREEN, SCREEN_WIDTH // 2, 400)
            
        self.draw_text("Appuyez sur ESC pour retourner au menu", self.font, GRAY, SCREEN_WIDTH // 2, 550)
        pygame.display.flip()
