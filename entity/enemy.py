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
            self.config = {
                "speed": 150.0,
                "chase_radius": 400.0,
                "health": 1,
                "damage": 1,
                "patrol_distance": 200.0
            }
        else:
            with open(config_path, "rb") as f:
                self.config = tomllib.load(f)
                
        self.sprite_sheet = resource_manager.get_image(image_path)
        self.scale_factor = 3 # Increased scale
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
        
        # Patrol logic
        self.start_x = x
        self.patrol_dist = self.config.get("patrol_distance", 200.0)
        self.patrol_dir = 1 # 1 for right, -1 for left
        
        # AI state
        self.target_player = None
        self.lost_timer = 0
        self.lost_pause_duration = 2.0
        self.is_paused = False

    def load_frames(self):
        frames = {"IDLE": [], "WALK": []}
        for i, state in enumerate(["IDLE", "WALK"]):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            surf.blit(self.sprite_sheet, (0, 0), (i * 32, 0, 32, 32))
            frames[state].append(pygame.transform.scale(surf, (32 * self.scale_factor, 32 * self.scale_factor)))
        return frames

    def update(self, dt, player, platforms):
        # Gravity
        self.vel.y += self.gravity * dt
        
        # AI Logic
        dist_vec = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        dist = dist_vec.length()
        
        if dist < self.config["chase_radius"]:
            # Chasing player
            self.state = "WALK"
            self.is_paused = False
            self.lost_timer = 0
            
            # Using 10px buffer to prevent rapid switching when overlapping
            if abs(player.rect.centerx - self.rect.centerx) > 10:
                if player.rect.centerx > self.rect.centerx:
                    self.vel.x = self.config["speed"]
                    self.facing_right = True
                    self.patrol_dir = 1
                else:
                    self.vel.x = -self.config["speed"]
                    self.facing_right = False
                    self.patrol_dir = -1
        else:
            # Player lost or not in range
            if not self.is_paused and self.state == "WALK" and dist >= self.config["chase_radius"]:
                # Just lost player
                self.is_paused = True
                self.lost_timer = 0
                self.state = "IDLE"
                self.vel.x = 0
            
            if self.is_paused:
                self.lost_timer += dt
                if self.lost_timer >= self.lost_pause_duration:
                    self.is_paused = False
                    # Use current facing to decide patrol direction
                    self.patrol_dir = 1 if self.facing_right else -1
            else:
                # Patrol logic
                self.state = "WALK"
                self.vel.x = self.config["speed"] * self.patrol_dir
                self.facing_right = (self.patrol_dir == 1)
                
                # Check patrol boundaries
                if self.patrol_dir == 1 and self.pos.x >= self.start_x + self.patrol_dist:
                    self.patrol_dir = -1
                    self.facing_right = False
                elif self.patrol_dir == -1 and self.pos.x <= self.start_x:
                    self.patrol_dir = 1
                    self.facing_right = True

        # Movement - Horizontal
        self.pos.x += self.vel.x * dt
        self.rect.x = round(self.pos.x)
        if self.check_collisions(platforms, 'horizontal'):
            # If hit a wall during patrol, reverse direction
            if not self.is_paused and dist >= self.config["chase_radius"]:
                self.patrol_dir *= -1
                self.facing_right = (self.patrol_dir == 1)
        
        # Movement - Vertical
        self.pos.y += self.vel.y * dt
        self.rect.y = round(self.pos.y)
        self.check_collisions(platforms, 'vertical')
        
        self.animate(dt)

    def check_collisions(self, platforms, direction):
        hit = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                hit = True
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
        return hit

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
