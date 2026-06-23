import pygame
import sys
from player import Player
from game import Game, W, H


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Card Dungeon")
    clock = pygame.time.Clock()

    player = Player()
    game = Game(screen, player)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)

        game.draw()
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
