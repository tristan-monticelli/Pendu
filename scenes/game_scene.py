"""
Scène de jeu - Version Simpson refonte complète
Garde toutes les fonctionnalités de la branche feat/noemie avec le nouveau design
"""

from __future__ import annotations

import pygame
import random
import math

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WORDS_PATH,
    COLORS,
    DIFFICULTIES,
    DEFAULT_DIFFICULTY,
    MAX_HINTS,
    BUTTON_SIZES,
    MARGIN_SCREEN,
    GAP_ELEMENTS,
)

from core.words_io import load_words_by_difficulty
from core.game_state import start_game_from_word, apply_guess, build_masked_word
from core.input_normalize import normalize_letter_input
from core.time_tracker import start_session_timer, get_elapsed_seconds, stop_session_timer
from core.scoring import set_difficulty, compute_score

from ui.simpson_theme import (
    draw_simpson_background,
    draw_cartoon_card,
    draw_text_with_shadow,
    draw_outlined_text,
)

from ui.simpson_components import (
    SimpsonButton,
    AlphabetGrid,
    LifeIndicator,
    HintIndicator,
    WordDisplay,
    show_toast,
)


class GameScene:
    """
    Scène principale du jeu
    
    Fonctionnalités complètes :
    - Difficulté FACILE/MOYEN/DIFFICILE avec indices en FACILE
    - 7 erreurs max (consigne)
    - Changement de difficulté avec TAB (relance partie)
    - Tutoriel pour nouveaux joueurs
    - Animation Trump selon l'état
    - Classement multi-joueurs
    """
    
    def __init__(self, manager, shared, runtime_state, payload):
        """
        Initialise la scène
        
        Args:
            manager: SceneManager
            shared: Ressources partagées (fonts, assets)
            runtime_state: État global
            payload: Données passées par la scène précédente
        """
        self.manager = manager
        self.shared = shared
        self.runtime_state = runtime_state
        self.payload = payload
        
        self.fonts = self.shared["fonts"]
        self.assets = self.shared["assets"]
        
        # État du jeu
        self.difficulty = DEFAULT_DIFFICULTY
        self.max_errors = 7  # Consigne : toujours 7
        self.state = None
        
        # Timer
        self.start_ticks = 0
        
        # ✅ Indices textuels (liste de 3 indices max)
        self.hint_list = []  # Liste des 3 indices pour le mot
        self.hints_used = 0  # Nombre d'indices déjà affichés
        self.current_displayed_hint = ""  # Indice actuellement affiché
        
        # Feedback
        self.feedback_line = ""
        
        # UI Components
        self.btn_menu = None
        self.btn_hint = None
        self.alphabet_grid = None
        self.life_indicator = None
        self.hint_indicator = None
        self.word_display = None
        
        # Tutoriel
        self.show_tutorial = False
        self.tutorial_closed = False
        
        # Animation Trump
        self.trump_mood = 0  # 0=happy, 1=angry, 2=sad, 3=dead
        self.trump_anim_time = 0
        
        # Positions calculées (définies dans on_enter)
        self.layout_positions = {}
    
    def on_enter(self):
        """
        Appelé lors de l'entrée dans la scène
        Initialise une nouvelle partie
        """
        # Vérification pseudo
        pseudo = self.runtime_state.get("active_pseudo")
        if not pseudo:
            show_toast(self.runtime_state["toast_manager"], "Entrer un pseudo avant de jouer", 2.0)
            self.manager.go_to("menu")
            return
        
        # Récupération de la difficulté
        diff = self.payload.get("difficulty", DEFAULT_DIFFICULTY)
        diff = (diff or "").strip().upper()
        if diff not in DIFFICULTIES:
            diff = DEFAULT_DIFFICULTY
        self.difficulty = diff
        
        # 7 erreurs max (consigne)
        self.max_errors = set_difficulty(self.difficulty)
        
        # Démarrage d'une partie
        ok = self._start_new_game()
        if not ok:
            self.manager.go_to("menu")
            return
        
        # Tutoriel si nouveau joueur
        self.show_tutorial = bool(self.payload.get("show_tutorial", False))
        self.tutorial_closed = False
        
        # Timer (sera démarré après fermeture du tuto)
        if self.show_tutorial and not self.tutorial_closed:
            self.start_ticks = start_session_timer(lambda: 0)
        else:
            self.start_ticks = start_session_timer(pygame.time.get_ticks)
        
        # Calcul du layout
        self._calculate_layout()
        
        # Création des composants UI
        self._create_ui_components()
        
        # Feedback initial
        self.feedback_line = "Trouve une lettre ! (TAB = changer difficulté)"
    
    def _start_new_game(self) -> bool:
        """
        Démarre une nouvelle partie avec la difficulté actuelle
        
        Returns:
            True si succès, False si aucun mot disponible
        """
        words, hints = load_words_by_difficulty(WORDS_PATH, self.difficulty)
        if not words:
            show_toast(self.runtime_state["toast_manager"], f"Aucun mot en {self.difficulty}", 2.0)
            return False
        
        secret_word = random.choice(words)
        
        # ✅ Charger les 3 indices textuels pour le mot (toutes difficultés)
        self.hint_list = hints.get(secret_word, [])
        self.hints_used = 0
        self.current_displayed_hint = ""
        
        # Initialisation de l'état
        self.state = start_game_from_word(secret_word, self.max_errors)
        
        # Reset compteurs
        self.trump_mood = 0
        
        # Reset timer
        self.start_ticks = start_session_timer(pygame.time.get_ticks)
        
        return True
    
    def _calculate_layout(self):
        """
        Calcule toutes les positions des éléments
        Responsive selon la taille d'écran
        """
        w = WINDOW_WIDTH
        h = WINDOW_HEIGHT
        margin = MARGIN_SCREEN
        
        # Header (bandeau haut)
        header_height = int(h * 0.10)
        
        # ✅ Zone de jeu principale (réduite pour laisser de l'espace)
        game_area_top = header_height + margin + 10  # +10 pour espace avec header
        game_area_height = int(h * 0.65)  # Réduit de 0.70 à 0.65
        game_area_bottom = game_area_top + game_area_height
        
        # ✅ Footer (plus d'espace)
        footer_top = game_area_bottom + 20  # Espace entre card et bouton
        
        # ✅ Colonnes avec gap entre les deux cards
        card_gap = 20  # Espace entre les deux cards
        pendu_width = int((w - 2 * margin - card_gap) * 0.48)
        info_x = margin + pendu_width + card_gap
        info_width = w - info_x - margin
        
        self.layout_positions = {
            # Header
            "header_y": margin,
            "header_height": header_height,
            
            # Pendu + Trump (gauche)
            "pendu_x": margin,
            "pendu_y": game_area_top,
            "pendu_width": pendu_width,
            "pendu_height": game_area_height,
            
            # Infos (droite)
            "info_x": info_x,
            "info_y": game_area_top,
            "info_width": info_width,
            "info_height": game_area_height,
            
            # Footer
            "footer_y": footer_top,
            "footer_height": h - footer_top - margin,
        }
    
    def _create_ui_components(self):
        """
        Crée tous les composants UI
        """
        pos = self.layout_positions
        
        # ✅ Bouton Menu (centré entre la card et le bas de l'écran)
        btn_w, btn_h = BUTTON_SIZES["normal"]
        
        # Calcul pour centrer verticalement dans l'espace disponible
        space_available = WINDOW_HEIGHT - pos["footer_y"] - MARGIN_SCREEN
        btn_y = pos["footer_y"] + (space_available - btn_h) // 2
        
        btn_menu_rect = pygame.Rect(
            MARGIN_SCREEN,
            btn_y,
            btn_w,
            btn_h
        )
        
        def action_menu():
            # ✅ Stopper les sons Trump avant de quitter
            self._stop_all_trump_sounds()
            show_toast(self.runtime_state["toast_manager"], "Partie quittée", 1.2)
            self.manager.go_to("menu")
        
        # ✅ Bouton MENU - Jaune pâle (DA)
        self.btn_menu = SimpsonButton(
            rect=btn_menu_rect,
            text="MENU",
            action=action_menu,
            color=COLORS["btn_yellow_pale"],
        )
        
        # ✅ Bouton Indice (disponible pour TOUTES les difficultés)
        btn_hint_rect = pygame.Rect(
            btn_menu_rect.right + 30,
            btn_y,  # Même hauteur que MENU
            btn_w,
            btn_h
        )
        
        def action_hint():
            self._use_hint()
        
        # Vérifier si des indices sont disponibles pour ce mot
        has_hints = len(self.hint_list) > 0
        
        # Bouton INDICE - Rose pâle (DA)
        self.btn_hint = SimpsonButton(
            rect=btn_hint_rect,
            text="INDICE",
            action=action_hint,
            color=COLORS["btn_pink_pale"],
            enabled=(has_hints and self.hints_used < len(self.hint_list)),
        )
        
        # Grille alphabet (dans la zone info, en haut)
        alphabet_x = pos["info_x"] + 50
        alphabet_y = pos["info_y"] + 200
        self.alphabet_grid = AlphabetGrid(
            pos=(alphabet_x, alphabet_y),
            letter_size=70,  # Augmenté
            spacing=12,      # Augmenté
        )
        
        # Indicateur de vies (en haut à gauche de la card pendu)
        life_x = pos["pendu_x"] + 20
        life_y = pos["pendu_y"] + 15
        self.life_indicator = LifeIndicator(
            pos=(life_x, life_y),
            max_lives=self.max_errors,
            heart_full_img=self.assets.get("heart_full"),
            heart_empty_img=self.assets.get("heart_empty"),
        )
        self.life_indicator.set_lives(self.max_errors)
        
        # ✅ Indicateur d'indices (disponible pour TOUTES les difficultés)
        # Position à droite dans la card pendu
        hint_x = pos["pendu_x"] + pos["pendu_width"] - 190
        hint_y = life_y  # Même ligne que les cœurs
        self.hint_indicator = HintIndicator(
            pos=(hint_x, hint_y),
            max_hints=MAX_HINTS,
            hint_available_img=self.assets.get("hint_available"),
            hint_used_img=self.assets.get("hint_used"),
        )
        self.hint_indicator.set_hints(min(MAX_HINTS, len(self.hint_list)))
        
        # Affichage du mot (centré verticalement dans la zone sous l'alphabet)
        word_display_y = pos["info_y"] + pos["info_height"] - 80  # ✅ Remonté un peu
        word_display_x = pos["info_x"] + pos["info_width"] // 2
        self.word_display = WordDisplay(
            pos=(word_display_x, word_display_y),
            letter_spacing=8,  # ✅ Réduit car on a maintenant des cases
        )
        
        # Mise à jour du mot masqué
        masked = build_masked_word(self.state.secret_word, self.state.guessed_letters)
        self.word_display.set_word(masked)
    
    def _cycle_difficulty(self):
        """
        Change la difficulté (TAB) et relance une nouvelle partie
        """
        # ✅ Stopper les sons avant de relancer
        self._stop_all_trump_sounds()
        
        if self.difficulty not in DIFFICULTIES:
            self.difficulty = DEFAULT_DIFFICULTY
        
        idx = DIFFICULTIES.index(self.difficulty)
        idx = (idx + 1) % len(DIFFICULTIES)
        self.difficulty = DIFFICULTIES[idx]
        
        # Max errors reste 7 (consigne)
        self.max_errors = set_difficulty(self.difficulty)
        
        ok = self._start_new_game()
        if ok:
            # Recréation des composants UI
            self._create_ui_components()
            self.feedback_line = f"Mode : {self.difficulty}"
        else:
            self.manager.go_to("menu")
    
    def _use_hint(self):
        """
        Utilise un indice textuel (affiche l'indice suivant)
        Les indices sont affichés dans l'ordre : indice1, puis indice2, puis indice3
        Chaque clic remplace l'indice précédent
        """
        if self.hints_used >= MAX_HINTS:
            show_toast(self.runtime_state["toast_manager"], "Plus d'indices !", 1.0)
            return
        
        # Vérifier qu'on a des indices disponibles
        if not self.hint_list or self.hints_used >= len(self.hint_list):
            show_toast(self.runtime_state["toast_manager"], "Pas d'indice disponible", 1.0)
            return
        
        # ✅ Récupérer l'indice suivant
        hint_text = self.hint_list[self.hints_used]
        # Remplacer les underscores par des espaces pour l'affichage
        hint_display = hint_text.replace("_", " ")
        
        # ✅ Afficher l'indice (remplace le précédent)
        self.current_displayed_hint = hint_display
        
        self.hints_used += 1
        if self.hint_indicator:
            self.hint_indicator.set_hints(MAX_HINTS - self.hints_used)
        
        if self.btn_hint:
            self.btn_hint.enabled = (self.hints_used < MAX_HINTS and self.hints_used < len(self.hint_list))
        
        # Toast pour confirmer
        show_toast(self.runtime_state["toast_manager"], f"Indice {self.hints_used}/3", 1.0)
    
    def _process_letter(self, letter: str):
        """
        Traite une tentative de lettre
        
        Args:
            letter: Lettre normalisée (minuscule, sans accent)
        """
        self.state, guess_result = apply_guess(self.state, letter)
        
        # Feedback
        self.feedback_line = guess_result.message
        
        # Mise à jour de l'alphabet
        if guess_result.kind == "good":
            self.alphabet_grid.set_letter_state(letter.upper(), "correct")
        elif guess_result.kind == "bad":
            self.alphabet_grid.set_letter_state(letter.upper(), "wrong")
            
            # Mise à jour des vies
            remaining = self.max_errors - len(self.state.wrong_letters)
            self.life_indicator.set_lives(remaining)
            
            # Mise à jour du mood Trump
            self._update_trump_mood()
        
        # Mise à jour du mot masqué
        masked = build_masked_word(self.state.secret_word, self.state.guessed_letters)
        self.word_display.set_word(masked)
        
        # Note: La vérification de fin de partie est faite dans update()
    
    def _update_trump_mood(self):
        """
        Met à jour l'humeur de Trump selon les erreurs
        Joue un son quand l'humeur change
        """
        errors = len(self.state.wrong_letters)
        remaining = self.max_errors - errors
        
        # Sauvegarder l'ancien mood pour détecter les changements
        old_mood = self.trump_mood
        
        if remaining > self.max_errors * 0.6:
            self.trump_mood = 0  # Happy
        elif remaining > self.max_errors * 0.3:
            self.trump_mood = 1  # Angry
        elif remaining > 0:
            self.trump_mood = 2  # Sad
        else:
            self.trump_mood = 3  # Dead
        
        # ✅ Jouer un son si l'humeur a changé
        if self.trump_mood != old_mood:
            self._play_mood_sound(self.trump_mood)
    
    def _play_mood_sound(self, mood: int):
        """
        Joue le son correspondant à l'humeur de Trump EN BOUCLE
        Stoppe le son précédent avant d'en jouer un nouveau
        
        Args:
            mood: 0=Happy, 1=Angry, 2=Sad, 3=Dead
        """
        sounds = self.shared.get("sounds", {})
        
        sound_map = {
            1: "trump_angry",  # Angry
            2: "trump_sad",    # Sad
            3: "trump_dead",   # Dead
        }
        
        # ✅ Stopper TOUS les sons Trump avant d'en jouer un nouveau
        self._stop_all_trump_sounds()
        
        # ✅ Jouer le nouveau son EN BOUCLE (-1 = infini)
        sound_name = sound_map.get(mood)
        if sound_name and sounds.get(sound_name):
            sounds[sound_name].play(loops=-1)  # ✅ Boucle infinie
    
    def _stop_all_trump_sounds(self):
        """
        Stoppe tous les sons Trump (utilisé lors des transitions)
        """
        sounds = self.shared.get("sounds", {})
        for sound_name in ["trump_angry", "trump_sad", "trump_dead"]:
            if sounds.get(sound_name):
                sounds[sound_name].stop()
    
    def handle_event(self, event):
        """
        Gestion des événements
        
        Args:
            event: Événement pygame
        """
        if self.state is None:
            return
        
        # PRIORITÉ : Tutoriel
        if self.show_tutorial and not self.tutorial_closed:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                    self.tutorial_closed = True
                    self.start_ticks = start_session_timer(pygame.time.get_ticks)
                    self.feedback_line = "Tutoriel fermé : bonne chance !"
            return
        
        # ESC : retour menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.btn_menu.action()
            return
        
        # TAB : changer difficulté
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self._cycle_difficulty()
            return
        
        # Position souris
        mouse_pos = pygame.mouse.get_pos()
        
        # Boutons
        self.btn_menu.handle_event(event, mouse_pos)
        if self.btn_hint:
            self.btn_hint.handle_event(event, mouse_pos)
        
        # Alphabet grid (uniquement hover, pas de clic)
        self.alphabet_grid.handle_event(event, mouse_pos)
        
        # Clavier physique (lettre)
        letter = normalize_letter_input(event)
        if letter:
            self._process_letter(letter)
    
    def update(self, dt):
        """
        Mise à jour de la scène
        
        Args:
            dt: Delta time en secondes
        """
        # Animation Trump (balancement)
        self.trump_anim_time += dt
        
        # ✅ Vérification fin de partie avec délai
        if self.state and self.state.status in ("won", "lost"):
            # Initialiser le timer si pas encore fait
            if not hasattr(self, '_end_timer'):
                self._end_timer = pygame.time.get_ticks()
                
                # Mettre à jour le mood et feedback
                if self.state.status == "lost":
                    self.trump_mood = 3  # Dead
                    self.feedback_line = "GAME OVER !"
                else:
                    self.trump_mood = 0  # Happy
                    self.feedback_line = "BRAVO !"
                return
            
            # Vérifier si le délai est écoulé (2 secondes)
            elapsed = pygame.time.get_ticks() - self._end_timer
            if elapsed < 2000:
                return  # On attend encore
            
            # ✅ Transition vers game_over
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
            
            # Reset le timer pour la prochaine partie
            if hasattr(self, '_end_timer'):
                del self._end_timer
            
            # ✅ Stopper les sons Trump avant de quitter
            self._stop_all_trump_sounds()
            
            self.manager.go_to("game_over", payload=payload)
    
    def draw(self, screen):
        """
        Dessin de la scène
        
        Args:
            screen: Surface pygame
        """
        if self.state is None:
            return
        
        # Fond Simpson (ciel + herbe)
        from ui.simpson_theme import draw_simpson_background
        draw_simpson_background(screen)
        
        # Header
        self._draw_header(screen)
        
        # Zone pendu (gauche)
        self._draw_pendu_zone(screen)
        
        # Zone infos (droite)
        self._draw_info_zone(screen)
        
        # Footer (boutons + feedback)
        self._draw_footer(screen)
        
        # Overlay tutoriel (par-dessus tout)
        if self.show_tutorial and not self.tutorial_closed:
            self._draw_tutorial_overlay(screen)
    
    def _draw_header(self, screen):
        """Dessine le header (infos de partie)"""
        pos = self.layout_positions
        
        # Card header
        header_rect = pygame.Rect(
            MARGIN_SCREEN,
            pos["header_y"],
            WINDOW_WIDTH - 2 * MARGIN_SCREEN,
            pos["header_height"]
        )
        
        draw_cartoon_card(
            screen,
            header_rect,
            bg_color=COLORS["simpson_yellow"],
        )
        
        # Informations
        pseudo = self.runtime_state.get("active_pseudo", "—")
        
        if self.show_tutorial and not self.tutorial_closed:
            elapsed_s = 0
        else:
            elapsed_s = get_elapsed_seconds(self.start_ticks, pygame.time.get_ticks)
        
        mm = elapsed_s // 60
        ss = elapsed_s % 60
        time_str = f"{mm:02d}:{ss:02d}"
        
        # Texte header
        header_text = f"Joueur : {pseudo}    |    Timer : {time_str}    |    Difficulté : {self.difficulty}"
        
        draw_text_with_shadow(
            screen,
            header_text,
            (header_rect.centerx, header_rect.centery),
            self.fonts["large"],
            color=COLORS["text_black"],
            shadow_color=COLORS["text_white"],
            shadow_offset=(2, 2),
            centered=True,
        )
    
    def _draw_pendu_zone(self, screen):
        """Dessine la zone pendu + Trump + vies"""
        pos = self.layout_positions
        
        # Card pendu
        pendu_rect = pygame.Rect(
            pos["pendu_x"],
            pos["pendu_y"],
            pos["pendu_width"],
            pos["pendu_height"]
        )
        
        draw_cartoon_card(
            screen,
            pendu_rect,
            bg_color=COLORS["bg_card"],
        )
        
        # ✅ Potence (pendu) - remontée un peu
        if "pendu_wood" in self.assets:
            pendu_img = self.assets["pendu_wood"]
            # Position : centrée horizontalement, remontée de 60px du bas
            pendu_img_rect = pendu_img.get_rect(
                midbottom=(pendu_rect.centerx, pendu_rect.bottom - 60)
            )
            screen.blit(pendu_img, pendu_img_rect)
        
        # Trump (animé)
        self._draw_trump(screen, pendu_rect)
        
        # Indicateur de vies
        if self.life_indicator:
            self.life_indicator.draw(screen)
        
        # Indicateur d'indices (toutes difficultés)
        if self.hint_indicator:
            self.hint_indicator.draw(screen)
    
    def _draw_trump(self, screen, pendu_rect):
        """
        Dessine Trump avec animation basée sur le système de origin/visuel
        Utilise des rotations avec points d'ancrage pour un rendu naturel
        
        Args:
            screen: Surface pygame
            pendu_rect: Rectangle de la zone pendu (pour positionnement)
        """
        # ============================================================
        # CONFIGURATION ANIMATIONS (basé sur origin/visuel)
        # ============================================================
        ANIMATIONS = {
            0: {  # Happy
                "arm_left": {"speed": 500, "amplitude": 15},
                "arm_right": {"speed": 500, "amplitude": -15},
                "leg_left": {"speed": 600, "amplitude": 5},
                "leg_right": {"speed": 600, "amplitude": -5},
                "head": {"speed": 800, "amplitude": 3},
                "body": {"speed": 600, "amplitude": 2},
            },
            1: {  # Angry
                "arm_left": {"speed": 100, "amplitude": 25},
                "arm_right": {"speed": 100, "amplitude": -25},
                "leg_left": {"speed": 150, "amplitude": 3},
                "leg_right": {"speed": 150, "amplitude": -3},
                "head": {"speed": 50, "amplitude": 5},
                "body": {"speed": 80, "amplitude": 2},
            },
            2: {  # Sad
                "arm_left": {"speed": 2000, "amplitude": 5},
                "arm_right": {"speed": 2000, "amplitude": 5},
                "leg_left": {"speed": 2500, "amplitude": 2},
                "leg_right": {"speed": 2500, "amplitude": 2},
                "head": {"speed": 3000, "amplitude": 10},
                "body": {"speed": 2500, "amplitude": 3},
            },
            3: {  # Dead - pas d'animation
                "arm_left": {"speed": 1, "amplitude": 0},
                "arm_right": {"speed": 1, "amplitude": 0},
                "leg_left": {"speed": 1, "amplitude": 0},
                "leg_right": {"speed": 1, "amplitude": 0},
                "head": {"speed": 1, "amplitude": 0},
                "body": {"speed": 1, "amplitude": 0},
            },
        }
        
        # ============================================================
        # POSITIONS RELATIVES (basées sur origin/visuel layout.py)
        # Le personnage est construit autour d'un point central (corps)
        # ============================================================
        
        # Point de base : centre du corps aligné avec la corde
        base_x = pendu_rect.centerx + 58  # ✅ Aligné avec la corde de la potence
        base_y = pendu_rect.centery + 50  # Centré verticalement
        
        # Offsets relatifs au corps (basés sur les ANCHORS de origin/visuel)
        OFFSETS = {
            "head": (0, -90),         # Au-dessus du corps
            "body": (0, 0),           # Centre de référence
            "arm_left": (-48, -40),   # Épaule gauche
            "arm_right": (48, -40),   # Épaule droite
            "leg_left": (-25, 70),    # Hanche gauche
            "leg_right": (25, 70),    # Hanche droite
        }
        
        # Récupérer le mood actuel
        mood = self.trump_mood
        anim = ANIMATIONS.get(mood, ANIMATIONS[0])
        
        # Temps en millisecondes pour les animations
        t = pygame.time.get_ticks()
        
        # Calculer les angles de rotation pour chaque partie
        def calc_angle(part_name):
            """Calcule l'angle de rotation pour une partie du corps"""
            part_anim = anim.get(part_name, {"speed": 1000, "amplitude": 0})
            speed = part_anim["speed"]
            amplitude = part_anim["amplitude"]
            return math.sin(t / speed) * amplitude
        
        angles = {
            "head": calc_angle("head"),
            "body": calc_angle("body"),
            "arm_left": calc_angle("arm_left"),
            "arm_right": calc_angle("arm_right"),
            "leg_left": calc_angle("leg_left"),
            "leg_right": calc_angle("leg_right"),
        }
        
        # Nombre d'erreurs pour afficher les parties du corps
        errors = len(self.state.wrong_letters)
        
        # ============================================================
        # FONCTION DE DESSIN AVEC ROTATION
        # ============================================================
        def rotate_and_draw(asset_key, part_name):
            """Dessine une partie du corps avec rotation"""
            if asset_key not in self.assets:
                return
            
            surface = self.assets[asset_key]
            angle = angles.get(part_name, 0)
            offset = OFFSETS.get(part_name, (0, 0))
            
            # Position finale
            pos_x = base_x + offset[0]
            pos_y = base_y + offset[1]
            
            # Rotation
            rotated = pygame.transform.rotate(surface, angle)
            rect = rotated.get_rect(center=(pos_x, pos_y))
            screen.blit(rotated, rect)
        
        # ============================================================
        # DESSIN DES PARTIES (ordre z-index : arrière vers avant)
        # ============================================================
        
        # 1) Jambes (derrière) - 5 et 6 erreurs
        if errors >= 6:
            rotate_and_draw("trump_leg_right", "leg_right")
        if errors >= 5:
            rotate_and_draw("trump_leg_left", "leg_left")
        
        # 2) Bras droit (derrière le corps) - 4 erreurs
        if errors >= 4:
            rotate_and_draw("trump_arm_right", "arm_right")
        
        # 3) Corps - 2 erreurs
        if errors >= 2:
            rotate_and_draw("trump_body", "body")
        
        # 4) Bras gauche (devant le corps) - 3 erreurs
        if errors >= 3:
            rotate_and_draw("trump_arm_left", "arm_left")
        
        # 5) Tête (toujours devant) - 1 erreur
        if errors >= 1:
            mood_names = ["happy", "angry", "sad", "dead"]
            trump_head_key = f"trump_{mood_names[mood]}"
            rotate_and_draw(trump_head_key, "head")
    
    def _draw_trump_body_parts(self, screen, head_center, errors):
        """
        OBSOLÈTE - Les parties sont maintenant dessinées dans _draw_trump
        Gardé pour compatibilité mais ne fait rien
        """
        pass
    
    def _draw_info_zone(self, screen):
        """Dessine la zone d'infos (mot + alphabet)"""
        pos = self.layout_positions
        
        # Card infos
        info_rect = pygame.Rect(
            pos["info_x"],
            pos["info_y"],
            pos["info_width"],
            pos["info_height"]
        )
        
        draw_cartoon_card(
            screen,
            info_rect,
            bg_color=COLORS["bg_card"],
            title="Mot à trouver",
            title_font=self.fonts["body"],
        )
        
        # ✅ Afficher l'indice textuel actuel (si on a cliqué sur INDICE)
        if self.current_displayed_hint:
            hint_y = pos["info_y"] + 100
            hint_text = f"Indice : {self.current_displayed_hint}"
            draw_text_with_shadow(
                screen,
                hint_text,
                (info_rect.centerx, hint_y),
                self.fonts["body"],             # Taille réduite pour indices longs
                color=COLORS["text_indice"],    # Violet foncé (WCAG AA)
                shadow_color=(0, 0, 0),         # Ombre noire
                shadow_offset=(2, 2),
                centered=True,
            )
        
        # Alphabet grid
        if self.alphabet_grid:
            self.alphabet_grid.draw(screen, self.fonts["body"])
        
        # Mot masqué
        if self.word_display:
            self.word_display.draw(screen, self.fonts["title"])  # ✅ title au lieu de huge
    
    def _draw_footer(self, screen):
        """Dessine le footer (boutons + feedback)"""
        # Boutons
        self.btn_menu.draw(screen, self.fonts["body"])
        if self.btn_hint:
            self.btn_hint.draw(screen, self.fonts["body"])
        
        # ✅ Feedback message (bulle) - centrée horizontalement et verticalement
        if self.feedback_line:
            # Calcul pour centrer la bulle verticalement
            footer_y = self.layout_positions["footer_y"]
            space_available = WINDOW_HEIGHT - footer_y - MARGIN_SCREEN
            feedback_y = footer_y + (space_available // 2) - 25
            
            from ui.simpson_theme import draw_speech_bubble
            
            # ✅ Bulle plus large pour les messages longs
            bubble_max_width = 500
            bubble_x = (WINDOW_WIDTH - bubble_max_width) // 2
            
            draw_speech_bubble(
                screen,
                self.feedback_line,
                (bubble_x, feedback_y),
                self.fonts["body"],
                max_width=bubble_max_width,
                tail_direction="bottom",
                bg_color=COLORS["text_white"],
            )
    
    def _draw_tutorial_overlay(self, screen):
        """
        Dessine l'overlay du tutoriel
        Style cohérent avec la DA Simpson
        """
        # Fond semi-transparent noir
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Card tutoriel centrée (même style que les autres cards)
        tuto_width = 800
        tuto_height = 550
        tuto_rect = pygame.Rect(
            (WINDOW_WIDTH - tuto_width) // 2,
            (WINDOW_HEIGHT - tuto_height) // 2,
            tuto_width,
            tuto_height
        )
        
        # Card jaune pâle (comme bg_card)
        draw_cartoon_card(
            screen,
            tuto_rect,
            bg_color=COLORS["bg_card"],
        )
        
        # Titre "COMMENT JOUER" en haut
        title_y = tuto_rect.y + 35
        draw_text_with_shadow(
            screen,
            "COMMENT JOUER",
            (tuto_rect.centerx, title_y),
            self.fonts["large"],
            color=COLORS["text_black"],
            shadow_color=(150, 150, 150),
            shadow_offset=(2, 2),
            centered=True,
        )
        
        # Ligne de séparation
        line_y = title_y + 50
        pygame.draw.line(
            screen,
            COLORS["border_black"],
            (tuto_rect.x + 40, line_y),
            (tuto_rect.right - 40, line_y),
            3
        )
        
        # Section REGLES
        section_y = line_y + 30
        draw_text_with_shadow(
            screen,
            "REGLES",
            (tuto_rect.centerx, section_y),
            self.fonts["body"],
            color=(180, 100, 0),  # Orange foncé lisible
            shadow_color=(100, 100, 100),
            shadow_offset=(1, 1),
            centered=True,
        )
        
        # Règles
        rules = [
            "Tape une lettre au clavier",
            "7 erreurs maximum",
            "FACILE = indice affiche",
        ]
        
        rules_y = section_y + 45
        for rule in rules:
            draw_text_with_shadow(
                screen,
                rule,
                (tuto_rect.centerx, rules_y),
                self.fonts["small"],
                color=COLORS["text_black"],
                shadow_color=(150, 150, 150),
                shadow_offset=(1, 1),
                centered=True,
            )
            rules_y += 35
        
        # Section COMMANDES
        commands_title_y = rules_y + 20
        draw_text_with_shadow(
            screen,
            "COMMANDES",
            (tuto_rect.centerx, commands_title_y),
            self.fonts["body"],
            color=(180, 100, 0),  # Orange foncé lisible
            shadow_color=(100, 100, 100),
            shadow_offset=(1, 1),
            centered=True,
        )
        
        # Commandes
        commands = [
            "TAB = Changer difficulte",
            "ESC = Retour menu",
        ]
        
        commands_y = commands_title_y + 45
        for cmd in commands:
            draw_text_with_shadow(
                screen,
                cmd,
                (tuto_rect.centerx, commands_y),
                self.fonts["small"],
                color=COLORS["text_black"],
                shadow_color=(150, 150, 150),
                shadow_offset=(1, 1),
                centered=True,
            )
            commands_y += 35
        
        # Message final en bas (jaune Simpson avec outline)
        final_y = tuto_rect.bottom - 50
        draw_outlined_text(
            screen,
            "ENTREE pour commencer",
            (tuto_rect.centerx, final_y),
            self.fonts["body"],
            color=COLORS["simpson_yellow"],
            outline_color=COLORS["border_black"],
            outline_width=3,
            centered=True,
        )
