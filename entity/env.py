import pygame
import os
from core.resource import resource_manager
from core.mixer import mixer
from constant import (
    PLATFORM_PATH, MOVING_PLATFORM_PATH, GROUND_PATH,
    CHEESE_PATH, TRAP_PATH, CRATE_PATH,
    SFX_CHEESE, SFX_TRAP_SNAP, SFX_CRATE_BREAK
)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path=PLATFORM_PATH):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        tile_img = resource_manager.get_image(image_path)
        
        # Scaling tiles
        self.tile_scale = 2 # Scale tiles 2x (64x64)
        scaled_tile = pygame.transform.scale(tile_img, (32 * self.tile_scale, 32 * self.tile_scale))
        tile_size = 32 * self.tile_scale
        
        # Tile the image
        for ty in range(0, height, tile_size):
            for tx in range(0, width, tile_size):
                self.image.blit(scaled_tile, (tx, ty))
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

class Cheese(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = resource_manager.get_image(CHEESE_PATH)
        # Jerry is scale 3, so cheese should be scale 2 or 3
        self.image = pygame.transform.scale(img, (64, 64))
        self.rect = self.image.get_rect(topleft=(x, y))

    def collect(self):
        mixer.play_sfx(resource_manager.get_sound(SFX_CHEESE))
        self.kill()

class Trap(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = resource_manager.get_image(TRAP_PATH)
        self.scale_factor = 3 # Increased scale
        self.frames = self.load_frames()
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.active = True
        self.alpha = 255
        self.fade_speed = 200 # alpha per second

    def load_frames(self):
        frames = []
        for i in range(2):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            surf.blit(self.sprite_sheet, (0, 0), (i * 32, 0, 32, 32))
            frames.append(pygame.transform.scale(surf, (32 * self.scale_factor, 32 * self.scale_factor)))
        return frames

    def activate(self):
        if self.active:
            self.active = False
            self.image = self.frames[1]
            mixer.play_sfx(resource_manager.get_sound(SFX_TRAP_SNAP))

    def update(self, dt):
        if not self.active:
            self.alpha -= self.fade_speed * dt
            if self.alpha <= 0:
                self.kill()
            else:
                self.image.set_alpha(int(self.alpha))

class Crate(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = resource_manager.get_image(CRATE_PATH)
        self.scale_factor = 2 # Reverted to 2x scale (64x64)
        self.frames = self.load_frames()
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.gravity = 1200
        self.friction = 500
        self.is_broken = False
        self.activated_by_player = False
        self.broken_timer = 0
        self.broken_duration = 1.0 # Duration before chips disappear

    def load_frames(self):
        frames = []
        for i in range(2):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            surf.blit(self.sprite_sheet, (0, 0), (i * 32, 0, 32, 32))
            frames.append(pygame.transform.scale(surf, (32 * self.scale_factor, 32 * self.scale_factor)))
        return frames

    def update(self, dt, platforms):
        if self.is_broken:
            self.broken_timer += dt
            if self.broken_timer >= self.broken_duration:
                self.kill()
            else:
                # Fade out effect
                alpha = max(0, 255 * (1 - self.broken_timer / self.broken_duration))
                self.image.set_alpha(int(alpha))
            return

        # Gravity
        self.vel.y += self.gravity * dt
        
        # Apply friction
        if self.vel.x > 0:
            self.vel.x = max(0, self.vel.x - self.friction * dt)
        elif self.vel.x < 0:
            self.vel.x = min(0, self.vel.x + self.friction * dt)

        # Movement
        self.pos.x += self.vel.x * dt
        self.rect.x = round(self.pos.x)
        self.check_collisions(platforms, 'horizontal')
        
        self.pos.y += self.vel.y * dt
        self.rect.y = round(self.pos.y)
        self.check_collisions(platforms, 'vertical')

    def check_collisions(self, platforms, direction):
        for platform in platforms:
            if platform == self: continue
            if self.rect.colliderect(platform.rect):
                if direction == 'horizontal':
                    if self.vel.x > 0:
                        self.rect.right = platform.rect.left
                        self.pos.x = self.rect.x
                        self.vel.x = 0
                    elif self.vel.x < 0:
                        self.rect.left = platform.rect.right
                        self.pos.x = self.rect.x
                        self.vel.x = 0
                else:
                    if self.vel.y > 0:
                        self.rect.bottom = platform.rect.top
                        self.pos.y = self.rect.y
                        self.vel.y = 0
                    elif self.vel.y < 0:
                        self.rect.top = platform.rect.bottom
                        self.pos.y = self.rect.y
                        self.vel.y = 0

    def break_crate(self):
        if not self.is_broken:
            self.is_broken = True
            self.image = self.frames[1]
            mixer.play_sfx(resource_manager.get_sound(SFX_CRATE_BREAK))
            # Spawn cheese logic should be in scene
            return True
        return False
