import pygame
import json
import os
from scene.base import Scene
from entity.player import Player
from entity.env import Platform, MovingPlatform, Cheese, Trap, Crate
from entity.enemy import Tom, Broom
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
        self.cheeses = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()
        self.crates = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
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
        
        # Background - scale to screen height 720
        raw_bg = resource_manager.get_image(self.level_data["background"])
        bg_height = 720
        bg_aspect = raw_bg.get_width() / raw_bg.get_height()
        bg_width = int(bg_height * bg_aspect)
        self.background = pygame.transform.scale(raw_bg, (bg_width, bg_height))
        self.bg_width = self.background.get_width()
        
        # Spawn player
        spawn = self.level_data["spawn_point"]
        self.player = Player(spawn[0], spawn[1])
        
        # Load platforms
        self.platforms.empty()
        from constant import GROUND_PATH
        for i, p in enumerate(self.level_data["platforms"]):
            # Use GROUND_PATH for the first platform (ground) or any very wide platform
            path = GROUND_PATH if i == 0 or p[2] > 1000 else None
            if path:
                self.platforms.add(Platform(p[0], p[1], p[2], p[3], image_path=path))
            else:
                self.platforms.add(Platform(p[0], p[1], p[2], p[3]))
            
        self.moving_platforms.empty()
        for mp in self.level_data["moving_platforms"]:
            self.moving_platforms.add(MovingPlatform(mp["x"], mp["y"], mp["width"], mp["height"], mp["path"], mp["speed"]))
            
        # Load Cheeses
        self.cheeses.empty()
        for c in self.level_data["cheeses"]:
            self.cheeses.add(Cheese(c[0], c[1]))
            
        # Load Traps
        self.traps.empty()
        for t in self.level_data["traps"]:
            self.traps.add(Trap(t[0], t[1]))
            
        # Load Crates
        self.crates.empty()
        for cr in self.level_data["crates"]:
            self.crates.add(Crate(cr[0], cr[1]))
            
        # Load Enemies
        self.enemies.empty()
        for en in self.level_data["enemies"]:
            if en["type"] == "tom":
                self.enemies.add(Tom(en["x"], en["y"]))
            elif en["type"] == "broom":
                self.enemies.add(Broom(en["x"], en["y"]))
            
        # Initial stats
        self.total_cheese = 0
        self.scale_cheese = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.state_machine.set_state("MENU") # Should be PAUSE
        
        self.player.handle_input()

    def update(self, dt):
        self.moving_platforms.update(dt)
        self.traps.update(dt)
        
        # Solid platforms for player and other entities
        solids = list(self.platforms) + list(self.moving_platforms) + list(self.crates)
        
        self.player.update(dt, solids)
        self.enemies.update(dt, self.player, solids)
        self.crates.update(dt, solids)
        
        # Player collisions
        # 1. Cheese
        collected = pygame.sprite.spritecollide(self.player, self.cheeses, True)
        for c in collected:
            c.collect()
            self.total_cheese += 1
            self.scale_cheese += 1
            if self.scale_cheese >= 5:
                self.scale_cheese = 0
                if self.player.health < self.player.config["max_health"]:
                    self.player.health += 1

        # 2. Traps
        traps_hit = pygame.sprite.spritecollide(self.player, self.traps, False)
        for trap in traps_hit:
            if trap.active:
                if self.player.take_damage():
                    trap.activate()

        # 3. Enemies
        enemies_hit = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemies_hit:
            self.player.take_damage()
        
        # 5. Death check
        if self.player.health <= 0:
            # For now, restart the level
            # In a real game, this would go to a Game Over screen
            self.enter(level_id=self.level_data.get("id", 1))

        # 4. Crate/Enemy interaction
        for crate in self.crates:
            if crate.is_broken: continue
            enemies_hit_crate = pygame.sprite.spritecollide(crate, self.enemies, False)
            for enemy in enemies_hit_crate:
                if crate.activated_by_player:
                    if crate.break_crate():
                        enemy.kill()
                        # Spawn cheese from crate
                        self.cheeses.add(Cheese(crate.rect.x, crate.rect.y))
        
        self.camera.update(self.player.rect)

    def draw(self, screen):
        # Draw parallax background
        bg_offset = -(self.camera.offset.x * 0.5) % self.bg_width
        screen.blit(self.background, (bg_offset - self.bg_width, 0))
        screen.blit(self.background, (bg_offset, 0))
        screen.blit(self.background, (bg_offset + self.bg_width, 0))
        
        # Draw entities with camera offset
        groups = [self.platforms, self.moving_platforms, self.cheeses, self.traps, self.crates, self.enemies]
        for group in groups:
            for sprite in group:
                screen.blit(sprite.image, sprite.rect.topleft - self.camera.offset)
            
        self.player.draw(screen, self.camera.offset)
        
        # HUD
        self.hud.draw(screen, self.player.health, self.player.config["max_health"], self.total_cheese, self.scale_cheese)
