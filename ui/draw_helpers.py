"""Fonctions de dessin et etat visuel"""

import pygame
import math
import os
from settings import PATHS, FONT_NAME, MAX_ERRORS_NORMAL
from ui.layout import SIZES, POSITIONS, ANCHORS

#--------------------------------------VisualState--------------------------------------#

class VisualState:
    """Etat visuel global - modifie ces variables pour changer l'affichage"""

    # Etat du personnage (0=Happy, 1=Angry, 2=Sad, 3=Dead)
    current_mood = 0

    # Nombre d'erreurs (0-6 normal, 0-4 difficile)
    errors = 0

    # Vies max selon difficulte
    max_errors = MAX_ERRORS_NORMAL

    # Indices restants (0-3)
    hints_remaining = 3

    # Mot masque affiche ("_ A _ _ E")
    word_display = ""

    # Lettres jouees
    guessed_letters = []  # Lettres correctes (jaune)
    wrong_letters = []    # Lettres fausses (rouge)

    # Nom du joueur actuel
    current_player_name = ""

    # Timer affiche ("01:23")
    timer_text = "00:00"

    # Difficulte ("normal" ou "difficile")
    difficulty = "normal"

    # Toast message
    _toast_message = ""
    _toast_end_time = 0

#--------------------------------------Fonctions utilitaires--------------------------------------#

def update_mood_from_errors(errors: int, max_errors: int):
    """Met a jour current_mood selon les erreurs"""
    remaining = max_errors - errors
    if remaining > max_errors * 0.6:
        VisualState.current_mood = 0  # Happy
    elif remaining > max_errors * 0.3:
        VisualState.current_mood = 1  # Angry
    elif remaining > 0:
        VisualState.current_mood = 2  # Sad
    else:
        VisualState.current_mood = 3  # Dead

def show_toast(message: str, duration: float = 1.5):
    """Affiche un message temporaire (toast)"""
    VisualState._toast_message = message
    VisualState._toast_end_time = pygame.time.get_ticks() + int(duration * 1000)

def get_toast():
    """Retourne le toast actif ou None"""
    if pygame.time.get_ticks() < VisualState._toast_end_time:
        return VisualState._toast_message
    return None

#--------------------------------------Chargement des ressources--------------------------------------#

_textures = None
_fonts = {}
_angles = {
    "arm_left": 0,
    "arm_right": 0,
    "leg_left": 0,
    "leg_right": 0,
    "head": 0,
    "body": 0,
}

def load_font(size: int):
    """Charge la police Simpson a la taille donnee"""
    if size not in _fonts:
        font_path = os.path.join(PATHS["fonts"], FONT_NAME)
        try:
            _fonts[size] = pygame.font.Font(font_path, size)
        except:
            _fonts[size] = pygame.font.Font(None, size)
    return _fonts[size]

def load_textures():
    """Charge toutes les textures du jeu"""
    global _textures

    if _textures is not None:
        return _textures

    base = PATHS["images"]

    _textures = {
        "head": [
            pygame.transform.scale(pygame.image.load(os.path.join(base, "Trump/Head/Happy.png")).convert_alpha(), SIZES["head"]),
            pygame.transform.scale(pygame.image.load(os.path.join(base, "Trump/Head/Angry.png")).convert_alpha(), SIZES["head"]),
            pygame.transform.scale(pygame.image.load(os.path.join(base, "Trump/Head/Sad.png")).convert_alpha(), SIZES["head"]),
            pygame.transform.scale(pygame.image.load(os.path.join(base, "Trump/Head/Dead.png")).convert_alpha(), SIZES["head"]),
        ],
        "pendu": [
            pygame.transform.scale(pygame.image.load(os.path.join(base, "Pendu/Wood.png")).convert_alpha(), SIZES["pendu"]),
            pygame.transform.scale(pygame.image.load(os.path.join(base, "Pendu/Metal.png")).convert_alpha(), SIZES["pendu"]),
        ],
        "hearth": [
            pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Health/Full.png")).convert_alpha(), SIZES["hearth"]),
            pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Health/Empty.png")).convert_alpha(), SIZES["hearth"]),
        ],
        "hint": [
            pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Hint/New.png")).convert_alpha(), SIZES["hint"]),
            pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Hint/Used.png")).convert_alpha(), SIZES["hint"]),
        ],
        "button": {
            "normal": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Button/normal.png")).convert_alpha(), SIZES["large_button"]),
            "difficile": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Button/difficile.png")).convert_alpha(), SIZES["large_button"]),
            "leader": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Button/Leader.png")).convert_alpha(), SIZES["large_button"]),
            "solution": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Button/Solution.png")).convert_alpha(), SIZES["compact_button"]),
            "1joueur": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Button/1joueur.png")).convert_alpha(), SIZES["large_button"]),
            "2joueurs": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Button/2joueurs.png")).convert_alpha(), SIZES["large_button"]),
            "3joueurs": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Button/3joueurs.png")).convert_alpha(), SIZES["large_button"]),
            "quitter": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Button/quitter.png")).convert_alpha(), SIZES["compact_button"]),
            "ajouter": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Button/ajouter.png")).convert_alpha(), SIZES["compact_button"]),
            "retour": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Button/retour.png")).convert_alpha(), SIZES["compact_button"]),
            "rejouer": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Button/rejouer.png")).convert_alpha(), SIZES["compact_button"]),
            "menu": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Button/menu.png")).convert_alpha(), SIZES["compact_button"]),
        },
        "frame": {
            "leader": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Frame/Leader.png")).convert_alpha(), SIZES["leader"]),
            "chat": pygame.transform.scale(pygame.image.load(os.path.join(base, "Gui/Frame/Chat.png")).convert_alpha(), SIZES["chat"]),
        },
        "body": pygame.transform.scale(pygame.image.load(os.path.join(base, "Trump/Body.png")).convert_alpha(), SIZES["body"]),
        "arm_left": pygame.transform.scale(pygame.image.load(os.path.join(base, "Trump/Arm-L.png")).convert_alpha(), SIZES["arm_left"]),
        "arm_right": pygame.transform.scale(pygame.image.load(os.path.join(base, "Trump/Arm-R.png")).convert_alpha(), SIZES["arm_right"]),
        "leg_left": pygame.transform.scale(pygame.image.load(os.path.join(base, "Trump/Limb-L.png")).convert_alpha(), SIZES["leg_left"]),
        "leg_right": pygame.transform.scale(pygame.image.load(os.path.join(base, "Trump/Limb-R.png")).convert_alpha(), SIZES["leg_right"]),
    }

    return _textures

def get_textures():
    """Retourne les textures (charge si necessaire)"""
    return load_textures()

#--------------------------------------Animations--------------------------------------#

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
    3: {  # Dead
        "arm_left": {"speed": 1, "amplitude": 0, "offset": 0},
        "arm_right": {"speed": 1, "amplitude": 0, "offset": 0},
        "leg_left": {"speed": 1, "amplitude": 0, "offset": 0},
        "leg_right": {"speed": 1, "amplitude": 0, "offset": 0},
        "head": {"speed": 1, "amplitude": 0, "offset": 0},
        "body": {"speed": 1, "amplitude": 0, "offset": 0},
    },
}

def update_animations():
    """Met a jour les angles d'animation"""
    t = pygame.time.get_ticks()
    state_anim = ANIMATIONS[VisualState.current_mood]

    for part in ["arm_left", "arm_right", "leg_left", "leg_right", "head", "body"]:
        anim = state_anim[part]
        speed = anim["speed"]
        amplitude = anim["amplitude"]
        offset = anim.get("offset", 0)
        _angles[part] = math.sin(t / speed) * amplitude + offset

#--------------------------------------Fonctions de dessin--------------------------------------#

def rotate_at(surface, angle, anchor):
    """Rotation d'une surface autour d'un point d'ancrage"""
    rotated = pygame.transform.rotate(surface, angle)
    rect = rotated.get_rect(center=anchor)
    return rotated, rect.topleft

def get_visible_parts(errors: int, difficulty: str):
    """
    Retourne les parties du corps visibles selon les erreurs
    Normal (6 erreurs): tete, corps, bras_g, bras_d, jambe_g, jambe_d
    Difficile (4 erreurs): tete, corps, 2_bras, 2_jambes
    """
    parts = {
        "head": False,
        "body": False,
        "arm_left": False,
        "arm_right": False,
        "leg_left": False,
        "leg_right": False,
    }

    if difficulty == "normal":
        # 6 etapes
        if errors >= 1: parts["head"] = True
        if errors >= 2: parts["body"] = True
        if errors >= 3: parts["arm_left"] = True
        if errors >= 4: parts["arm_right"] = True
        if errors >= 5: parts["leg_left"] = True
        if errors >= 6: parts["leg_right"] = True
    else:
        # 4 etapes (difficile)
        if errors >= 1: parts["head"] = True
        if errors >= 2: parts["body"] = True
        if errors >= 3:
            parts["arm_left"] = True
            parts["arm_right"] = True
        if errors >= 4:
            parts["leg_left"] = True
            parts["leg_right"] = True

    return parts

def draw_character(screen, show_all=False):
    """Dessine le personnage anime (membres selon erreurs)"""
    textures = get_textures()
    update_animations()

    # Pendu (Wood pour normal, Metal pour difficile)
    if VisualState.difficulty == "normal":
        screen.blit(textures["pendu"][0], POSITIONS["pendu"])  # Wood
    else:
        screen.blit(textures["pendu"][1], POSITIONS["pendu"])  # Metal

    # Quelles parties sont visibles?
    if show_all:
        visible = {k: True for k in ["head", "body", "arm_left", "arm_right", "leg_left", "leg_right"]}
    else:
        visible = get_visible_parts(VisualState.errors, VisualState.difficulty)

    # Calculer les rotations
    arm_l, pos_arm_l = rotate_at(textures["arm_left"], _angles["arm_left"], ANCHORS["arm_left"])
    arm_r, pos_arm_r = rotate_at(textures["arm_right"], _angles["arm_right"], ANCHORS["arm_right"])
    leg_l, pos_leg_l = rotate_at(textures["leg_left"], _angles["leg_left"], ANCHORS["leg_left"])
    leg_r, pos_leg_r = rotate_at(textures["leg_right"], _angles["leg_right"], ANCHORS["leg_right"])
    head, pos_head = rotate_at(textures["head"][VisualState.current_mood], _angles["head"], ANCHORS["head"])
    body, pos_body = rotate_at(textures["body"], _angles["body"], ANCHORS["body"])

    # Dessiner dans l'ordre (z-index) - seulement les parties visibles
    if visible["leg_right"]: screen.blit(leg_r, pos_leg_r)
    if visible["leg_left"]: screen.blit(leg_l, pos_leg_l)
    if visible["arm_right"]: screen.blit(arm_r, pos_arm_r)
    if visible["body"]: screen.blit(body, pos_body)
    if visible["arm_left"]: screen.blit(arm_l, pos_arm_l)
    if visible["head"]: screen.blit(head, pos_head)

def draw_hearts(screen):
    """Dessine les coeurs de vie"""
    textures = get_textures()
    lives = VisualState.max_errors - VisualState.errors

    screen.blit(textures["hearth"][0 if lives >= 1 else 1], POSITIONS["hearth1"])
    screen.blit(textures["hearth"][0 if lives >= 2 else 1], POSITIONS["hearth2"])
    screen.blit(textures["hearth"][0 if lives >= 3 else 1], POSITIONS["hearth3"])
    screen.blit(textures["hearth"][0 if lives >= 4 else 1], POSITIONS["hearth4"])

    if VisualState.max_errors >= 5:
        screen.blit(textures["hearth"][0 if lives >= 5 else 1], POSITIONS["hearth5"])
    if VisualState.max_errors >= 6:
        screen.blit(textures["hearth"][0 if lives >= 6 else 1], POSITIONS["hearth6"])

def draw_hints(screen):
    """Dessine les indices"""
    textures = get_textures()
    hints = VisualState.hints_remaining

    screen.blit(textures["hint"][0 if hints >= 1 else 1], POSITIONS["hint1"])
    screen.blit(textures["hint"][0 if hints >= 2 else 1], POSITIONS["hint2"])
    screen.blit(textures["hint"][0 if hints >= 3 else 1], POSITIONS["hint3"])

def draw_text_centered(screen, text: str, pos: tuple, font_size: int = 24,
                        color: tuple = (255, 255, 255)):
    """Dessine du texte centre avec police Simpson"""
    font = load_font(font_size)
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=pos)
    screen.blit(surface, rect)

def draw_text(screen, text: str, pos: tuple, font_size: int = 24,
              color: tuple = (255, 255, 255)):
    """Dessine du texte (coin superieur gauche)"""
    font = load_font(font_size)
    surface = font.render(text, True, color)
    screen.blit(surface, pos)

def draw_alphabet(screen):
    """Dessine l'alphabet a droite (jaune=trouve, rouge=faux, blanc=pas joue)"""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    start_x = 720
    start_y = 100
    col_height = 13  # 13 lettres par colonne

    font = load_font(20)

    for i, letter in enumerate(alphabet):
        col = i // col_height
        row = i % col_height
        x = start_x + col * 35
        y = start_y + row * 28

        # Couleur selon l'etat
        if letter in VisualState.guessed_letters:
            color = (255, 255, 0)  # Jaune - trouve
        elif letter in VisualState.wrong_letters:
            color = (255, 50, 50)  # Rouge - faux
        else:
            color = (200, 200, 200)  # Gris clair - pas joue

        surface = font.render(letter, True, color)
        screen.blit(surface, (x, y))

def draw_chat_frame(screen, text: str = ""):
    """Dessine le cadre de chat avec le texte"""
    textures = get_textures()
    screen.blit(textures["frame"]["chat"], POSITIONS["chat"])

    if text:
        # Centrer le texte dans le chat
        chat_center = (
            POSITIONS["chat"][0] + SIZES["chat"][0] // 2,
            POSITIONS["chat"][1] + SIZES["chat"][1] // 2
        )
        draw_text_centered(screen, text, chat_center, font_size=32)

def draw_timer(screen):
    """Dessine le timer"""
    draw_text(screen, VisualState.timer_text, POSITIONS["timer"], font_size=28)

def draw_player_name(screen):
    """Dessine le nom du joueur"""
    if VisualState.current_player_name:
        draw_text_centered(screen, VisualState.current_player_name, POSITIONS["player_name"],
                          font_size=28, color=(255, 255, 0))

def draw_toast(screen):
    """Dessine le toast si actif"""
    toast = get_toast()
    if toast:
        # Fond semi-transparent
        font = load_font(32)
        surface = font.render(toast, True, (255, 255, 0))
        rect = surface.get_rect(center=(400, 300))

        bg_rect = rect.inflate(20, 10)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect.topleft)
        screen.blit(surface, rect)

def draw_button(screen, button_name: str, pos: tuple):
    """Dessine un bouton texture"""
    textures = get_textures()
    if button_name in textures["button"]:
        screen.blit(textures["button"][button_name], pos)

def draw_game_ui(screen):
    """Dessine tous les elements UI du jeu"""
    draw_character(screen)
    draw_hearts(screen)
    draw_hints(screen)
    draw_timer(screen)
    draw_alphabet(screen)
    draw_chat_frame(screen, VisualState.word_display)
    draw_toast(screen)
