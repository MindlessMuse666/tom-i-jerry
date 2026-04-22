import pygame
from core.resource import resource_manager
from constant import (
    HEART_FULL, HEART_EMPTY, CHEESE_HUD, CHEESE_HUD_EMPTY, DECOY_PATH,
    DEFAULT_FONT, SCREEN_WIDTH, LOGICAL_WIDTH
)

class HUD:
    def __init__(self):
        self.heart_full = resource_manager.get_image(HEART_FULL)
        self.heart_empty = resource_manager.get_image(HEART_EMPTY)
        self.cheese_full = resource_manager.get_image(CHEESE_HUD)
        self.cheese_empty = resource_manager.get_image(CHEESE_HUD_EMPTY)
        self.decoy_img = pygame.transform.scale(resource_manager.get_image(DECOY_PATH), (32, 32))
        self.font = resource_manager.get_font(DEFAULT_FONT, 28) # Reduced from 36 to 28

    def draw(self, screen, player_health, max_health, cheese_count, scale_cheese, red_cheese_left=None):
        # 1. Cheese counter (top left)
        cheese_text = self.font.render(f"Сыр: {cheese_count}", True, (255, 255, 255))
        screen.blit(cheese_text, (20, 20))
        
        # 1.1 Red cheese counter (for boss level)
        if red_cheese_left is not None:
             red_text = self.font.render(f"До победы: {red_cheese_left}", True, (255, 50, 50))
             screen.blit(red_text, (20, 60))
        
        # 2. Health (top right)
        margin = 10
        x_start = LOGICAL_WIDTH - (max_health * (32 + margin)) - 20
        for i in range(max_health):
            img = self.heart_full if i < player_health else self.heart_empty
            screen.blit(img, (x_start + i * (32 + margin), 20))
            
        # 3. Cheese scale (under health)
        scale_size = 5
        x_start_scale = LOGICAL_WIDTH - (scale_size * (32 + margin)) - 20
        for i in range(scale_size):
            img = self.cheese_full if i < scale_cheese else self.cheese_empty
            screen.blit(img, (x_start_scale + i * (32 + margin), 60))
