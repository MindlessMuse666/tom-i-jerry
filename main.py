import pygame
import sys
from core.game import Game
from constant import FPS

def main():
    """
    Точка входа в игру.
    Инициализирует Pygame, создает объект игры и запускает главный цикл.
    """
    pygame.init()
    pygame.mixer.init()
    
    # Создание основного игрового контроллера
    game = Game()
    clock = pygame.time.Clock()

    # Главный игровой цикл
    while game.running:
        # Ограничение FPS и расчет дельты времени
        dt = clock.tick(FPS) / 1000.0
        
        # Ограничение dt для предотвращения рывков физики (например, при загрузке)
        dt = min(dt, 0.05)
        
        # Обработка ввода, обновление логики и отрисовка
        game.handle_events()
        game.update(dt)
        game.draw()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
