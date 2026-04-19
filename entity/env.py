import pygame
from core.resource import resource_manager
from constant import PLATFORM_PATH, MOVING_PLATFORM_PATH, GROUND_PATH

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path=PLATFORM_PATH):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        tile_img = resource_manager.get_image(image_path)
        # Tile the image (32x32 tiles)
        for ty in range(0, height, 32):
            for tx in range(0, width, 32):
                self.image.blit(tile_img, (tx, ty))
        self.rect = self.image.get_rect(topleft=(x, y))

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, path, speed):
        super().__init__(x, y, width, height, MOVING_PLATFORM_PATH)
        self.start_pos = pygame.Vector2(x, y)
        self.path = pygame.Vector2(path) # Relative to start
        self.end_pos = self.start_pos + self.path
        self.speed = speed
        self.direction = 1
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0) # Store current velocity

    def update(self, dt):
        target = self.end_pos if self.direction == 1 else self.start_pos
        move_vec = target - self.pos
        
        if move_vec.length() > 0:
            # Correct velocity calculation
            direction_vec = move_vec.normalize()
            self.vel = direction_vec * self.speed
            
            self.pos += self.vel * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
            
            # Check if reached target
            if (target - self.pos).length() < 2:
                self.direction *= -1
        else:
            self.vel = pygame.Vector2(0, 0)
