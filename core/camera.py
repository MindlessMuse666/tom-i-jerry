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
        # For X, we clamp strictly to the level width
        target_x = max(0, min(target_x, self.width - LOGICAL_WIDTH))
        
        # For Y, we allow the camera to follow upwards if the player jumps high
        # We only clamp the bottom boundary to the level height
        # But we allow the top to go beyond 0 if needed (though usually 0 is top of level)
        # If height is 720 and LOGICAL_HEIGHT is 720, target_y is 0
        target_y = min(target_y, self.height - LOGICAL_HEIGHT)
        # Allow looking up slightly beyond 0 if needed, but let's keep it clamped at 0 for now 
        # unless we specifically want a very tall level.
        target_y = max(-500, target_y) # Allow looking up to -500px for tall jumps
        
        # Lerp
        self.offset.x += (target_x - self.offset.x) * self.lerp_speed
        self.offset.y += (target_y - self.offset.y) * self.lerp_speed
