import pygame
from scene.base import Scene
from ui.button import Button
from constant import DEFAULT_FONT, LOGICAL_WIDTH, LOGICAL_HEIGHT, BG_PAUSE
from core.resource import resource_manager
from core.mixer import mixer

class PauseScene(Scene):
    """
    Сцена паузы.
    Приостанавливает игровой процесс, позволяя вернуться в игру, изменить настройки или выйти.
    """
    def __init__(self, game):
        """
        Инициализация сцены паузы.

        Args:
            game: Объект игры.
        """
        super().__init__(game)
        self.font_large = resource_manager.get_font(DEFAULT_FONT, 56)
        
        # Загрузка фона
        raw_bg = resource_manager.get_image(BG_PAUSE)
        self.bg = pygame.transform.scale(raw_bg, (LOGICAL_WIDTH, LOGICAL_HEIGHT))
        
        # Затемнение
        self.overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 100)) 
        
        center_x = LOGICAL_WIDTH // 2
        self.buttons = [
            Button(center_x, 320, "Игра", self.resume_game, game=self.game),
            Button(center_x, 420, "Опции", self.open_settings, game=self.game),
            Button(center_x, 580, "Меню", self.go_to_menu, game=self.game)
        ]
        self.current_level_id = 1

    def enter(self, **kwargs):
        """Сохранение текущего ID уровня для возврата из паузы."""
        self.current_level_id = kwargs.get("level_id", 1)

    def resume_game(self):
        """Продолжение игры с того же места."""
        self.game.state_machine.set_state("LEVEL", level_id=self.current_level_id, resume=True)

    def open_settings(self):
        """Переход в настройки с запоминанием возврата в паузу."""
        self.game.state_machine.get_state("SETTINGS").previous_state = "PAUSE"
        self.game.state_machine.set_state("SETTINGS")

    def go_to_menu(self):
        """Полная остановка игры и выход в главное меню."""
        mixer.stop_music()
        mixer.stop_all_sfx()
        self.game.state_machine.set_state("MENU")

    def update(self, dt: float):
        """Обновление (не используется)."""
        pass

    def draw(self, screen: pygame.Surface):
        """
        Отрисовка экрана паузы поверх игрового мира.

        Args:
            screen: Поверхность для отрисовки.
        """
        screen.blit(self.bg, (0, 0))
        screen.blit(self.overlay, (0, 0))
        
        # Заголовок "ПАУЗА"
        title_surf = self.font_large.render("ПАУЗА", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(LOGICAL_WIDTH // 2, 150))
        screen.blit(title_surf, title_rect)
        
        for button in self.buttons:
            button.draw(screen)
