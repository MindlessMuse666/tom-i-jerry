from core.state_machine import BaseState

import pygame

class Scene(BaseState):
    """
    Базовый класс для всех игровых сцен.
    Обеспечивает общую логику управления кнопками и переходов.
    """
    def __init__(self, game):
        """
        Инициализация сцены.

        Args:
            game: Объект игры.
        """
        super().__init__(game)
        self.buttons = []
        self.selected_button_index = -1 # Индекс выбранной кнопкой (клавиатура/геймпад)

    def enter(self, **kwargs):
        """Вызывается при входе в сцену."""
        pass

    def exit(self):
        """Вызывается при выходе из сцены."""
        pass

    def handle_events(self, events: list[pygame.event.Event]):
        """
        Обработка событий ввода для сцены и её кнопок.

        Args:
            events: Список событий Pygame.
        """
        # Стандартная навигация по кнопкам
        if self.buttons:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        if self.selected_button_index == -1:
                            self.selected_button_index = len(self.buttons) - 1
                        else:
                            self.selected_button_index = (self.selected_button_index - 1) % len(self.buttons)
                    elif event.key == pygame.K_DOWN:
                        if self.selected_button_index == -1:
                            self.selected_button_index = 0
                        else:
                            self.selected_button_index = (self.selected_button_index + 1) % len(self.buttons)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_button_index == -1:
                            # Если ничего не выбрано, нажимаем первую кнопку
                            self.selected_button_index = 0
                            self.buttons[0].click()
                        else:
                            self.buttons[self.selected_button_index].click()
            
            # Обновление состояния выбора и обработка мыши
            for i, button in enumerate(self.buttons):
                button.is_selected = (i == self.selected_button_index)
                button.handle_events(events)
                # Если мышь над кнопкой, она перехватывает фокус
                if button.is_hovered:
                    self.selected_button_index = i

    def update(self, dt: float):
        """
        Обновление логики сцены.

        Args:
            dt: Дельта времени.
        """
        pass

    def draw(self, screen: pygame.Surface):
        """
        Отрисовка сцены.

        Args:
            screen: Поверхность для отрисовки.
        """
        pass
