"""
Модуль игрока (Джерри).
Реализует физику движения, анимации, обработку ввода и взаимодействие с миром.
"""
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
    """
    Класс главного героя — мышонка Джерри.
    """
    def __init__(self, x, y):
        super().__init__()
        
        # Загрузка конфигурации из TOML
        config_path = os.path.join("config", "player.toml")
        with open(config_path, "rb") as f:
            self.config = tomllib.load(f)
            
        # Физические параметры
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, self.config["gravity"])
        self.speed = self.config["speed"]
        self.jump_force = self.config["jump_force"]
        
        # Анимация и спрайты
        self.sprite_sheet = resource_manager.get_image(PLAYER_PATH)
        self.scale_factor = 3 # Масштаб игрока
        self.frames = {}
        self.mirrored_frames = {}
        self.load_all_frames()
        
        self.state = "IDLE" # Текущее состояние анимации
        self.frame_index = 0
        self.animation_speed = 4 
        self.animation_timer = 0
        self.facing_right = True
        
        self.image = self.frames["IDLE"][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-20, -8) # Уменьшенный хитбокс для честных столкновений
        
        # Характеристики и состояние здоровья
        self.health = self.config["max_health"]
        self.is_invulnerable = False
        self.invulnerability_timer = 0
        self.visible = True
        self.blink_timer = 0
        
        self.on_ground = False
        self.current_platform = None
        
        # Логика приманок
        self.decoy_cooldown = 0
        self.throw_force = 1000 # Базовая сила броска

    def load_all_frames(self):
        """Загрузка всех кадров анимации из спрайт-листа."""
        states = ["IDLE", "WALK", "JUMP", "HURT"]
        for state in states:
            self.frames[state] = []
            self.mirrored_frames[state] = []
            
        # Ряд 1 (y=0): Ожидание (2 кадра, 22x28)
        for i in range(2):
            frame = self.get_frame(i, 0, 22, 28)
            self.frames["IDLE"].append(frame)
            self.mirrored_frames["IDLE"].append(pygame.transform.flip(frame, True, False))
            
        # Ряд 2 (y=1): Ходьба (2 кадра, 22x28)
        for i in range(2):
            frame = self.get_frame(i, 1, 22, 28)
            self.frames["WALK"].append(frame)
            self.mirrored_frames["WALK"].append(pygame.transform.flip(frame, True, False))
        
        # Прыжок — первый кадр ходьбы
        jump_frame = self.frames["WALK"][0]
        self.frames["JUMP"].append(jump_frame)
        self.mirrored_frames["JUMP"].append(pygame.transform.flip(jump_frame, True, False))
            
        # Ряд 3 (y=2): Получение урона (1 кадр, 22x28)
        hurt_frame = self.get_frame(0, 2, 22, 28)
        self.frames["HURT"].append(hurt_frame)
        self.mirrored_frames["HURT"].append(pygame.transform.flip(hurt_frame, True, False))

    def get_frame(self, col, row, width, height):
        """Извлечение и масштабирование отдельного кадра."""
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.blit(self.sprite_sheet, (0, 0), (col * width, row * height, width, height))
        new_size = (int(width * self.scale_factor), int(height * self.scale_factor))
        return pygame.transform.scale(surf, new_size)

    def handle_input(self):
        """Обработка ввода игрока."""
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
        """Обновление физики и состояния игрока."""
        # 1. Смещение на движущихся платформах
        if self.on_ground and self.current_platform and hasattr(self.current_platform, 'vel'):
            platform_displacement = self.current_platform.vel * dt
            self.pos += platform_displacement
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # 2. Применение гравитации с переменным весом
        gravity = self.acc.y
        if self.vel.y > 0: # Падение тяжелее
             gravity *= 1.5
        elif self.vel.y < 0 and abs(self.vel.y) < 100: # "Невесомость" в пике прыжка
             gravity *= 0.5
             
        self.vel.y += gravity * dt
        
        # Горизонтальное движение
        self.pos.x += self.vel.x * dt
        self.rect.x = round(self.pos.x)
        self.check_collisions(platforms, 'horizontal')
        
        # Вертикальное движение
        self.pos.y += self.vel.y * dt
        self.rect.y = round(self.pos.y)
        self.check_collisions(platforms, 'vertical')
        
        # Проверка "земли" под ногами для предотвращения мерцания
        if self.on_ground and self.current_platform:
            test_rect = self.rect.copy()
            test_rect.y += 2
            if not test_rect.colliderect(self.current_platform.rect):
                self.on_ground = False
                self.current_platform = None
        
        self.update_state()
        self.animate(dt)
        self.update_invulnerability(dt)
        
        if self.decoy_cooldown > 0:
            self.decoy_cooldown -= dt

    def throw_decoy(self, decoys_group, target_pos=None):
        """Бросок сырной приманки в сторону курсора или по направлению взгляда."""
        if self.decoy_cooldown <= 0:
            from entity.projectile import Decoy
            start_x = self.rect.centerx
            start_y = self.rect.centery
            
            if target_pos:
                target_vec = pygame.Vector2(target_pos) - pygame.Vector2(start_x, start_y)
                if target_vec.length() > 0:
                    force = min(target_vec.length() * 2, self.throw_force)
                    velocity = target_vec.normalize() * force
                    vx, vy = velocity.x, velocity.y
                else:
                    vx, vy = 0, 0
            else:
                vx = self.throw_force * 0.8 if self.facing_right else -self.throw_force * 0.8
                vy = -self.throw_force * 0.4
            
            decoy = Decoy(start_x, start_y, vx, vy)
            decoys_group.add(decoy)
            
            mixer.play_sfx(resource_manager.get_sound(SFX_DECOY_THROW))
            self.decoy_cooldown = 0.5
            return True
        return False

    def check_collisions(self, platforms, direction):
        """Обработка столкновений с платформами и ящиками."""
        if direction == 'horizontal':
            for platform in platforms:
                if platform == self.current_platform:
                    continue
                    
                if self.rect.colliderect(platform.rect):
                    # Толкание ящиков
                    if hasattr(platform, 'vel') and not hasattr(platform, 'path'): 
                        platform.vel.x = self.vel.x
                        platform.activated_by_player = True
                    
                    if self.vel.x > 0:
                        self.rect.right = platform.rect.left
                        self.pos.x = self.rect.x
                    elif self.vel.x < 0:
                        self.rect.left = platform.rect.right
                        self.pos.x = self.rect.x
        else:
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.vel.y > 0: # Приземление
                        self.rect.bottom = platform.rect.top
                        self.pos.y = self.rect.y
                        self.vel.y = 0
                        self.on_ground = True
                        self.current_platform = platform
                    elif self.vel.y < 0: # Удар головой
                        self.rect.top = platform.rect.bottom
                        self.pos.y = self.rect.y
                        self.vel.y = 0
                        if self.current_platform == platform:
                             self.on_ground = False
                             self.current_platform = None

    def update_state(self):
        """Выбор текущего состояния анимации."""
        if not self.on_ground:
            new_state = "JUMP"
        elif abs(self.vel.x) > 10.0:
            new_state = "WALK"
        else:
            new_state = "IDLE"
        
        if new_state != self.state:
            self.state = new_state
            self.frame_index = 0
            self.animation_timer = 0

    def animate(self, dt):
        """Отрисовка анимации с учетом направления взгляда."""
        self.animation_timer += dt
        if self.animation_timer >= 1.0 / self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames[self.state])
            
        if self.facing_right:
            self.image = self.frames[self.state][self.frame_index]
        else:
            self.image = self.mirrored_frames[self.state][self.frame_index]

    def update_invulnerability(self, dt):
        """Логика мигания при неуязвимости."""
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
        """Получение урона и активация неуязвимости."""
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
        """Отрисовка игрока со смещением камеры."""
        if self.visible:
            draw_pos = self.rect.topleft - offset
            screen.blit(self.image, draw_pos)
