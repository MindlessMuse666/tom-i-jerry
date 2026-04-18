import pygame
import json
import os
from scene.base import Scene
from entity.player import Player
from entity.env import Platform, MovingPlatform
from core.camera import Camera
from core.resource import resource_manager
from core.mixer import mixer
from ui.hud import HUD

class LevelScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.level_data = None
        self.camera = None
        self.player = None
        self.platforms = pygame.sprite.Group()
        self.moving_platforms = pygame.sprite.Group()
        self.cheeses = pygame.sprite.Group() # To be implemented
        self.hud = HUD()
        
        # Game stats for HUD
        self.total_cheese = 0
        self.scale_cheese = 0
        
        self.background = None
        self.bg_width = 0

    def enter(self, level_id=1):
        self.load_level(level_id)
        mixer.play_music(self.level_data["music"])

    def load_level(self, level_id):
        path = os.path.join("level", f"level{level_id}.json")
        with open(path, "r") as f:
            self.level_data = json.load(f)
            
        self.camera = Camera(self.level_data["width"], self.level_data["height"])
        
        # Background
        self.background = resource_manager.get_image(self.level_data["background"])
        self.bg_width = self.background.get_width()
        
        # Spawn player
        spawn = self.level_data["spawn_point"]
        self.player = Player(spawn[0], spawn[1])
        
        # Load platforms
        self.platforms.empty()
        for p in self.level_data["platforms"]:
            self.platforms.add(Platform(p[0], p[1], p[2], p[3]))
            
        self.moving_platforms.empty()
        for mp in self.level_data["moving_platforms"]:
            self.moving_platforms.add(MovingPlatform(mp["x"], mp["y"], mp["width"], mp["height"], mp["path"], mp["speed"]))
            
        # Initial cheese
        self.total_cheese = 0
        self.scale_cheese = 0
        # Cheese implementation will come in next stage, but we can add placeholders

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.state_machine.set_state("MENU") # Should be PAUSE
        
        self.player.handle_input()

    def update(self, dt):
        self.moving_platforms.update(dt)
        
        # Combine all solid platforms for player collision
        all_platforms = list(self.platforms) + list(self.moving_platforms)
        self.player.update(dt, all_platforms)
        
        self.camera.update(self.player.rect)

    def draw(self, screen):
        # Draw parallax background
        # 0.5 parallax factor
        bg_offset = -(self.camera.offset.x * 0.5) % self.bg_width
        screen.blit(self.background, (bg_offset - self.bg_width, 0))
        screen.blit(self.background, (bg_offset, 0))
        screen.blit(self.background, (bg_offset + self.bg_width, 0))
        
        # Draw entities with camera offset
        for platform in self.platforms:
            screen.blit(platform.image, platform.rect.topleft - self.camera.offset)
            
        for mp in self.moving_platforms:
            screen.blit(mp.image, mp.rect.topleft - self.camera.offset)
            
        self.player.draw(screen, self.camera.offset)
        
        # HUD
        self.hud.draw(screen, self.player.health, self.player.config["max_health"], self.total_cheese, self.scale_cheese)
