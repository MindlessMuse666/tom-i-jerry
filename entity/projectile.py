import pygame
import os
from core.resource import resource_manager
from constant import DECOY_PATH, ROCKET_PATH, SFX_ROCKET, SFX_CRATE_BREAK
from core.mixer import mixer

class Decoy(pygame.sprite.Sprite):
    """
    A cheese decoy that Jerry can throw to attract enemies.
    """
    def __init__(self, x, y, vel_x, vel_y):
        super().__init__()
        
        # Load visual
        img = resource_manager.get_image(DECOY_PATH)
        # Scaling: same as Cheese (scale 2, 64x64)
        self.image = pygame.transform.scale(img, (64, 64))
        self.rect = self.image.get_rect(center=(x, y))
        
        # Physics
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(vel_x, vel_y)
        self.gravity = 1200
        self.friction = 300
        self.bounce = 0.2 # Small bounce force
        
        self.on_ground = False
        self.bounce_count = 0
        self.life_timer = None # Will be set to 3.0 after first bounce/landing
        
    def update(self, dt, platforms):
        # 1. Gravity (only if not landed or still bouncing)
        if not self.on_ground:
            self.vel.y += self.gravity * dt
        
        # 2. Horizontal movement
        if not self.on_ground:
            self.pos.x += self.vel.x * dt
            self.rect.centerx = round(self.pos.x)
            self.check_collisions(platforms, 'horizontal')
        
        # 3. Vertical movement
        if not self.on_ground:
            self.pos.y += self.vel.y * dt
            self.rect.centery = round(self.pos.y)
            self.check_collisions(platforms, 'vertical')
        
        # 4. Life timer (starts after landing)
        if self.on_ground:
            if self.life_timer is None:
                self.life_timer = 3.0
            
            self.life_timer -= dt
            if self.life_timer <= 0:
                self.kill()

    def check_collisions(self, platforms, direction):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == 'horizontal':
                    if self.vel.x > 0:
                        self.rect.right = platform.rect.left
                    elif self.vel.x < 0:
                        self.rect.left = platform.rect.right
                    
                    if self.bounce_count >= 1:
                        self.vel.x = 0
                        self.on_ground = True
                    else:
                        self.vel.x *= -self.bounce
                    
                    self.bounce_count += 1
                    self.pos.x = float(self.rect.centerx)
                else:
                    if self.vel.y > 0: # Falling
                        self.rect.bottom = platform.rect.top
                        
                        if self.bounce_count >= 1:
                            self.vel.y = 0
                            self.vel.x = 0
                            self.on_ground = True
                        else:
                            self.vel.y *= -self.bounce
                        
                        self.bounce_count += 1
                    elif self.vel.y < 0: # Hit ceiling
                        self.rect.top = platform.rect.bottom
                        self.vel.y *= -self.bounce
                    self.pos.y = float(self.rect.centery)

class Rocket(pygame.sprite.Sprite):
    """
    Rocket fired by Boss Tom.
    """
    def __init__(self, x, y, target_player):
        super().__init__()
        img = resource_manager.get_image(ROCKET_PATH)
        self.image = pygame.transform.scale(img, (48, 48))
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.target = target_player
        self.speed = 300
        self.vel = pygame.Vector2(0, 0)
        
        # Play fire sound
        mixer.play_sfx(resource_manager.get_sound(SFX_ROCKET))

    def update(self, dt):
        # Home in on player center
        target_pos = pygame.Vector2(self.target.rect.center)
        direction = (target_pos - self.pos).normalize()
        
        self.vel = direction * self.speed
        self.pos += self.vel * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
        # Rotate image to face movement
        angle = self.vel.angle_to(pygame.Vector2(1, 0))
        self.image = pygame.transform.rotate(
            pygame.transform.scale(resource_manager.get_image(ROCKET_PATH), (48, 48)), 
            angle
        )
        
        # Out of bounds
        if self.pos.x < -100 or self.pos.x > 1400 or self.pos.y < -100 or self.pos.y > 800:
            self.kill()
