import pygame
from constant import LOGICAL_WIDTH, LOGICAL_HEIGHT
from core.state_machine import StateMachine

class Game:
    """
    Основной класс игры, управляющий окном, ресурсами и циклом событий.
    """
    def __init__(self):
        """
        Инициализация игрового движка, создание окна и регистрация сцен.
        """
        # Настройка дисплея
        # Используем SCALED для автоматического масштабирования логического разрешения
        # и FULLSCREEN для запуска во весь экран
        flags = pygame.SCALED | pygame.FULLSCREEN
        
        # Устанавливаем логическое разрешение 1280x720. 
        # Режим SCALED растянет его до физического разрешения монитора.
        self.screen = pygame.display.set_mode((LOGICAL_WIDTH, LOGICAL_HEIGHT), flags)
        pygame.display.set_caption("Jerry's Escape from the Crazy Cat's House")
        
        self.running = True
        self.state_machine = StateMachine()
        
        # Импорт сцен (ленивый импорт для предотвращения циклической зависимости)
        from scene.menu import MenuScene
        from scene.settings import SettingsScene
        from scene.level import LevelScene
        from scene.game_over import GameOverScene
        from scene.level_win import LevelWinScene
        from scene.pause import PauseScene
        from scene.credits import CreditsScene
        
        # Регистрация всех игровых состояний
        self.state_machine.add_state("MENU", MenuScene(self))
        self.state_machine.add_state("SETTINGS", SettingsScene(self))
        self.state_machine.add_state("LEVEL", LevelScene(self))
        self.state_machine.add_state("GAME_OVER", GameOverScene(self))
        self.state_machine.add_state("LEVEL_WIN", LevelWinScene(self))
        self.state_machine.add_state("PAUSE", PauseScene(self))
        self.state_machine.add_state("CREDITS", CreditsScene(self))
        
        # Начальное состояние - главное меню
        self.state_machine.set_state("MENU")
        
        # Установка иконки окна
        try:
            icon = pygame.image.load("asset/other/icon.ico")
            pygame.display.set_icon(icon)
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")
        
        # Настройка кастомных курсоров
        pygame.mouse.set_visible(False)
        from constant import CUR_BASIC, CUR_SELECT, CUR_CANCEL, CUR_SLIDER
        from core.resource import resource_manager
        self.cursors = {
            "basic": resource_manager.get_image(CUR_BASIC),
            "select": resource_manager.get_image(CUR_SELECT),
            "cancel": resource_manager.get_image(CUR_CANCEL),
            "slider": resource_manager.get_image(CUR_SLIDER)
        }
        self.current_cursor_type = "basic"

    def handle_events(self):
        """Обработка системных событий и событий ввода."""
        events = pygame.event.get()
        # Сброс типа курсора к базовому каждый кадр; кнопки изменят его при наведении
        self.current_cursor_type = "basic"
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        
        self.state_machine.handle_events(events)

    def update(self, dt: float):
        """
        Обновление логики текущей активной сцены.

        Args:
            dt: Дельта времени.
        """
        self.state_machine.update(dt)

    def draw(self):
        """Отрисовка кадра: сцена + кастомный курсор."""
        self.screen.fill((0, 0, 0)) # Заливка черным цветом по умолчанию
        self.state_machine.draw(self.screen)
        
        # Отрисовка курсора мыши поверх всех элементов
        cursor_img = self.cursors.get(self.current_cursor_type, self.cursors["basic"])
        self.screen.blit(cursor_img, pygame.mouse.get_pos())
        
        pygame.display.flip()

    def quit(self):
        """Завершение работы игры."""
        self.running = False
