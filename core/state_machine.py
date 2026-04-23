"""
Модуль для управления состояниями (сценами) игры.
Реализует паттерн «Состояние» для переключения между уровнями, меню и другими экранами.
"""

class StateMachine:
    """
    Машина состояний, управляющая жизненным циклом текущей активной сцены.
    """
    def __init__(self):
        self.states = {}
        self.current_state = None

    def add_state(self, name, state):
        """Регистрация нового состояния в машине."""
        self.states[name] = state

    def get_state(self, name):
        """Получение объекта состояния по его имени."""
        return self.states.get(name)

    def set_state(self, name, **kwargs):
        """
        Переключение на указанное состояние.
        Вызывает exit() у старого состояния и enter() у нового.
        """
        if self.current_state:
            self.current_state.exit()
        
        self.current_state = self.states[name]
        self.current_state.enter(**kwargs)

    def handle_events(self, events):
        """Передача событий Pygame текущему состоянию."""
        if self.current_state:
            self.current_state.handle_events(events)

    def update(self, dt):
        """Обновление логики текущего состояния."""
        if self.current_state:
            self.current_state.update(dt)

    def draw(self, screen):
        """Отрисовка текущего состояния на экран."""
        if self.current_state:
            self.current_state.draw(screen)

class BaseState:
    """
    Базовый класс для всех состояний игры.
    Определяет интерфейс, который должны реализовать все сцены.
    """
    def __init__(self, game):
        self.game = game

    def enter(self, **kwargs):
        """Вызывается при входе в состояние."""
        pass

    def exit(self):
        """Вызывается при выходе из состояния."""
        pass

    def handle_events(self, events):
        """Обработка ввода пользователя."""
        pass

    def update(self, dt):
        """Обновление игровой логики за кадр."""
        pass

    def draw(self, screen):
        """Отрисовка кадра."""
        pass
