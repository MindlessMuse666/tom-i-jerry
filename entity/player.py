import pygame
import tomllib
import os
from constant import PLAYER_PATH
from core.resource import resource_manager

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Load config
        config_path = os.path.join("config", "player.toml")
        with open(config_path, "rb") as f:
            self.config = tomllib.load(f)
            
        # Physics parameters
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, self.config["gravity"])
        self.speed = self.config["speed"]
        self.jump_force = self.config["jump_force"]
        
        # Animation
        self.sprite_sheet = resource_manager.get_image(PLAYER_PATH)
        self.scale_factor = 3 # Scale player 2x
        self.frames = self.load_frames()
        self.state = "IDLE"
        self.frame_index = 0
        self.animation_speed = 8 # frames per second
        self.animation_timer = 0
        self.facing_right = True
        
        self.image = self.frames["IDLE"][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-20, -8) # Adjusted hitbox for 2x scale
        
        # Stats
        self.health = self.config["max_health"]
        self.is_invulnerable = False
        self.invulnerability_timer = 0
        self.visible = True
        self.blink_timer = 0
        
        self.on_ground = False
        self.current_platform = None

    def load_frames(self):
        frames = {
            "IDLE": [],
            "WALK": [],
            "JUMP": [],
            "HURT": []
        }
        
        # Row 1 (y=0): Idle (2 frames)
        for i in range(2):
            frames["IDLE"].append(self.get_frame(i, 0))
            
        # Row 2 (y=1): Walk (2 frames), 1st frame is also for Jump
        for i in range(2):
            frames["WALK"].append(self.get_frame(i, 1))
        
        # Jump is first frame of row 2
        frames["JUMP"].append(self.get_frame(0, 1))
            
        # Row 3 (y=2): Hurt (1 frame)
        frames["HURT"].append(self.get_frame(0, 2))
        
        return frames

    def get_frame(self, col, row):
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        surf.blit(self.sprite_sheet, (0, 0), (col * 32, row * 32, 32, 32))
        # Scale the frame
        new_size = (int(32 * self.scale_factor), int(32 * self.scale_factor))
        return pygame.transform.scale(surf, new_size)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel.x = 0
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel.x = -self.speed
            self.facing_right = False
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel.x = self.speed
            self.facing_right = True
            
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel.y = self.jump_force
            self.on_ground = False

    def update(self, dt, platforms):
        # Apply gravity
        self.vel.y += self.acc.y * dt
        
        # Move horizontal
        self.pos.x += self.vel.x * dt
        # Add moving platform velocity
        if self.on_ground and hasattr(self.current_platform, 'vel'):
            self.pos.x += self.current_platform.vel.x * dt
            
        self.rect.x = round(self.pos.x)
        self.check_collisions(platforms, 'horizontal')
        
        # Move vertical
        self.pos.y += self.vel.y * dt
        if self.on_ground and hasattr(self.current_platform, 'vel'):
            self.pos.y += self.current_platform.vel.y * dt
            
        self.rect.y = round(self.pos.y)
        self.check_collisions(platforms, 'vertical')
        
        self.update_state()
        self.animate(dt)
        self.update_invulnerability(dt)

    def check_collisions(self, platforms, direction):
        if direction == 'horizontal':
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.vel.x > 0:
                        self.rect.right = platform.rect.left
                        self.pos.x = self.rect.x
                    elif self.vel.x < 0:
                        self.rect.left = platform.rect.right
                        self.pos.x = self.rect.x
        else:
            self.on_ground = False
            self.current_platform = None
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.vel.y > 0:
                        self.rect.bottom = platform.rect.top
                        self.pos.y = self.rect.y
                        self.vel.y = 0
                        self.on_ground = True
                        self.current_platform = platform
                    elif self.vel.y < 0:
                        self.rect.top = platform.rect.bottom
                        self.pos.y = self.rect.y
                        self.vel.y = 0

    def update_state(self):
        new_state = "IDLE"
        if not self.on_ground:
            new_state = "JUMP"
        elif abs(self.vel.x) > 0.1: # Use small threshold
            new_state = "WALK"
        
        if new_state != self.state:
            self.state = new_state
            self.frame_index = 0
            self.animation_timer = 0

    def animate(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= 1.0 / self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames[self.state])
            
        self.image = self.frames[self.state][self.frame_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def update_invulnerability(self, dt):
        if self.is_invulnerable:
            self.invulnerability_timer -= dt
            self.blink_timer += dt
            if self.blink_timer >= 0.1:
                self.blink_timer = 0
                self.visible = not self.visible
            
            if self.invulnerability_timer <= 0:
                self.is_invulnerable = False
                self.visible = True
        else:
            self.visible = True

    def take_damage(self, amount=1):
        if not self.is_invulnerable:
            self.health -= amount
            self.is_invulnerable = True
            self.invulnerability_timer = self.config["invulnerability_time"]
            if self.health <= 0:
                self.health = 0
                # Handle death?
            return True
        return False

    def draw(self, screen, offset):
        if self.visible:
            draw_pos = self.rect.topleft - offset
            screen.blit(self.image, draw_pos)
