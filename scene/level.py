import pygame
import json
import os
from scene.base import Scene
from entity.player import Player
from entity.env import Platform, MovingPlatform, Cheese, Trap, Crate, Hole
from entity.enemy import Tom, Broom, BossTom
from constant import SFX_CHEESE, SFX_WIN
from entity.projectile import Decoy, Rocket
from core.camera import Camera
from core.resource import resource_manager
from core.mixer import mixer
from ui.hud import HUD

class LevelScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.level_data = None
        self.current_level_id = 1
        self.camera = None
        self.player = None
        self.platforms = pygame.sprite.Group()
        self.moving_platforms = pygame.sprite.Group()
        self.cheeses = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()
        self.crates = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.decoys = pygame.sprite.Group()
        self.rockets = pygame.sprite.Group()
        self.boss = None
        self.hole = None
        self.hud = HUD()
        
        # Game stats for HUD
        self.total_cheese = 0
        self.scale_cheese = 0
        
        self.background = None
        self.bg_width = 0
        
        # Cheat system
        self.cheat_buffer = ""
        self.cheat_timer = 0
        self.god_mode = False

    def enter(self, level_id=1):
        self.current_level_id = level_id
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
            if isinstance(c, list):
                self.cheeses.add(Cheese(c[0], c[1]))
            else: # Dictionary for red cheese or special properties
                is_red = c.get("is_red", False)
                self.cheeses.add(Cheese(c["x"], c["y"], is_red=is_red))
            
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
        
        # Load Boss (Level 3 specific)
        if "boss_spawn" in self.level_data:
            bx, by = self.level_data["boss_spawn"]
            # Position boss slightly higher as requested
            self.boss = BossTom(bx, by - 50)
        else:
            self.boss = None
            
        # Load Hole (if exists in level data)
        if "hole" in self.level_data:
            hx, hy = self.level_data["hole"]
            self.hole = Hole(hx, hy)
        else:
            self.hole = None
            
        # Initial stats
        self.total_cheese = 0
        self.scale_cheese = 0
        self.red_cheese_collected = 0
        
        # Hole appearance condition: count all visible cheeses AND cheeses inside crates
        # (Each crate currently spawns exactly 1 cheese when broken)
        # For Level 3 (Boss), we might have a specific requirement (15 red cheeses)
        if self.current_level_id == 3:
            self.cheeses_to_spawn_hole = 15
        else:
            self.cheeses_to_spawn_hole = len(self.cheeses) + len(self.crates)

    def handle_events(self, events):
        self.player.handle_input()
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Cheat input collection
                if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                    self.cheat_buffer += event.unicode
                    self.cheat_timer = 2.0 # Reset timer on each keypress
                    self.check_cheats()
                
                if event.key == pygame.K_f or event.key == pygame.K_LCTRL:
                    # Get mouse pos and convert to world coords
                    mouse_pos = pygame.mouse.get_pos()
                    world_mouse = mouse_pos + self.camera.offset
                    self.player.throw_decoy(self.decoys, world_mouse)
                elif event.key == pygame.K_ESCAPE:
                    self.game.state_machine.set_state("MENU")
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click
                    mouse_pos = pygame.mouse.get_pos()
                    world_mouse = mouse_pos + self.camera.offset
                    self.player.throw_decoy(self.decoys, world_mouse)

    def check_cheats(self):
        if "0000" in self.cheat_buffer:
            self.god_mode = not self.god_mode
            self.cheat_buffer = ""
            # Reset player health if enabling god mode
            if self.god_mode:
                self.player.health = self.player.config["max_health"]
            # Play a sound to confirm cheat
            mixer.play_sfx(resource_manager.get_sound(SFX_CHEESE))
            print(f"God Mode: {self.god_mode}")
        elif "9999" in self.cheat_buffer:
            self.cheat_buffer = ""
            mixer.play_sfx(resource_manager.get_sound(SFX_WIN))
            self.game.state_machine.set_state("LEVEL_WIN", 
                                            cheese_count=self.total_cheese, 
                                            level_id=self.current_level_id)

    def update(self, dt):
        # Update cheat timer
        if self.cheat_timer > 0:
            self.cheat_timer -= dt
            if self.cheat_timer <= 0:
                self.cheat_buffer = ""
        
        self.moving_platforms.update(dt)
        self.traps.update(dt)
        
        # Solid platforms for player and other entities
        # Filter out broken crates so they don't have collision
        solids = list(self.platforms) + list(self.moving_platforms) + [c for c in self.crates if not c.is_broken]
        
        self.decoys.update(dt, solids)
        self.player.update(dt, solids)
        self.enemies.update(dt, self.player, solids, self.decoys)
        self.crates.update(dt, solids)
        self.rockets.update(dt)
        
        if self.boss:
            self.boss.update(dt, self.player, self.rockets, self.crates)
        
        # Player collisions
        # 1. Cheese
        collected = pygame.sprite.spritecollide(self.player, self.cheeses, True)
        for c in collected:
            c.collect()
            if c.is_red:
                self.red_cheese_collected += 1
                # Red cheese also counts towards total if needed, but here it's for level 3
            else:
                self.total_cheese += 1
                self.scale_cheese += 1
                if self.scale_cheese >= 5:
                    self.scale_cheese = 0
                    if self.player.health < self.player.config["max_health"]:
                        self.player.health += 1
            
            # Hole appearance condition
            condition_met = False
            if self.current_level_id == 3:
                condition_met = self.red_cheese_collected >= self.cheeses_to_spawn_hole
            else:
                condition_met = self.total_cheese >= self.cheeses_to_spawn_hole
                
            if condition_met and self.hole:
                self.hole.activate()

        # 1.1 Hole collision
        if self.hole and self.hole.active:
            if self.player.rect.colliderect(self.hole.rect):
                # Level complete!
                self.game.state_machine.set_state("LEVEL_WIN", 
                                                cheese_count=self.total_cheese, 
                                                level_id=self.current_level_id)

        # 2. Traps
        traps_hit = pygame.sprite.spritecollide(self.player, self.traps, False)
        for trap in traps_hit:
            if trap.active:
                if not self.god_mode:
                    if self.player.take_damage():
                        trap.activate()
                else:
                    trap.activate()

        # 3. Enemies
        enemies_hit = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemies_hit:
            if not self.god_mode:
                self.player.take_damage()
        
        # 3.0 Boss/Projectiles
        if self.boss:
            if self.player.rect.colliderect(self.boss.rect):
                if not self.god_mode:
                    self.player.take_damage()
                    
        rockets_hit = pygame.sprite.spritecollide(self.player, self.rockets, False)
        for rocket in rockets_hit:
            if not self.god_mode:
                if self.player.take_damage():
                    rocket.explode()
            else:
                rocket.explode()
        
        # 3.0.1 Rocket/Platform/Crate collision
        for rocket in list(self.rockets):
            if pygame.sprite.spritecollide(rocket, self.platforms, False) or \
               pygame.sprite.spritecollide(rocket, self.moving_platforms, False) or \
               pygame.sprite.spritecollide(rocket, self.crates, False):
                rocket.explode()
        
        # 3.1 Fall damage (Out of bounds)
        # If player falls significantly below the level height or 1200px
        if self.player.pos.y > self.level_data["height"] + 200 or self.player.pos.y > 1200:
             if not self.god_mode:
                 self.player.health = 0
             else:
                 # Respawn at spawn point if god mode
                 spawn = self.level_data["spawn_point"]
                 self.player.pos = pygame.Vector2(spawn[0], spawn[1])
                 self.player.vel = pygame.Vector2(0, 0)
        
        # 5. Death check
        if self.player.health <= 0:
            self.game.state_machine.set_state("GAME_OVER", cheese_count=self.total_cheese)

        # 4. Crate/Enemy/Decoy interaction
        for crate in list(self.crates):
            if crate.is_broken: continue
            
            # A crate can only kill enemies if it's actually MOVING horizontally 
            # and was activated by the player
            if crate.activated_by_player and abs(crate.vel.x) > 10.0:
                enemies_hit_crate = pygame.sprite.spritecollide(crate, self.enemies, False)
                for enemy in enemies_hit_crate:
                    cx, cy = crate.rect.x, crate.rect.y
                    if crate.break_crate():
                        enemy.kill()
                        self.cheeses.add(Cheese(cx, cy))
                
                # Boss crate special logic: drop red cheese when it hits ground or player
                if crate.is_boss_crate:
                    # Check if hit ground
                    if crate.vel.y == 0: # It landed
                        cx, cy = crate.rect.centerx, crate.rect.top
                        if crate.break_crate():
                            self.cheeses.add(Cheese(cx, cy, is_red=True))
                    
                    # Check if hit player
                    if self.player.rect.colliderect(crate.rect):
                         cx, cy = crate.rect.centerx, crate.rect.top
                         if not self.god_mode:
                             self.player.take_damage()
                         if crate.break_crate():
                             self.cheeses.add(Cheese(cx, cy, is_red=True))

                # Crate also breaks if it hits a decoy (distraction mechanic)
                decoys_hit_crate = pygame.sprite.spritecollide(crate, self.decoys, True)
                if decoys_hit_crate:
                    crate.break_crate()
        
        self.camera.update(self.player.rect)

    def draw(self, screen):
        # Draw parallax background
        bg_offset = -(self.camera.offset.x * 0.5) % self.bg_width
        screen.blit(self.background, (bg_offset - self.bg_width, 0))
        screen.blit(self.background, (bg_offset, 0))
        screen.blit(self.background, (bg_offset + self.bg_width, 0))
        
        # Draw entities with camera offset
        groups = [self.platforms, self.moving_platforms, self.cheeses, self.traps, self.crates, self.enemies, self.decoys, self.rockets]
        for group in groups:
            for sprite in group:
                screen.blit(sprite.image, sprite.rect.topleft - self.camera.offset)
        
        # Boss
        if self.boss:
            screen.blit(self.boss.image, self.boss.rect.topleft - self.camera.offset)
        
        # Hole
        if self.hole:
            self.hole.draw(screen, self.camera.offset)
            
        self.player.draw(screen, self.camera.offset)
        
        # HUD
        self.hud.draw(screen, self.player.health, self.player.config["max_health"], 
                      self.total_cheese, self.scale_cheese)
