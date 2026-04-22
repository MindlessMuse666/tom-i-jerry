import pygame
try:
    import tomllib
except ImportError:
    import tomli as tomllib
import os
from constant import PLAYER_PATH, SFX_DECOY_THROW
from core.resource import resource_manager
from core.mixer import mixer

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
        self.scale_factor = 3 # Scaling
        self.frames = {}
        self.mirrored_frames = {}
        self.load_all_frames()
        
        self.state = "IDLE"
        self.frame_index = 0
        self.animation_speed = 4 # Reduced animation speed for organic look
        self.animation_timer = 0
        self.facing_right = True
        
        self.image = self.frames["IDLE"][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-20, -8)
        
        # Stats
        self.health = self.config["max_health"]
        self.is_invulnerable = False
        self.invulnerability_timer = 0
        self.visible = True
        self.blink_timer = 0
        
        self.on_ground = False
        self.current_platform = None
        
        # Decoy throw logic
        self.decoy_cooldown = 0
        self.throw_force = 1000 # Base force for throwing

    def load_all_frames(self):
        states = ["IDLE", "WALK", "JUMP", "HURT"]
        for state in states:
            self.frames[state] = []
            self.mirrored_frames[state] = []
            
        # Row 1 (y=0): Idle (2 frames, each 22x28)
        for i in range(2):
            frame = self.get_frame(i, 0, 22, 28)
            self.frames["IDLE"].append(frame)
            self.mirrored_frames["IDLE"].append(pygame.transform.flip(frame, True, False))
            
        # Row 2 (y=1): Walk (2 frames, each 22x28)
        for i in range(2):
            frame = self.get_frame(i, 1, 22, 28)
            self.frames["WALK"].append(frame)
            self.mirrored_frames["WALK"].append(pygame.transform.flip(frame, True, False))
        
        # Jump is first frame of row 2
        jump_frame = self.frames["WALK"][0]
        self.frames["JUMP"].append(jump_frame)
        self.mirrored_frames["JUMP"].append(pygame.transform.flip(jump_frame, True, False))
            
        # Row 3 (y=2): Hurt (1 frame, 22x28)
        hurt_frame = self.get_frame(0, 2, 22, 28)
        self.frames["HURT"].append(hurt_frame)
        self.mirrored_frames["HURT"].append(pygame.transform.flip(hurt_frame, True, False))

    def get_frame(self, col, row, width, height):
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.blit(self.sprite_sheet, (0, 0), (col * width, row * height, width, height))
        new_size = (int(width * self.scale_factor), int(height * self.scale_factor))
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
        # 1. Handle moving platform displacement (if standing on one)
        if self.on_ground and self.current_platform and hasattr(self.current_platform, 'vel'):
            platform_displacement = self.current_platform.vel * dt
            self.pos += platform_displacement
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # 2. Apply gravity and own movement
        # Improve gravity: heavier when falling, slightly floaty at peak
        gravity = self.acc.y
        if self.vel.y > 0: # Falling
             gravity *= 1.5
        elif self.vel.y < 0 and abs(self.vel.y) < 100: # Peak of jump
             gravity *= 0.5
             
        self.vel.y += gravity * dt
        
        # Move horizontal
        self.pos.x += self.vel.x * dt
        self.rect.x = round(self.pos.x)
        self.check_collisions(platforms, 'horizontal')
        
        # Move vertical
        self.pos.y += self.vel.y * dt
        self.rect.y = round(self.pos.y)
        self.check_collisions(platforms, 'vertical')
        
        # 4. Final check: if we are not colliding anymore, we are not on ground
        # This prevents flickering on moving platforms
        if self.on_ground and self.current_platform:
            # Check if we are still "touching" the current platform with a 2px buffer
            test_rect = self.rect.copy()
            test_rect.y += 2
            if not test_rect.colliderect(self.current_platform.rect):
                self.on_ground = False
                self.current_platform = None
        
        self.update_state()
        self.animate(dt)
        self.update_invulnerability(dt)
        
        # Cooldown for throwing
        if self.decoy_cooldown > 0:
            self.decoy_cooldown -= dt

    def throw_decoy(self, decoys_group, target_pos=None):
        """
        Jerry throws a cheese decoy towards target_pos (world coordinates).
        If target_pos is None, throws in facing direction.
        """
        if self.decoy_cooldown <= 0:
            from entity.projectile import Decoy
            # Initial position: Jerry's center
            start_x = self.rect.centerx
            start_y = self.rect.centery
            
            if target_pos:
                # Calculate direction vector to target
                target_vec = pygame.Vector2(target_pos) - pygame.Vector2(start_x, start_y)
                if target_vec.length() > 0:
                    # Normalize and scale by throw force
                    # We also want a slight upward arc, but if user points somewhere, we follow that
                    # Limit force to prevent too fast projectiles
                    force = min(target_vec.length() * 2, self.throw_force)
                    velocity = target_vec.normalize() * force
                    vx, vy = velocity.x, velocity.y
                else:
                    vx, vy = 0, 0
            else:
                # Default throw if no target (fallback)
                vx = self.throw_force * 0.8 if self.facing_right else -self.throw_force * 0.8
                vy = -self.throw_force * 0.4
            
            decoy = Decoy(start_x, start_y, vx, vy)
            decoys_group.add(decoy)
            
            # Play throw sound
            mixer.play_sfx(resource_manager.get_sound(SFX_DECOY_THROW))
            
            self.decoy_cooldown = 0.5 # 0.5 seconds between throws
            return True
        return False

    def check_collisions(self, platforms, direction):
        if direction == 'horizontal':
            for platform in platforms:
                # Skip horizontal collision with the platform we are standing on 
                if platform == self.current_platform:
                    continue
                    
                if self.rect.colliderect(platform.rect):
                    # Handle Crate pushing
                    if hasattr(platform, 'vel') and not hasattr(platform, 'path'): # It's a crate
                        platform.vel.x = self.vel.x
                        platform.activated_by_player = True
                    
                    if self.vel.x > 0:
                        self.rect.right = platform.rect.left
                        self.pos.x = self.rect.x
                    elif self.vel.x < 0:
                        self.rect.left = platform.rect.right
                        self.pos.x = self.rect.x
        else:
            # Vertical collisions
            # We don't reset self.on_ground here to prevent flickering
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.vel.y > 0: # Falling or standing
                        self.rect.bottom = platform.rect.top
                        self.pos.y = self.rect.y
                        self.vel.y = 0
                        self.on_ground = True
                        self.current_platform = platform
                    elif self.vel.y < 0: # Jumping up
                        self.rect.top = platform.rect.bottom
                        self.pos.y = self.rect.y
                        self.vel.y = 0
                        # If we hit a ceiling, we might be hitting a platform from below
                        if self.current_platform == platform:
                             self.on_ground = False
                             self.current_platform = None

    def update_state(self):
        # Determine the next state
        if not self.on_ground:
            new_state = "JUMP"
        elif abs(self.vel.x) > 10.0: # Using a larger threshold for "moving"
            new_state = "WALK"
        else:
            new_state = "IDLE"
        
        # Only reset animation if the state actually changes
        if new_state != self.state:
            self.state = new_state
            self.frame_index = 0
            self.animation_timer = 0

    def animate(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= 1.0 / self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames[self.state])
            
        if self.facing_right:
            self.image = self.frames[self.state][self.frame_index]
        else:
            self.image = self.mirrored_frames[self.state][self.frame_index]

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
            from core.mixer import mixer
            from core.resource import resource_manager
            from constant import SFX_HURT
            mixer.play_sfx(resource_manager.get_sound(SFX_HURT))
            if self.health <= 0:
                self.health = 0
            return True
        return False

    def draw(self, screen, offset):
        if self.visible:
            draw_pos = self.rect.topleft - offset
            screen.blit(self.image, draw_pos)
