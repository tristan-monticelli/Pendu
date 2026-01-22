"""
BUT DU FICHIER
- Lancer le jeu Pendu.
- Initialiser Pygame (fenêtre, horloge, polices).
- Charger les données (classement).
- Créer le SceneManager.
- Faire la boucle principale :
    events -> scène
    update -> scène
    draw -> scène

RÈGLES
- Pas de logique de pendu ici (c'est dans game_state.py).
"""

from __future__ import annotations

import pygame

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    FONT_SIZE_TITLE,
    FONT_SIZE_BODY,
    FONT_SIZE_SMALL,
    LEADERBOARD_PATH,
)

from scene_manager import SceneManager
from core.leaderboard_io import load_leaderboard, get_last_player_summary
from ui.widgets import ToastManager, update_toasts, draw_toasts


def init_pygame() -> tuple[pygame.Surface, pygame.time.Clock, dict]:
    """
    Initialise Pygame et retourne :
    - screen : la fenêtre
    - clock : pour gérer les FPS
    - fonts : dictionnaire de polices (title/body/small)
    """
    pygame.init()

    # Création de la fenêtre
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pendu")

    # Horloge pour gérer FPS
    clock = pygame.time.Clock()

    # Polices (on utilise une police par défaut pygame)
    fonts = {
        "title": pygame.font.Font(None, FONT_SIZE_TITLE),
        "body": pygame.font.Font(None, FONT_SIZE_BODY),
        "small": pygame.font.Font(None, FONT_SIZE_SMALL),
    }

    return screen, clock, fonts


def create_runtime_state() -> dict:
    """
    Crée l'état global du programme (partagé entre les scènes).

    Contenu important :
    - active_pseudo : pseudo actuel (None au départ)
    - leaderboard_cache : le classement chargé une fois
    - last_player_summary : résumé du dernier joueur (pour l'afficher dans le menu)
    - toast_manager : pour afficher des petits messages temporaires
    - should_quit : bool pour quitter la boucle principale
    """
    leaderboard = load_leaderboard(LEADERBOARD_PATH)
    last_summary = get_last_player_summary(leaderboard)

    runtime_state = {
        "active_pseudo": None,
        "leaderboard_cache": leaderboard,
        "last_player_summary": last_summary,
        "toast_manager": ToastManager(),
        "should_quit": False,
    }

    return runtime_state


def run_app_loop(screen: pygame.Surface, clock: pygame.time.Clock, manager: SceneManager, runtime_state: dict, fonts: dict) -> None:
    """
    Boucle principale du jeu.

    Étapes répétées :
    1) limiter FPS et récupérer dt
    2) récupérer les events pygame
    3) envoyer les events à la scène
    4) update scène + update toasts
    5) draw scène + draw toasts
    6) pygame.display.flip()
    """
    while runtime_state["should_quit"] is False:
        # dt = durée depuis la dernière frame (en secondes)
        dt_ms = clock.tick(FPS)
        dt = dt_ms / 1000.0

        # 1) Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runtime_state["should_quit"] = True
            else:
                manager.dispatch_event(event)

        # 2) Update
        manager.update_scene(dt)
        update_toasts(runtime_state["toast_manager"], dt)

        # 3) Draw
        manager.draw_scene(screen)
        draw_toasts(screen, runtime_state["toast_manager"], fonts)

        # 4) Afficher la frame
        pygame.display.flip()

    pygame.quit()


def main() -> None:
    """
    Point d'entrée du programme.

    Étapes :
    1) init_pygame
    2) create_runtime_state
    3) créer shared (fonts)
    4) créer SceneManager
    5) lancer la boucle principale
    """
    screen, clock, fonts = init_pygame()

    runtime_state = create_runtime_state()

    # shared = ressources partagées (au minimum fonts)
    shared = {"fonts": fonts}

    manager = SceneManager(shared, runtime_state)

    run_app_loop(screen, clock, manager, runtime_state, fonts)


if __name__ == "__main__":
    main()
