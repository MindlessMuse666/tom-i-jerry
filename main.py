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
    
    # Инициализация аудио с обработкой ошибок (WASAPI Fix)
    try:
        pygame.mixer.init()
    except pygame.error as e:
        print(f"Предупреждение: Не удалось инициализировать аудио (WASAPI error): {e}")
        # Попытка инициализации с фиктивным драйвером (без звука), чтобы игра не вылетала
        import os
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
        try:
            pygame.mixer.init()
        except:
            print("Критическая ошибка: Аудио-подсистема полностью недоступна.")
    
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
