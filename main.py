"""Point d'entree du jeu du Pendu"""

import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BACKGROUND_COLOR
from scene_manager import SceneManager

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Le Pendu")
    clock = pygame.time.Clock()

    manager = SceneManager(screen)
    manager.go_to("menu")

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        manager.handle_events(events)
        manager.update()

        screen.fill(BACKGROUND_COLOR)
        manager.draw()
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
