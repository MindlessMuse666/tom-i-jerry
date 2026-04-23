import pygame
import json
import os
from scene.base import Scene
from entity.player import Player
from entity.env import Platform, MovingPlatform, Cheese, Trap, Crate, Hole
from entity.enemy import Tom, Broom, BossTom
from constant import SFX_BOSS_DEATH, SFX_CHEESE, SFX_LEVEL_START, SFX_TOM_DEATH, SFX_WIN
from entity.projectile import Decoy, Rocket
from core.camera import Camera
from core.resource import resource_manager
from core.mixer import mixer
from ui.hud import HUD

class LevelScene(Scene):
    """
    Основная игровая сцена (уровень).
    Управляет игровым циклом, физикой, коллизиями, спауном объектов и HUD.
    """
    def __init__(self, game):
        """
        Инициализация уровня.

        Args:
            game: Объект игры.
        """
        super().__init__(game)
        self.level_data = None
        self.current_level_id = 1
        self.camera = None
        self.player = None
        
        # Группы спрайтов для различных игровых объектов
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
        
        # Игровая статистика для HUD
        self.total_cheese = 0
        self.scale_cheese = 0
        self.red_cheese_collected = 0
        
        self.background = None
        self.bg_width = 0
        
        # Система чит-кодов
        self.cheat_buffer = ""
        self.cheat_timer = 0
        self.god_mode = False
        self.debug_mode = False
        self.frame_count = 0

    def enter(self, level_id=1, resume=False):
        """
        Вызывается при входе в сцену уровня.

        Args:
            level_id: ID загружаемого уровня.
            resume: Если True, продолжает текущую игру без перезагрузки.
        """
        self.current_level_id = level_id
        if not resume:
            # Остановка всех звуков перед загрузкой нового уровня
            mixer.stop_music()
            mixer.stop_all_sfx()
            
            self.load_level(level_id)
            mixer.play_music(self.level_data["music"])
            # Звук начала уровня
            mixer.play_sfx(resource_manager.get_sound(SFX_LEVEL_START))

    def load_level(self, level_id: int):
        """
        Загрузка конфигурации уровня из JSON-файла.

        Args:
            level_id: ID уровня для загрузки.
        """
        path = os.path.join("level", f"level{level_id}.json")
        with open(path, "r") as f:
            self.level_data = json.load(f)
            
        self.camera = Camera(self.level_data["width"], self.level_data["height"])
        
        # Загрузка фона с масштабированием под высоту экрана (720px)
        raw_bg = resource_manager.get_image(self.level_data["background"])
        bg_height = 720
        bg_aspect = raw_bg.get_width() / raw_bg.get_height()
        bg_width = int(bg_height * bg_aspect)
        self.background = pygame.transform.scale(raw_bg, (bg_width, bg_height))
        self.bg_width = self.background.get_width()
        
        # Спаун игрока
        spawn = self.level_data["spawn_point"]
        self.player = Player(spawn[0], spawn[1])
        
        # Загрузка платформ
        self.platforms.empty()
        from constant import GROUND_PATH
        for i, p in enumerate(self.level_data["platforms"]):
            # Используем текстуру земли для первой платформы или очень широких участков
            path = GROUND_PATH if i == 0 or p[2] > 1000 else None
            if path:
                self.platforms.add(Platform(p[0], p[1], p[2], p[3], image_path=path))
            else:
                self.platforms.add(Platform(p[0], p[1], p[2], p[3]))
            
        self.moving_platforms.empty()
        for mp in self.level_data["moving_platforms"]:
            self.moving_platforms.add(MovingPlatform(mp["x"], mp["y"], mp["width"], mp["height"], mp["path"], mp["speed"]))
            
        # Загрузка сыра
        self.cheeses.empty()
        for c in self.level_data["cheeses"]:
            if isinstance(c, list):
                self.cheeses.add(Cheese(c[0], c[1]))
            else: # Словарь для красного сыра или особых свойств
                is_red = c.get("is_red", False)
                self.cheeses.add(Cheese(c["x"], c["y"], is_red=is_red))
            
        # Загрузка капканов
        self.traps.empty()
        for t in self.level_data["traps"]:
            self.traps.add(Trap(t[0], t[1]))
            
        # Загрузка ящиков
        self.crates.empty()
        for cr in self.level_data["crates"]:
            self.crates.add(Crate(cr[0], cr[1]))
            
        # Загрузка врагов
        self.enemies.empty()
        for en in self.level_data["enemies"]:
            if en["type"] == "tom":
                self.enemies.add(Tom(en["x"], en["y"]))
            elif en["type"] == "broom":
                self.enemies.add(Broom(en["x"], en["y"]))
        
        # Загрузка босса (только для уровня 3)
        if "boss_spawn" in self.level_data:
            bx, by = self.level_data["boss_spawn"]
            # Спауним босса чуть выше для корректной позиции на платформе
            self.boss = BossTom(bx, by - 50)
        else:
            self.boss = None
            
        # Загрузка выхода (норы)
        if "hole" in self.level_data:
            hx, hy = self.level_data["hole"]
            self.hole = Hole(hx, hy)
        else:
            self.hole = None
            
        # Сброс статистики
        self.total_cheese = 0
        self.scale_cheese = 0
        self.red_cheese_collected = 0
        self.frame_count = 0
        
        # Условие появления выхода: собрать весь доступный сыр
        if self.current_level_id == 3:
            self.cheeses_to_spawn_hole = 25 # Для босса нужно 25 красных сыров
        else:
            self.cheeses_to_spawn_hole = len(self.cheeses) + len(self.crates)

    def handle_events(self, events: list[pygame.event.Event]):
        """Обработка ввода игрока и системы читов."""
        self.player.handle_input()
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Набор чит-кода
                if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                    self.cheat_buffer += event.unicode
                    self.cheat_timer = 2.0 # Сброс таймера при нажатии
                    self.check_cheats()
                
                # Использование приманки
                if event.key == pygame.K_f:
                    mouse_pos = pygame.mouse.get_pos()
                    world_mouse = mouse_pos + self.camera.offset
                    self.player.throw_decoy(self.decoys, world_mouse)
                # Пауза
                elif event.key == pygame.K_ESCAPE:
                    self.game.state_machine.set_state("PAUSE", level_id=self.current_level_id)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Левый клик (приманка)
                    mouse_pos = pygame.mouse.get_pos()
                    world_mouse = mouse_pos + self.camera.offset
                    self.player.throw_decoy(self.decoys, world_mouse)

    def check_cheats(self):
        """Проверка введенных комбинаций чит-кодов."""
        if "0000" in self.cheat_buffer:
            self.god_mode = not self.god_mode
            self.cheat_buffer = ""
            if self.god_mode:
                self.player.health = self.player.config["max_health"]
            mixer.play_sfx(resource_manager.get_sound(SFX_CHEESE))
            print(f"Режим Бога: {self.god_mode}")
        elif "9999" in self.cheat_buffer:
            self.cheat_buffer = ""
            mixer.play_sfx(resource_manager.get_sound(SFX_WIN))
            self.game.state_machine.set_state("LEVEL_WIN", 
                                            cheese_count=self.total_cheese, 
                                            level_id=self.current_level_id)
        elif "8888" in self.cheat_buffer:
            self.debug_mode = not self.debug_mode
            self.cheat_buffer = ""
            mixer.play_sfx(resource_manager.get_sound(SFX_CHEESE))
            print(f"Режим отладки: {self.debug_mode}")

    def update(self, dt: float):
        """
        Обновление всей игровой логики уровня.

        Args:
            dt: Дельта времени.
        """
        self.dt = dt
        self.frame_count += 1
        
        # Обновление таймера чит-кода
        if self.cheat_timer > 0:
            self.cheat_timer -= dt
            if self.cheat_timer <= 0:
                self.cheat_buffer = ""
        
        self.moving_platforms.update(dt)
        self.traps.update(dt)
        
        # Список твердых объектов для коллизий (платформы + целые ящики)
        solids = list(self.platforms) + list(self.moving_platforms) + [c for c in self.crates if not c.is_broken]
        
        self.decoys.update(dt, solids)
        self.player.update(dt, solids)
        self.enemies.update(dt, self.player, solids, self.decoys)
        
        # Проверка падения врагов в пропасть
        for enemy in list(self.enemies):
            if hasattr(enemy, 'fell_off') and enemy.fell_off:
                # Спаун сыра на месте начального появления врага
                self.cheeses.add(Cheese(enemy.spawn_pos.x, enemy.spawn_pos.y))
                enemy.kill()

        # Проверка падения ящиков в пропасть
        self.crates.update(dt, solids)
        for crate in list(self.crates):
            if hasattr(crate, 'fell_off') and crate.fell_off:
                self.cheeses.add(Cheese(crate.spawn_pos.x, crate.spawn_pos.y))
                crate.kill()

        self.rockets.update(dt)
        
        if self.boss:
            self.boss.update(dt, self.player, self.rockets, self.crates)
        
        # Обработка столкновений игрока
        # 1. Сыр
        collected = pygame.sprite.spritecollide(self.player, self.cheeses, True)
        for c in collected:
            c.collect()
            if c.is_red:
                self.red_cheese_collected += 1
            else:
                self.total_cheese += 1
                self.scale_cheese += 1
                # Каждые 5 сыров восстанавливают 1 HP
                if self.scale_cheese >= 5:
                    self.scale_cheese = 0
                    if self.player.health < self.player.config["max_health"]:
                        self.player.health += 1
            
            # Условие активации выхода
            condition_met = False
            if self.current_level_id == 3:
                condition_met = self.red_cheese_collected >= self.cheeses_to_spawn_hole
            else:
                condition_met = self.total_cheese >= self.cheeses_to_spawn_hole
                
            if condition_met and self.hole:
                if self.current_level_id == 3:
                     mixer.play_sfx(resource_manager.get_sound(SFX_BOSS_DEATH))
                self.hole.activate()

        # 1.1 Столкновение с норой (победа)
        if self.hole and self.hole.active:
            if self.player.rect.colliderect(self.hole.rect):
                self.game.state_machine.set_state("LEVEL_WIN", 
                                                cheese_count=self.total_cheese, 
                                                level_id=self.current_level_id)

        # 2. Капканы
        traps_hit = pygame.sprite.spritecollide(self.player, self.traps, False)
        for trap in traps_hit:
            if trap.active:
                if not self.god_mode:
                    if self.player.take_damage():
                        trap.activate()
                else:
                    trap.activate()

        # 3. Враги
        enemies_hit = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemies_hit:
            if not self.god_mode:
                self.player.take_damage()
        
        # 3.0 Босс и снаряды
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

        # 4. Проверка смерти или падения игрока
        if self.player.health <= 0 or (self.player.pos.y > self.level_data["height"] + 200 and self.frame_count > 10):
            self.game.state_machine.set_state("GAME_OVER", cheese_count=self.total_cheese)

        # Обновление камеры
        self.camera.update(self.player.rect, dt)

    def draw(self, screen: pygame.Surface):
        """Отрисовка всех объектов уровня с учетом камеры."""
        # Параллакс фона
        bg_x = -(self.camera.offset.x * 0.5) % self.bg_width
        screen.blit(self.background, (bg_x, 0))
        if bg_x > 0:
            screen.blit(self.background, (bg_x - self.bg_width, 0))
        else:
            screen.blit(self.background, (bg_x + self.bg_width, 0))
            
        # Отрисовка игровых объектов со смещением камеры
        for group in [self.platforms, self.moving_platforms, self.cheeses, 
                     self.traps, self.crates, self.enemies, self.decoys, self.rockets]:
            for sprite in group:
                screen.blit(sprite.image, sprite.rect.topleft - self.camera.offset)
                
        if self.boss:
            screen.blit(self.boss.image, self.boss.rect.topleft - self.camera.offset)
            
        if self.hole:
            screen.blit(self.hole.image, self.hole.rect.topleft - self.camera.offset)
            
        screen.blit(self.player.image, self.player.rect.topleft - self.camera.offset)
        
        # Отрисовка отладочной информации
        if self.debug_mode:
            pos_text = f"X: {int(self.player.pos.x)} Y: {int(self.player.pos.y)}"
            debug_surf = resource_manager.get_font(DEFAULT_FONT, 20).render(pos_text, True, (255, 255, 0))
            screen.blit(debug_surf, (LOGICAL_WIDTH // 2 - debug_surf.get_width() // 2, 20))

        # Отрисовка HUD поверх всего
        self.hud.draw(screen, self.player.health, self.player.config["max_health"], 
                     self.total_cheese, self.scale_cheese, 
                     red_cheese_collected=self.red_cheese_collected if self.current_level_id == 3 else None,
                     required_cheese=self.cheeses_to_spawn_hole,
                     level_id=self.current_level_id, dt=self.dt)
