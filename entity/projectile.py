import pygame
import os
from core.resource import resource_manager
from constant import DECOY_PATH, ROCKET_PATH, SFX_ROCKET_LAUNCH, SFX_EXPLOSION, SFX_CRATE_BREAK
from core.mixer import mixer

class Decoy(pygame.sprite.Sprite):
    """
    A cheese decoy that Jerry can throw to attract enemies.
    """
    def __init__(self, x, y, vel_x, vel_y):
        super().__init__()
        
        # Load visual
        self.sprite_sheet = resource_manager.get_image(DECOY_PATH)
        self.frames = self.load_frames()
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8 # Fast blink/animation
        
        self.image = self.frames[0]
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

    def load_frames(self):
        frames = []
        # decoy.png (64x32), 2 frames of 32x32
        for i in range(2):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            surf.blit(self.sprite_sheet, (0, 0), (i * 32, 0, 32, 32))
            # Scale 2x as before (64x64)
            frames.append(pygame.transform.scale(surf, (64, 64)))
        return frames
        
    def update(self, dt, platforms):
        # Animation
        self.animation_timer += dt
        if self.animation_timer >= 1.0 / self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

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
        # Increased scale 2x (base was 48, now 96)
        self.image = pygame.transform.scale(img, (96, 96))
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.target = target_player
        self.speed = 350
        self.vel = pygame.Vector2(0, 0)
        
        # Play fire sound
        mixer.play_sfx(resource_manager.get_sound(SFX_ROCKET_LAUNCH))

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
            pygame.transform.scale(resource_manager.get_image(ROCKET_PATH), (96, 96)), 
            angle
        )
        
        # Out of bounds
        if self.pos.x < -100 or self.pos.x > 1400 or self.pos.y < -100 or self.pos.y > 800:
            self.kill()

    def explode(self):
        mixer.play_sfx(resource_manager.get_sound(SFX_EXPLOSION))
        self.kill()
