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
        self.scale_factor = 3
        self.frames = self.load_frames()
        
        self.state = "PATROL" # PATROL, CHASE, LOST
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
        
        # Patrol settings
        self.start_x = x
        self.patrol_dist = self.config.get("patrol_distance", 200.0)
        self.patrol_dir = 1 # 1 right, -1 left
        
        # Timers
        self.lost_timer = 0
        self.lost_pause_duration = 2.0

    def load_frames(self):
        frames = {"IDLE": [], "WALK": []}
        for i, state in enumerate(["IDLE", "WALK"]):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            surf.blit(self.sprite_sheet, (0, 0), (i * 32, 0, 32, 32))
            frames[state].append(pygame.transform.scale(surf, (32 * self.scale_factor, 32 * self.scale_factor)))
        return frames

    def update(self, dt, player, platforms, decoys=None):
        # 1. Gravity
        self.vel.y += self.gravity * dt
        
        # 2. Logic based on distance to player OR decoys
        target_pos = pygame.Vector2(player.rect.center)
        target_dist = (target_pos - pygame.Vector2(self.rect.center)).length()
        is_chasing_decoy = False
        
        # Decoys attract enemies even more than player
        if decoys and len(decoys) > 0:
            # Get the latest decoy (last in group)
            latest_decoy = decoys.sprites()[-1]
            decoy_pos = pygame.Vector2(latest_decoy.rect.center)
            decoy_dist = (decoy_pos - pygame.Vector2(self.rect.center)).length()
            
            # If decoy is within attraction radius, prioritize it!
            if decoy_dist < self.config["chase_radius"] * 1.5:
                target_pos = decoy_pos
                target_dist = decoy_dist
                is_chasing_decoy = True
        
        if target_dist < self.config["chase_radius"] or is_chasing_decoy:
            # Switch to chase
            self.state = "CHASE"
            self.lost_timer = 0
        elif self.state == "CHASE":
            # Just lost target
            self.state = "LOST"
            self.lost_timer = 0
            self.vel.x = 0

        # 3. Action based on current state
        if self.state == "CHASE":
            # Chase target (player or decoy)
            if abs(target_pos.x - self.rect.centerx) > 10:
                self.patrol_dir = 1 if target_pos.x > self.rect.centerx else -1
                self.vel.x = self.config["speed"] * self.patrol_dir
                self.facing_right = (self.patrol_dir == 1)
            else:
                self.vel.x = 0
        
        elif self.state == "LOST":
            # Stay still for a bit
            self.vel.x = 0
            self.lost_timer += dt
            if self.lost_timer >= self.lost_pause_duration:
                self.state = "PATROL"
                # Keep current facing for patrol start
                self.patrol_dir = 1 if self.facing_right else -1
        
        elif self.state == "PATROL":
            # Normal patrol
            self.vel.x = self.config["speed"] * self.patrol_dir
            self.facing_right = (self.patrol_dir == 1)
            
            # 3.1 Edge Detection (Don't fall off during patrol)
            # Only if on ground
            if self.on_ground:
                # Check point ahead and below
                look_ahead_x = self.rect.right + 5 if self.patrol_dir == 1 else self.rect.left - 5
                look_ahead_rect = pygame.Rect(look_ahead_x, self.rect.bottom + 5, 1, 1)
                
                any_platform_ahead = False
                for platform in platforms:
                    if look_ahead_rect.colliderect(platform.rect):
                        any_platform_ahead = True
                        break
                
                if not any_platform_ahead:
                    self.patrol_dir *= -1
                    self.vel.x = 0 # Stop for this frame
            
            # 3.2 Boundary check
            if self.patrol_dir == 1 and self.pos.x >= self.start_x + self.patrol_dist:
                self.patrol_dir = -1
            elif self.patrol_dir == -1 and self.pos.x <= self.start_x:
                self.patrol_dir = 1

        # 4. Movement execution
        # Horizontal
        self.pos.x += self.vel.x * dt
        self.rect.x = round(self.pos.x)
        if self.check_collisions(platforms, 'horizontal'):
            if self.state == "PATROL":
                self.patrol_dir *= -1
            
        # Vertical
        self.pos.y += self.vel.y * dt
        self.rect.y = round(self.pos.y)
        self.check_collisions(platforms, 'vertical')
        
        # 5. Out of bounds check (Cleanup if really fell off)
        if self.pos.y > 2000: # Far below the map
            self.kill()
            
        self.update_animations(dt)

    def update_animations(self, dt):
        # Choose anim state
        anim_state = "IDLE" if abs(self.vel.x) < 1 else "WALK"
        
        self.animation_timer += dt
        if self.animation_timer >= 1.0 / self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames[anim_state])
            
        self.image = self.frames[anim_state][self.frame_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def check_collisions(self, platforms, direction):
        hit = False
        if direction == 'vertical':
            self.on_ground = False # Reset ground state before vertical check

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                hit = True
                if direction == 'horizontal':
                    if self.vel.x > 0:
                        self.rect.right = platform.rect.left
                    elif self.vel.x < 0:
                        self.rect.left = platform.rect.right
                    self.pos.x = float(self.rect.x) # Sync position!
                else:
                    if self.vel.y > 0:
                        self.rect.bottom = platform.rect.top
                        self.vel.y = 0
                        self.on_ground = True
                    elif self.vel.y < 0:
                        self.rect.top = platform.rect.bottom
                        self.vel.y = 0
                    self.pos.y = float(self.rect.y) # Sync position!
        return hit

class Tom(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, TOM_PATH)

class Broom(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, BROOM_PATH)
