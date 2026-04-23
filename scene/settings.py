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
        
        # Слайдеры громкости (приближены друг к другу для лучшего вида)
        slider_w = 400
        # Музыкальный блок опущен чуть ниже, чтобы быть ближе к эффектам
        self.music_slider = Slider(center_x - slider_w // 2, 270, slider_w, settings.music_volume, self.set_music_volume, game=self.game)
        self.sfx_slider = Slider(center_x - slider_w // 2, 420, slider_w, settings.sfx_volume, self.set_sfx_volume, game=self.game)
        
        # Кнопка возврата
        self.back_button = Button(center_x, 620, "Назад", self.go_back, game=self.game)
        self.buttons = [self.back_button]

    def draw_text_with_outline(self, screen, text, color, center_pos):
        """Отрисовка текста с четкой белой обводкой."""
        # Рендерим основной текст и обводку
        main_surf = self.font.render(text, True, color)
        # Белая обводка для лучшей читаемости на пестром фоне
        outline_surf = self.font.render(text, True, (255, 255, 255))
        
        x = center_pos[0] - main_surf.get_width() // 2
        y = center_pos[1]
        
        # Отрисовка обводки (в 8 направлениях для плотности)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
            screen.blit(outline_surf, (x + dx, y + dy))
        
        # Отрисовка основного текста
        screen.blit(main_surf, (x, y))

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
        
        # Отрисовка подписей с обводкой (позиции обновлены)
        self.draw_text_with_outline(screen, "Музыка", (255, 50, 50), (LOGICAL_WIDTH // 2, 220))
        self.draw_text_with_outline(screen, "Эффекты", (50, 150, 255), (LOGICAL_WIDTH // 2, 370))
        
        self.music_slider.draw(screen)
        self.sfx_slider.draw(screen)
        self.back_button.draw(screen)
