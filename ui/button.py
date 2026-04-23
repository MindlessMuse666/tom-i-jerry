import pygame
from core.resource import resource_manager
from core.mixer import mixer
from constant import BTN_NORMAL, BTN_HOVER, DEFAULT_FONT, SFX_UI_CLICK

class Button:
    """
    Класс интерактивной кнопки для игрового интерфейса.
    Поддерживает состояния наведения, выбора и вызов обратной функции при нажатии.
    """
    def __init__(self, x: int, y: int, text: str, callback, font_size=32, game=None, width=280, height=80): 
        """
        Инициализация кнопки.

        Args:
            x: Координата X центра кнопки.
            y: Координата Y центра кнопки.
            text: Текст на кнопке.
            callback: Функция, вызываемая при нажатии.
            font_size: Размер шрифта.
            game: Ссылка на основной объект игры (для смены курсора).
            width: Ширина кнопки.
            height: Высота кнопки.
        """
        self.game = game
        raw_normal = resource_manager.get_image(BTN_NORMAL)
        raw_hover = resource_manager.get_image(BTN_HOVER)
        
        # Масштабирование изображений кнопки
        self.normal_img = pygame.transform.scale(raw_normal, (width, height))
        self.hover_img = pygame.transform.scale(raw_hover, (width, height))
        
        self.rect = self.normal_img.get_rect(center=(x, y))
        self.text = text
        self.callback = callback
        self.font = resource_manager.get_font(DEFAULT_FONT, font_size)
        self.is_hovered = False
        self.is_selected = False
        
        # Определение типа курсора при наведении
        self.cursor_type = "select"
        if text in ["Выход", "Меню", "Назад"]:
            self.cursor_type = "cancel"

        # Предварительная загрузка звука клика
        self.click_sfx = resource_manager.get_sound(SFX_UI_CLICK)

        # Отрисовка текста
        self.text_surf = self.font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        # Небольшое смещение текста вверх для лучшего визуального центрирования
        self.text_rect.centery -= 2 

    def handle_events(self, events: list[pygame.event.Event]):
        """
        Обработка событий мыши для кнопки.

        Args:
            events: Список событий Pygame.
        """
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Смена курсора в зависимости от состояния
        if self.is_hovered and self.game:
            self.game.current_cursor_type = self.cursor_type

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.is_hovered:
                    self.click()

    def click(self):
        """Проигрывание звука и выполнение действия кнопки."""
        mixer.play_sfx(self.click_sfx)
        self.callback()

    def draw(self, screen: pygame.Surface):
        """
        Отрисовка кнопки на экране.

        Args:
            screen: Поверхность для отрисовки.
        """
        img = self.hover_img if (self.is_hovered or self.is_selected) else self.normal_img
        screen.blit(img, self.rect)
        screen.blit(self.text_surf, self.text_rect)

