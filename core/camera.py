import pygame
from constant import SCREEN_WIDTH, SCREEN_HEIGHT, LOGICAL_WIDTH, LOGICAL_HEIGHT

class Camera:
    def __init__(self, width, height):
        self.offset = pygame.Vector2(0, 0)
        self.width = width
        self.height = height
        self.lerp_speed = 0.1

    def apply(self, entity):
        return entity.rect.move(-self.offset.x, -self.offset.y)

    def update(self, target_rect):
        # Target position is center of logical screen
        target_x = target_rect.centerx - LOGICAL_WIDTH // 2
        target_y = target_rect.centery - LOGICAL_HEIGHT // 2
        
        # Clamp to level boundaries
        target_x = max(0, min(target_x, self.width - LOGICAL_WIDTH))
        target_y = max(0, min(target_y, self.height - LOGICAL_HEIGHT))
        
        # Lerp
        self.offset.x += (target_x - self.offset.x) * self.lerp_speed
        self.offset.y += (target_y - self.offset.y) * self.lerp_speed
