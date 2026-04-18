import pygame

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 100, 100)) # Gray platform
        self.rect = self.image.get_rect(topleft=(x, y))

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, path, speed):
        super().__init__(x, y, width, height)
        self.start_pos = pygame.Vector2(x, y)
        self.path = pygame.Vector2(path) # Relative to start
        self.end_pos = self.start_pos + self.path
        self.speed = speed
        self.direction = 1
        self.pos = pygame.Vector2(x, y)

    def update(self, dt):
        target = self.end_pos if self.direction == 1 else self.start_pos
        move_vec = target - self.pos
        
        if move_vec.length() > 0:
            move_vec = move_vec.normalize() * self.speed * dt
            self.pos += move_vec
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
            
            # Check if reached target
            if (target - self.pos).length() < 2:
                self.direction *= -1
