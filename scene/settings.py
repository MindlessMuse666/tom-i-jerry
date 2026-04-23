import pygame
from scene.base import Scene
from ui.button import Button
from ui.slider import Slider
from constant import SCREEN_WIDTH, SCREEN_HEIGHT, BG_MENU, DEFAULT_FONT, LOGICAL_WIDTH, LOGICAL_HEIGHT
from core.resource import resource_manager
from setting import settings

class SettingsScene(Scene):
    """
    Сцена настроек игры.
    Позволяет изменять громкость музыки и звуковых эффектов.
    """
    def __init__(self, game):
        """
        Инициализация экрана настроек.

        Args:
            game: Объект игры.
        """
        super().__init__(game)
        raw_bg = resource_manager.get_image(BG_MENU)
        self.bg = pygame.transform.scale(raw_bg, (LOGICAL_WIDTH, LOGICAL_HEIGHT))
        self.font = resource_manager.get_font(DEFAULT_FONT, 32)
        self.previous_state = "MENU"
        
        center_x = LOGICAL_WIDTH // 2
        
        # Подписи к слайдерам
        self.music_label = self.font.render("Музыка", True, (255, 50, 50))
        self.sfx_label = self.font.render("Эффекты", True, (50, 150, 255))
        
        # Слайдеры громкости
        slider_w = 400
        self.music_slider = Slider(center_x - slider_w // 2, 220, slider_w, settings.music_volume, self.set_music_volume, game=self.game)
        self.sfx_slider = Slider(center_x - slider_w // 2, 420, slider_w, settings.sfx_volume, self.set_sfx_volume, game=self.game)
        
        # Кнопка возврата
        self.back_button = Button(center_x, 620, "Назад", self.go_back, game=self.game)
        self.buttons = [self.back_button]

    def set_music_volume(self, value: float):
        """
        Изменение громкости музыки.

        Args:
            value: Значение от 0.0 до 1.0.
        """
        settings.music_volume = value
        pygame.mixer.music.set_volume(value)
        settings.save()

    def set_sfx_volume(self, value: float):
        """
        Изменение громкости звуковых эффектов.

        Args:
            value: Значение от 0.0 до 1.0.
        """
        settings.sfx_volume = value
        resource_manager.set_sfx_volume(value)
        settings.save()

    def go_back(self):
        """Возврат к предыдущему состоянию (Меню или Пауза)."""
        self.game.state_machine.set_state(self.previous_state)
        # Сброс к значению по умолчанию
        self.previous_state = "MENU"

    def handle_events(self, events: list[pygame.event.Event]):
        """Обработка событий слайдеров и кнопок."""
        self.music_slider.handle_events(events)
        self.sfx_slider.handle_events(events)
        super().handle_events(events)

    def draw(self, screen: pygame.Surface):
        """
        Отрисовка экрана настроек.

        Args:
            screen: Поверхность для отрисовки.
        """
        screen.blit(self.bg, (0, 0))
        
        # Отрисовка подписей над слайдерами
        screen.blit(self.music_label, (LOGICAL_WIDTH // 2 - self.music_label.get_width() // 2, 170))
        screen.blit(self.sfx_label, (LOGICAL_WIDTH // 2 - self.sfx_label.get_width() // 2, 370))
        
        self.music_slider.draw(screen)
        self.sfx_slider.draw(screen)
        self.back_button.draw(screen)
