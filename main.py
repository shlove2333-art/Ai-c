import pygame
import sys
from game import GameApp
from constants import W, H


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Forge & Guard")
    clock = pygame.time.Clock()

    app = GameApp(screen)

    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            app.handle_event(event)

        app.update(dt)
        app.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
