"""
Модуль камеры для управления отображением игрового мира.
Реализует следование за игроком с эффектом плавности (lerp) и смещением в сторону курсора.
"""
import pygame
from constant import LOGICAL_WIDTH, LOGICAL_HEIGHT

class Camera:
    """
    Класс камеры, вычисляющий смещение отрисовки для всех объектов мира.
    """
    def __init__(self, width, height):
        self.offset = pygame.Vector2(0, 0)
        self.width = width
        self.height = height
        self.lerp_speed = 0.1

    def apply(self, entity):
        """Возвращает прямоугольник объекта, смещенный относительно камеры."""
        return entity.rect.move(-self.offset.x, -self.offset.y)

    def update(self, target_rect, mouse_pos=None):
        """
        Обновляет позицию камеры на основе целевого объекта (игрока) и курсора мыши.
        """
        # Целевая позиция - центр логического экрана
        target_x = target_rect.centerx - LOGICAL_WIDTH // 2
        target_y = target_rect.centery - LOGICAL_HEIGHT // 2
        
        # Смещение камеры в сторону курсора (плавный взгляд вперед)
        if mouse_pos:
            mouse_shift_x = (mouse_pos[0] - LOGICAL_WIDTH // 2) * 0.2
            mouse_shift_y = (mouse_pos[1] - LOGICAL_HEIGHT // 2) * 0.2
            target_x += mouse_shift_x
            target_y += mouse_shift_y

        # Ограничение камеры границами уровня по горизонтали
        target_x = max(0, min(target_x, self.width - LOGICAL_WIDTH))
        
        # Ограничение камеры по вертикали (низ уровня)
        target_y = min(target_y, self.height - LOGICAL_HEIGHT)
        # Позволяем камере смотреть чуть выше при высоких прыжках
        target_y = max(-500, target_y)
        
        # Линейная интерполяция для плавного движения камеры
        self.offset.x += (target_x - self.offset.x) * self.lerp_speed
        self.offset.y += (target_y - self.offset.y) * self.lerp_speed
