import pygame
import math
from core.resource import resource_manager
from constant import (
    HEART_FULL, HEART_EMPTY, CHEESE_HUD, CHEESE_HUD_EMPTY, DECOY_PATH,
    DEFAULT_FONT, SCREEN_WIDTH, LOGICAL_WIDTH
)

class HUD:
    """
    Класс Heads-Up Display (HUD) для отображения игрового состояния.
    Отображает здоровье, количество собранного сыра и прогресс уровня.
    """
    def __init__(self):
        """Загрузка ресурсов интерфейса и инициализация таймеров."""
        self.heart_full = resource_manager.get_image(HEART_FULL)
        self.heart_empty = resource_manager.get_image(HEART_EMPTY)
        self.cheese_full = resource_manager.get_image(CHEESE_HUD)
        self.cheese_empty = resource_manager.get_image(CHEESE_HUD_EMPTY)
        self.decoy_img = pygame.transform.scale(resource_manager.get_image(DECOY_PATH), (32, 32))
        self.font = resource_manager.get_font(DEFAULT_FONT, 28)
        
        # Таймер для анимаций пульсации
        self.animation_timer = 0

    def draw(self, screen: pygame.Surface, player_health: int, max_health: int, cheese_count: int, 
             scale_cheese: int, red_cheese_collected=None, required_cheese=0, level_id=1, dt=0):
        """
        Отрисовка всех элементов HUD.

        Args:
            screen: Поверхность для отрисовки.
            player_health: Текущее здоровье игрока.
            max_health: Максимальное здоровье.
            cheese_count: Количество обычного сыра.
            scale_cheese: Прогресс накопления сыра для восстановления здоровья.
            red_cheese_collected: Количество красного сыра (для босса).
            required_cheese: Необходимое количество сыра для прохождения.
            level_id: ID текущего уровня.
            dt: Дельта времени для анимаций.
        """
        self.animation_timer += dt
        
        # 1. Счетчик сыра (верхний левый угол)
        cheese_color = (255, 255, 255)
        pulse_scale = 1.0
        
        # Подсветка и пульсация, если собрано достаточно сыра для выхода (уровни 1-2)
        if level_id < 3 and cheese_count >= required_cheese and required_cheese > 0:
            cheese_color = (255, 255, 50) # Желтый
            pulse_scale = 1.0 + 0.1 * math.sin(self.animation_timer * 10)
        
        cheese_text = self.font.render(f"Сыр: {cheese_count}", True, cheese_color)
        if pulse_scale != 1.0:
            new_size = (int(cheese_text.get_width() * pulse_scale), int(cheese_text.get_height() * pulse_scale))
            cheese_text = pygame.transform.scale(cheese_text, new_size)
        
        screen.blit(cheese_text, (20, 20))
        
        # 1.1 Счетчик красного сыра (только для уровня с боссом)
        if red_cheese_collected is not None:
             red_color = (255, 50, 50)
             red_pulse = 1.0
             if red_cheese_collected >= required_cheese:
                 red_color = (255, 0, 0) # Ярко-красный
                 red_pulse = 1.0 + 0.15 * math.sin(self.animation_timer * 12)
             
             red_left = max(0, required_cheese - red_cheese_collected)
             red_text = self.font.render(f"До победы: {red_left}", True, red_color)
             
             if red_pulse != 1.0:
                 new_size = (int(red_text.get_width() * red_pulse), int(red_text.get_height() * red_pulse))
                 red_text = pygame.transform.scale(red_text, new_size)
                 
             screen.blit(red_text, (20, 60))
        
        # 2. Здоровье (верхний правый угол)
        margin = 10
        x_start = LOGICAL_WIDTH - (max_health * (32 + margin)) - 20
        for i in range(max_health):
            img = self.heart_full if i < player_health else self.heart_empty
            screen.blit(img, (x_start + i * (32 + margin), 20))
            
        # 3. Шкала сыра (под здоровьем)
        scale_size = 5
        x_start_scale = LOGICAL_WIDTH - (scale_size * (32 + margin)) - 20
        for i in range(scale_size):
            img = self.cheese_full if i < scale_cheese else self.cheese_empty
            screen.blit(img, (x_start_scale + i * (32 + margin), 60))
