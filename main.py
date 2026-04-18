import pygame
import sys
from core.game import Game
from constant import FPS

def main():
    pygame.init()
    pygame.mixer.init()
    
    game = Game()
    clock = pygame.time.Clock()

    while game.running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        game.handle_events()
        game.update(dt)
        game.draw()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
