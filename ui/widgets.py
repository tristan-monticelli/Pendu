"""
BUT DU FICHIER
- Regrouper des "petits composants" d'interface (boutons, champs texte, toasts).
- Comme ça, les scènes (menu, game, leaderboard...) restent propres et lisibles.

RÈGLES
- Ce fichier fait UNIQUEMENT de l'UI (pas de logique de jeu).
- Les scènes appellent :
    - handle_* pour gérer les events
    - draw_* pour afficher

CONTENU
1) Button
   - make_button
   - handle_button_event
   - draw_button

2) TextInput
   - make_text_input
   - handle_text_input_event
   - draw_text_input

3) ToastManager
   - show_toast
   - update_toasts
   - draw_toasts
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame

from settings import (
    COLOR_TEXT,
    COLOR_MUTED,
    COLOR_BTN,
    COLOR_BTN_HOVER,
    COLOR_BTN_DISABLED,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_INPUT_ACTIVE,
)


"""
BOUTONS
"""

@dataclass
class Button:
    """
    Button = un bouton simple.

    Champs :
    - rect : pygame.Rect (position + taille)
    - label : texte affiché
    - action : fonction appelée quand on clique
    - enabled : si False => bouton grisé, pas cliquable
    - hovered : True si la souris est dessus (pour effet visuel)
    """
    rect: pygame.Rect
    label: str
    action: Callable[[], None]
    enabled: bool = True
    hovered: bool = False


def make_button(rect: pygame.Rect, label: str, action: Callable[[], None], enabled: bool = True) -> Button:
    """
    Fabrique un bouton (petit helper pour garder les scènes simples).
    """
    return Button(rect=rect, label=label, action=action, enabled=enabled, hovered=False)


def handle_button_event(button: Button, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> bool:
    """
    Gère l'hover + le clic sur un bouton.

    Retour :
    - True si un clic valide a déclenché l'action
    - False sinon

    Étapes :
    1) hovered = souris dans rect
    2) si clic gauche ET hovered ET enabled => appeler action()
    """
    button.hovered = button.rect.collidepoint(mouse_pos)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if button.hovered and button.enabled:
            button.action()
            return True

    return False


def draw_button(screen: pygame.Surface, button: Button, fonts: Dict[str, Any]) -> None:
    """
    Dessine le bouton.

    Couleurs :
    - disabled => gris
    - hover => un peu plus clair
    - normal => couleur standard
    """
    # Choix couleur de fond selon état
    if not button.enabled:
        bg = COLOR_BTN_DISABLED
    elif button.hovered:
        bg = COLOR_BTN_HOVER
    else:
        bg = COLOR_BTN

    # Rectangle du bouton
    pygame.draw.rect(screen, bg, button.rect, border_radius=10)

    # Texte centré
    font = fonts["body"]
    text_surface = font.render(button.label, True, COLOR_TEXT)
    text_rect = text_surface.get_rect(center=button.rect.center)
    screen.blit(text_surface, text_rect)


"""
# 2) CHAMP TEXTE (TextInput)
"""

@dataclass
class TextInput:
    """
    TextInput = champ texte minimal.

    Champs :
    - rect : zone du champ
    - text : texte tapé par l'utilisateur
    - focused : True si le champ a le focus (on tape dedans)
    - placeholder : texte affiché si text est vide
    - max_len : limite de caractères
    - validation_message : message affichable (ex: "Pseudo trop long")
    """
    rect: pygame.Rect
    placeholder: str
    max_len: int
    text: str = ""
    focused: bool = False
    validation_message: str = ""


def make_text_input(rect: pygame.Rect, placeholder: str, max_len: int) -> TextInput:
    """
    Fabrique un champ texte.
    """
    return TextInput(rect=rect, placeholder=placeholder, max_len=max_len)


def handle_text_input_event(input_field: TextInput, event: pygame.event.Event) -> Dict[str, bool]:
    """
    Gère focus + clavier pour un TextInput.

    Retour :
    - {"changed": bool, "submitted": bool}

    Règles :
    - Clic dans le champ => focused True
    - Clic ailleurs => focused False
    - Si focused :
        - BACKSPACE => supprime 1 caractère
        - ENTER => submitted True
        - sinon => ajoute event.unicode si possible

    Important :
    - On n'ajoute que des caractères "tapables" (event.unicode non vide).
    """
    result = {"changed": False, "submitted": False}

    # A) Focus avec la souris
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if input_field.rect.collidepoint(event.pos):
            input_field.focused = True
        else:
            input_field.focused = False

    # Si pas focus, on ne fait rien côté clavier
    if not input_field.focused:
        return result

    # B) Clavier
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_BACKSPACE:
            if input_field.text:
                input_field.text = input_field.text[:-1]
                result["changed"] = True

        elif event.key == pygame.K_RETURN:
            result["submitted"] = True

        else:
            ch = event.unicode
            # event.unicode peut être "" pour SHIFT, CTRL, etc.
            if isinstance(ch, str) and ch != "":
                if len(input_field.text) < input_field.max_len:
                    input_field.text += ch
                    result["changed"] = True

    return result


def draw_text_input(screen: pygame.Surface, input_field: TextInput, fonts: Dict[str, Any]) -> None:
    """
    Dessine un champ texte + son message de validation.

    Affichage :
    - rectangle + bordure
    - placeholder si text vide
    - texte sinon
    - validation_message sous le champ si non vide
    """
    # Fond
    pygame.draw.rect(screen, COLOR_INPUT_BG, input_field.rect, border_radius=10)

    # Bordure : plus claire si focus
    border_color = COLOR_INPUT_ACTIVE if input_field.focused else COLOR_INPUT_BORDER
    pygame.draw.rect(screen, border_color, input_field.rect, width=2, border_radius=10)

    # Texte ou placeholder
    font = fonts["body"]
    if input_field.text:
        txt = input_field.text
        color = COLOR_TEXT
    else:
        txt = input_field.placeholder
        color = COLOR_MUTED

    text_surface = font.render(txt, True, color)
    # petit padding à gauche
    text_pos = (input_field.rect.x + 14, input_field.rect.y + (input_field.rect.height - text_surface.get_height()) // 2)
    screen.blit(text_surface, text_pos)

    # Message de validation (si présent)
    if input_field.validation_message:
        small = fonts.get("small", fonts["body"])
        msg_surface = small.render(input_field.validation_message, True, COLOR_MUTED)
        msg_pos = (input_field.rect.x + 6, input_field.rect.y + input_field.rect.height + 8)
        screen.blit(msg_surface, msg_pos)


"""
TOASTS (petits messages temporaires)
"""

class ToastManager:
    """
    ToastManager stocke une liste de messages temporaires.

    Un toast = {"message": str, "remaining": float}
    - remaining diminue avec dt
    - quand remaining <= 0 => toast supprimé
    """

    def __init__(self) -> None:
        self.toasts: List[Dict[str, Any]] = []


def show_toast(toast_manager: ToastManager, message: str, duration: float = 1.5) -> None:
    """
    Ajoute un toast.

    Exemple :
    show_toast(runtime_state["toast_manager"], "Pseudo validé", 1.2)
    """
    toast_manager.toasts.append({"message": str(message), "remaining": float(duration)})


def update_toasts(toast_manager: ToastManager, dt: float) -> None:
    """
    Met à jour les toasts (durée).

    Étapes :
    1) décrémenter remaining
    2) supprimer ceux <= 0
    """
    if dt < 0:
        dt = 0.0

    for t in toast_manager.toasts:
        t["remaining"] -= dt

    toast_manager.toasts = [t for t in toast_manager.toasts if t["remaining"] > 0]


def draw_toasts(screen: pygame.Surface, toast_manager: ToastManager, fonts: Dict[str, Any]) -> None:
    """
    Dessine les toasts en bas de l'écran (pile verticale).

    Règle simple :
    - On affiche les derniers messages, du bas vers le haut.
    - Chaque toast est un petit rectangle avec le texte.
    """
    if not toast_manager.toasts:
        return

    font = fonts.get("small", fonts["body"])

    screen_w = screen.get_width()
    screen_h = screen.get_height()

    padding = 12
    gap = 8
    toast_h = 34
    max_toasts = 4  # évite d'envahir l'écran

    # On prend seulement les derniers toasts
    to_show = toast_manager.toasts[-max_toasts:]

    for i, t in enumerate(reversed(to_show)):
        msg = str(t.get("message", ""))

        text_surface = font.render(msg, True, COLOR_TEXT)
        text_w = text_surface.get_width()

        # Largeur du toast = texte + padding
        w = min(screen_w - 2 * padding, text_w + 2 * padding)
        x = (screen_w - w) // 2

        # Position verticale (bas de l'écran)
        y = screen_h - padding - toast_h - i * (toast_h + gap)

        rect = pygame.Rect(x, y, w, toast_h)

        # Fond toast (on réutilise la couleur bouton pour rester cohérent)
        pygame.draw.rect(screen, COLOR_BTN, rect, border_radius=10)

        # Texte centré
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
