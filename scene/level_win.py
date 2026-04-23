import pygame
import os
from scene.base import Scene
from ui.button import Button
from constant import DEFAULT_FONT, LOGICAL_WIDTH, LOGICAL_HEIGHT, BG_WIN
from core.resource import resource_manager
from core.mixer import mixer

class LevelWinScene(Scene):
    """
    Сцена победы на уровне.
    Отображает поздравление, количество собранного сыра и кнопки перехода.
    """
    def __init__(self, game):
        """
        Инициализация сцены победы.

        Args:
            game: Объект игры.
        """
        super().__init__(game)
        self.cheese_count = 0
        self.current_level_id = 1
        self.font_large = resource_manager.get_font(DEFAULT_FONT, 56)
        self.font_medium = resource_manager.get_font(DEFAULT_FONT, 32)
        
        # Загрузка фона
        raw_bg = resource_manager.get_image(BG_WIN)
        self.bg = pygame.transform.scale(raw_bg, (LOGICAL_WIDTH, LOGICAL_HEIGHT))
        
        # Затемнение фона
        self.overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 100)) 
        
        center_x = LOGICAL_WIDTH // 2
        self.buttons = [
            Button(center_x, 480, "Вперёд!", self.next_level, game=self.game),
            Button(center_x, 600, "В меню", self.go_to_menu, game=self.game)
        ]

    def enter(self, **kwargs):
        """Вызывается при входе в сцену победы."""
        self.cheese_count = kwargs.get("cheese_count", 0)
        self.current_level_id = kwargs.get("level_id", 1)
        # Остановка музыки и запуск победного звука
        mixer.stop_music()
        mixer.stop_all_sfx()
        from constant import SFX_WIN
        mixer.play_sfx(resource_manager.get_sound(SFX_WIN))

    def next_level(self):
        """Переход к следующему уровню или финальным титрам."""
        next_id = self.current_level_id + 1
        # Проверка существования следующего уровня
        next_path = os.path.join("level", f"level{next_id}.json")
        if os.path.exists(next_path):
            self.game.state_machine.set_state("LEVEL", level_id=next_id)
        elif self.current_level_id == 3:
            # После 3-го уровня запускаем финальные титры
            self.game.state_machine.set_state("CREDITS")
        else:
            # Если уровень не найден, возвращаемся в меню (запасной вариант)
            self.game.state_machine.set_state("MENU")

    def go_to_menu(self):
        """Возврат в главное меню."""
        self.game.state_machine.set_state("MENU")

    def update(self, dt: float):
        """Обновление (не используется)."""
        pass

    def draw(self, screen: pygame.Surface):
        """
        Отрисовка экрана победы.

        Args:
            screen: Поверхность для отрисовки.
        """
        # Отрисовка фона
        screen.blit(self.bg, (0, 0))
        screen.blit(self.overlay, (0, 0))
        
        # Заголовок
        title_surf = self.font_large.render("УРОВЕНЬ ПРОЙДЕН!", True, (50, 255, 50))
        title_rect = title_surf.get_rect(center=(LOGICAL_WIDTH // 2, 200))
        screen.blit(title_surf, title_rect)
        
        # Статистика собранного сыра
        score_surf = self.font_medium.render(f"Собрано сыра: {self.cheese_count}", True, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(LOGICAL_WIDTH // 2, 300))
        screen.blit(score_surf, score_rect)
        
        for button in self.buttons:
            button.draw(screen)
