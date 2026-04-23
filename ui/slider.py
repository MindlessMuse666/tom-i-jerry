import pygame
from core.resource import resource_manager
from constant import SLIDER_BG, SLIDER_HANDLE

class Slider:
    """
    Класс ползунка (слайдера) для настроек (например, громкости).
    Позволяет изменять значение в диапазоне [0, 1] путем перетаскивания.
    """
    def __init__(self, x: int, y: int, width: int, value: float, callback, game=None):
        """
        Инициализация слайдера.

        Args:
            x: Координата X левого верхнего угла.
            y: Координата Y левого верхнего угла.
            width: Ширина слайдера.
            value: Начальное значение (0.0 - 1.0).
            callback: Функция, вызываемая при изменении значения.
            game: Ссылка на основной объект игры (для смены курсора).
        """
        self.game = game
        raw_bg = resource_manager.get_image(SLIDER_BG)
        # Масштабирование фона (делаем чуть толще для лучшей видимости)
        self.bg_img = pygame.transform.scale(raw_bg, (width, 40))
        self.rect = self.bg_img.get_rect(topleft=(x, y))
        self.width = width
        
        raw_handle = resource_manager.get_image(SLIDER_HANDLE)
        # Масштабирование ручки под размер фона
        self.handle_img = pygame.transform.scale(raw_handle, (30, 60))
        # Начальная позиция ручки
        self.handle_rect = self.handle_img.get_rect(center=(self.rect.left + value * width, self.rect.centery))
        
        self.value = value
        self.callback = callback
        self.dragging = False

    def handle_events(self, events: list[pygame.event.Event]):
        """
        Обработка событий мыши для слайдера.

        Args:
            events: Список событий Pygame.
        """
        mouse_pos = pygame.mouse.get_pos()
        
        # Смена курсора при наведении на ручку
        if self.handle_rect.collidepoint(mouse_pos) and self.game:
            self.game.current_cursor_type = "slider"

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.handle_rect.collidepoint(mouse_pos):
                    self.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
        
        if self.dragging:
            # Обновление значения на основе позиции мыши с ограничением по краям фона
            new_x = max(self.rect.left, min(mouse_pos[0], self.rect.right))
            self.value = (new_x - self.rect.left) / self.width
            self.handle_rect.centerx = new_x
            self.callback(self.value)

    def draw(self, screen: pygame.Surface):
        """
        Отрисовка слайдера на экране.

        Args:
            screen: Поверхность для отрисовки.
        """
        screen.blit(self.bg_img, self.rect)
        screen.blit(self.handle_img, self.handle_rect)
