try:
    import tomllib
except ImportError:
    import tomli as tomllib
import os

import pygame
from core.resource import resource_manager
from core.mixer import mixer
from constant import TOM_PATH, BROOM_PATH, SFX_HURT

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        
        # Load config
        config_path = os.path.join("config", "enemy.toml")
        if not os.path.exists(config_path):
            # Create default config if missing
            self.config = {
                "speed": 150.0,
                "chase_radius": 400.0,
                "health": 1,
                "damage": 1
            }
        else:
            with open(config_path, "rb") as f:
                self.config = tomllib.load(f)
                
        self.sprite_sheet = resource_manager.get_image(image_path)
        self.scale_factor = 2
        self.frames = self.load_frames()
        
        self.state = "IDLE"
        self.frame_index = 0
        self.animation_speed = 6
        self.animation_timer = 0
        self.facing_right = True
        
        self.image = self.frames["IDLE"][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.gravity = 1200
        
        self.on_ground = False
        self.health = self.config["health"]

    def load_frames(self):
        frames = {"IDLE": [], "WALK": []}
        # 64x32 (cell 32x32): 1st cell - idle, 2nd cell - walk
        for i, state in enumerate(["IDLE", "WALK"]):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            surf.blit(self.sprite_sheet, (0, 0), (i * 32, 0, 32, 32))
            frames[state].append(pygame.transform.scale(surf, (32 * self.scale_factor, 32 * self.scale_factor)))
        return frames

    def update(self, dt, player, platforms):
        # Gravity
        self.vel.y += self.gravity * dt
        
        # AI Logic
        dist = (pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)).length()
        
        if dist < self.config["chase_radius"]:
            self.state = "WALK"
            if player.rect.centerx > self.rect.centerx:
                self.vel.x = self.config["speed"]
                self.facing_right = True
            else:
                self.vel.x = -self.config["speed"]
                self.facing_right = False
        else:
            self.state = "IDLE"
            self.vel.x = 0

        # Movement
        self.pos.x += self.vel.x * dt
        self.rect.x = round(self.pos.x)
        self.check_collisions(platforms, 'horizontal')
        
        self.pos.y += self.vel.y * dt
        self.rect.y = round(self.pos.y)
        self.check_collisions(platforms, 'vertical')
        
        self.animate(dt)

    def check_collisions(self, platforms, direction):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == 'horizontal':
                    if self.vel.x > 0:
                        self.rect.right = platform.rect.left
                        self.pos.x = self.rect.x
                    elif self.vel.x < 0:
                        self.rect.left = platform.rect.right
                        self.pos.x = self.rect.x
                else:
                    if self.vel.y > 0:
                        self.rect.bottom = platform.rect.top
                        self.pos.y = self.rect.y
                        self.vel.y = 0
                        self.on_ground = True
                    elif self.vel.y < 0:
                        self.rect.top = platform.rect.bottom
                        self.pos.y = self.rect.y
                        self.vel.y = 0

    def animate(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= 1.0 / self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames[self.state])
            
        self.image = self.frames[self.state][self.frame_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

class Tom(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, TOM_PATH)

class Broom(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, BROOM_PATH)
