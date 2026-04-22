try:
    import tomllib
except ImportError:
    import tomli as tomllib
import os

import pygame
from core.resource import resource_manager
from core.mixer import mixer
from constant import TOM_PATH, BROOM_PATH, BOSS_PATH, SFX_HURT, SFX_TOM_DEATH, SFX_BOSS_DEATH

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, frame_w=32, frame_h=32):
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
        self.frames = self.load_frames(frame_w, frame_h)
        
        self.state = "PATROL" # PATROL, CHASE, LOST
        self.frame_index = 0
        self.animation_speed = 6
        self.animation_timer = 0
        self.facing_right = True
        
        self.image = self.frames["IDLE"][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.spawn_pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.gravity = 1200
        
        self.on_ground = False
        self.health = self.config["health"]
        self.fell_off = False # Flag for LevelScene

        # Patrol settings
        self.start_x = x
        self.patrol_dist = self.config.get("patrol_distance", 200.0)
        self.patrol_dir = 1 # 1 right, -1 left
        
        # Timers
        self.lost_timer = 0
        self.lost_pause_duration = 2.0

    def load_frames(self, w, h):
        frames = {"IDLE": [], "WALK": []}
        # Both IDLE and WALK are in Row 1 (y=0)
        # IDLE is Frame 1 (col=0), WALK is Frame 2 (col=1)
        
        # IDLE (Frame 1)
        surf_idle = pygame.Surface((w, h), pygame.SRCALPHA)
        surf_idle.blit(self.sprite_sheet, (0, 0), (0, 0, w, h))
        frames["IDLE"].append(pygame.transform.scale(surf_idle, (w * self.scale_factor, h * self.scale_factor)))
        
        # WALK (Frame 2)
        surf_walk = pygame.Surface((w, h), pygame.SRCALPHA)
        surf_walk.blit(self.sprite_sheet, (0, 0), (w, 0, w, h))
        frames["WALK"].append(pygame.transform.scale(surf_walk, (w * self.scale_factor, h * self.scale_factor)))
        
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
            self.fell_off = True
            # self.kill() is now handled by LevelScene to spawn cheese
            
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
        # Tom: cell 28x29
        super().__init__(x, y, TOM_PATH, frame_w=28, frame_h=29)

class Broom(Enemy):
    def __init__(self, x, y):
        # Broom: cell 22x36
        super().__init__(x, y, BROOM_PATH, frame_w=22, frame_h=36)

class BossTom(pygame.sprite.Sprite):
    """
    Boss Tom with advanced AI and movement cycles.
    """
    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = resource_manager.get_image(BOSS_PATH)
        self.scale_factor = 3
        self.frames = self.load_frames()
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8 # Faster animation for boss
        
        self.start_pos = pygame.Vector2(x, y)
        self.pos = pygame.Vector2(x, y)
        
        # States: MOVE_RIGHT, ROCKETS, MOVE_CENTER, WAIT_LEFT, MOVE_LEFT, CRATES, MOVE_CENTER, WAIT_RIGHT
        self.state = "MOVE_RIGHT"
        self.image = self.frames["IDLE"][0]
        self.rect = self.image.get_rect(center=(x, y))
        
        self.timer = 0
        self.attack_timer = 0
        self.move_speed = 200
        self.facing_right = True
        
        # Timings
        self.wait_duration = 0.5
        self.phase_duration = 6.0
        self.rocket_cooldown = 1.0
        self.crate_cooldown = 0.8

    def load_frames(self):
        # 128x64 sprite sheet, two 64x64 frames
        frames = {"IDLE": [], "MOVE": [], "ACTION": []}
        for i in range(2):
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            surf.blit(self.sprite_sheet, (0, 0), (i * 64, 0, 64, 64))
            scaled = pygame.transform.scale(surf, (64 * self.scale_factor, 64 * self.scale_factor))
            frames["IDLE"].append(scaled)
            frames["MOVE"].append(scaled)
            frames["ACTION"].append(scaled)
        return frames

    def update(self, dt, player, projectile_group, crate_group):
        self.timer += dt
        
        # 1. Update facing direction (Always face player)
        self.facing_right = (player.rect.centerx > self.rect.centerx)
        
        # 2. State Logic
        if self.state == "MOVE_RIGHT":
            target_x = self.start_pos.x + 300
            self.move_towards(target_x, dt)
            if abs(self.pos.x - target_x) < 5:
                self.state = "ROCKETS"
                self.timer = 0
                self.attack_timer = 0
        
        elif self.state == "ROCKETS":
            self.attack_timer += dt
            if self.attack_timer >= self.rocket_cooldown:
                self.fire_rocket(player, projectile_group)
                self.attack_timer = 0
            if self.timer >= self.phase_duration:
                self.state = "MOVE_CENTER_FROM_RIGHT"
        
        elif self.state == "MOVE_CENTER_FROM_RIGHT":
            self.move_towards(self.start_pos.x, dt)
            if abs(self.pos.x - self.start_pos.x) < 5:
                self.state = "WAIT_LEFT"
                self.timer = 0
        
        elif self.state == "WAIT_LEFT":
            if self.timer >= self.wait_duration:
                self.state = "MOVE_LEFT"
        
        elif self.state == "MOVE_LEFT":
            target_x = self.start_pos.x - 300
            self.move_towards(target_x, dt)
            if abs(self.pos.x - target_x) < 5:
                self.state = "CRATES"
                self.timer = 0
                self.attack_timer = 0
        
        elif self.state == "CRATES":
            self.attack_timer += dt
            if self.attack_timer >= self.crate_cooldown:
                self.drop_crate(player, crate_group)
                self.attack_timer = 0
            if self.timer >= self.phase_duration:
                self.state = "MOVE_CENTER_FROM_LEFT"
        
        elif self.state == "MOVE_CENTER_FROM_LEFT":
            self.move_towards(self.start_pos.x, dt)
            if abs(self.pos.x - self.start_pos.x) < 5:
                self.state = "WAIT_RIGHT"
                self.timer = 0
        
        elif self.state == "WAIT_RIGHT":
            if self.timer >= self.wait_duration:
                self.state = "MOVE_RIGHT"

        # 3. Animation
        self.animate(dt)
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def move_towards(self, target_x, dt):
        if self.pos.x < target_x:
            self.pos.x = min(target_x, self.pos.x + self.move_speed * dt)
        elif self.pos.x > target_x:
            self.pos.x = max(target_x, self.pos.x - self.move_speed * dt)

    def animate(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= 1.0 / self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % 2
            
        # Get frame 0 or 1
        base_img = self.frames["IDLE"][self.frame_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(base_img, True, False)
        else:
            self.image = base_img

    def fire_rocket(self, player, projectile_group):
        from entity.projectile import Rocket
        # Target player's current center
        rocket = Rocket(self.rect.centerx, self.rect.centery, player.rect.center)
        projectile_group.add(rocket)

    def drop_crate(self, player, crate_group):
        from entity.env import Crate
        import random
        drop_x = player.rect.centerx + random.randint(-100, 100)
        drop_x = max(64, min(1216, drop_x))
        # Boss crates: scale 3.0 (1.5x larger than normal 2.0), faster fall
        crate = Crate(drop_x, -100, scale=3.0)
        crate.is_boss_crate = True
        crate.gravity = 800 # Slightly faster fall than 600
        crate_group.add(crate)
