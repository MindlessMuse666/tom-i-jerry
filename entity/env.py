"""
Модуль объектов окружения.
Включает платформы, движущиеся платформы, сыр, капканы, ящики и выход с уровня.
"""
import pygame
import os
from core.resource import resource_manager
from core.mixer import mixer
from constant import (
    PLATFORM_PATH, MOVING_PLATFORM_PATH, GROUND_PATH,
    CHEESE_PATH, RED_CHEESE_PATH, TRAP_PATH, CRATE_PATH, HOLE_PATH,
    SFX_CHEESE, SFX_TRAP_SNAP, SFX_CRATE_BREAK, SFX_WIN
)

class Platform(pygame.sprite.Sprite):
    """
    Базовая статичная платформа. Автоматически тайлится под заданный размер.
    """
    def __init__(self, x, y, width, height, image_path=PLATFORM_PATH):
        super().__init__()
        # Округление размеров до кратных 32 для идеального тайлинга
        width = (width // 32) * 32
        height = (height // 32) * 32
        
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        tile_img = resource_manager.get_image(image_path)
        
        tile_size = 32
        scaled_tile = pygame.transform.scale(tile_img, (tile_size, tile_size))
        
        # Заполнение поверхности тайлами
        for ty in range(0, height, tile_size):
            for tx in range(0, width, tile_size):
                self.image.blit(scaled_tile, (tx, ty))
        self.rect = self.image.get_rect(topleft=(x, y))

class MovingPlatform(Platform):
    """
    Движущаяся платформа, перемещающаяся между двумя точками.
    """
    def __init__(self, x, y, width, height, path, speed):
        super().__init__(x, y, width, height, MOVING_PLATFORM_PATH)
        self.start_pos = pygame.Vector2(x, y)
        self.path = pygame.Vector2(path) # Относительный путь от старта
        self.end_pos = self.start_pos + self.path
        self.speed = speed
        self.direction = 1
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)

    def update(self, dt):
        """Обновление позиции платформы и расчет текущей скорости."""
        target = self.end_pos if self.direction == 1 else self.start_pos
        move_vec = target - self.pos
        
        if move_vec.length() > 0:
            direction_vec = move_vec.normalize()
            self.vel = direction_vec * self.speed
            
            self.pos += self.vel * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
            
            # Проверка достижения целевой точки
            if (target - self.pos).length() < 2:
                self.direction *= -1
        else:
            self.vel = pygame.Vector2(0, 0)

class Cheese(pygame.sprite.Sprite):
    """
    Объект сыра для сбора игроком.
    """
    def __init__(self, x, y, is_red=False):
        super().__init__()
        self.is_red = is_red
        img_path = RED_CHEESE_PATH if is_red else CHEESE_PATH
        img = resource_manager.get_image(img_path)
        # Размер сыра 64x64 (масштаб 2)
        self.image = pygame.transform.scale(img, (64, 64))
        self.rect = self.image.get_rect(topleft=(x, y))

    def collect(self):
        """Логика сбора сыра."""
        mixer.play_sfx(resource_manager.get_sound(SFX_CHEESE))
        self.kill()

class Trap(pygame.sprite.Sprite):
    """
    Капкан, наносящий урон игроку или ломающий ящики.
    """
    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = resource_manager.get_image(TRAP_PATH)
        self.scale_factor = 3
        self.frames = self.load_frames()
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.active = True
        self.alpha = 255
        self.fade_speed = 200 # Скорость исчезновения после срабатывания

    def load_frames(self):
        """Загрузка кадров открытого и закрытого капкана (24x22)."""
        frames = []
        for i in range(2):
            surf = pygame.Surface((24, 22), pygame.SRCALPHA)
            surf.blit(self.sprite_sheet, (0, 0), (i * 24, 0, 24, 22))
            frames.append(pygame.transform.scale(surf, (int(24 * self.scale_factor), int(22 * self.scale_factor))))
        return frames

    def activate(self):
        """Срабатывание капкана."""
        if self.active:
            self.active = False
            self.image = self.frames[1]
            mixer.play_sfx(resource_manager.get_sound(SFX_TRAP_SNAP))

    def update(self, dt):
        """Плавное исчезновение после активации."""
        if not self.active:
            self.alpha -= self.fade_speed * dt
            if self.alpha <= 0:
                self.kill()
            else:
                self.image.set_alpha(int(self.alpha))

class Crate(pygame.sprite.Sprite):
    """
    Ящик, который можно толкать. Ломается при падении на врагов или капканы.
    """
    def __init__(self, x, y, scale=2):
        super().__init__()
        self.sprite_sheet = resource_manager.get_image(CRATE_PATH)
        self.scale_factor = scale 
        self.frames = self.load_frames()
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.pos = pygame.Vector2(x, y)
        self.spawn_pos = pygame.Vector2(x, y) # Для спауна сыра при падении
        self.vel = pygame.Vector2(0, 0)
        self.gravity = 1200
        self.friction = 500
        self.is_broken = False
        self.fell_off = False
        self.activated_by_player = False # Толкал ли игрок этот ящик
        self.is_boss_crate = False 
        self.has_dealt_fall_damage = False
        self.broken_timer = 0
        self.broken_duration = 0.3 
        
        self.break_sfx = resource_manager.get_sound(SFX_CRATE_BREAK)

    def load_frames(self):
        """Загрузка спрайта ящика и его обломков."""
        frames = []
        for i in range(2):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            surf.blit(self.sprite_sheet, (0, 0), (i * 32, 0, 32, 32))
            frames.append(pygame.transform.scale(surf, (int(32 * self.scale_factor), int(32 * self.scale_factor))))
        return frames

    def update(self, dt, platforms):
        """Физика падения и движения ящика."""
        if self.is_broken:
            self.broken_timer += dt
            if self.broken_timer >= self.broken_duration:
                self.kill()
            return

        # Проверка падения за пределы карты
        if self.pos.y > 2000:
            self.fell_off = True
            return

        self.vel.y += self.gravity * dt
        
        # Применение трения при качении
        if self.vel.x > 0:
            self.vel.x = max(0, self.vel.x - self.friction * dt)
        elif self.vel.x < 0:
            self.vel.x = min(0, self.vel.x + self.friction * dt)

        # Перемещение
        self.pos.x += self.vel.x * dt
        self.rect.x = round(self.pos.x)
        self.check_collisions(platforms, 'horizontal')
        
        self.pos.y += self.vel.y * dt
        self.rect.y = round(self.pos.y)
        self.check_collisions(platforms, 'vertical')

    def check_collisions(self, platforms, direction):
        """Обработка столкновений ящика с миром."""
        for platform in platforms:
            if platform == self: continue
            if self.rect.colliderect(platform.rect):
                if direction == 'horizontal':
                    if self.vel.x > 0:
                        self.rect.right = platform.rect.left
                    elif self.vel.x < 0:
                        self.rect.left = platform.rect.right
                    self.pos.x = self.rect.x
                    self.vel.x = 0
                else:
                    if self.vel.y > 0:
                        self.rect.bottom = platform.rect.top
                        self.vel.y = 0
                    elif self.vel.y < 0:
                        self.rect.top = platform.rect.bottom
                        self.vel.y = 0
                    self.pos.y = self.rect.y

    def break_crate(self):
        """Разрушение ящика: смена спрайта на щепки и звук."""
        if not self.is_broken:
            self.is_broken = True
            self.image = self.frames[1] # Спрайт щепок
            mixer.play_sfx(self.break_sfx)
            return True
        return False

class Hole(pygame.sprite.Sprite):
    """
    Выход с уровня (мышиная нора). 
    Активируется только после сбора всего сыра.
    """
    def __init__(self, x, y):
        super().__init__()
        img = resource_manager.get_image(HOLE_PATH)
        self.image = pygame.transform.scale(img, (32 * 3, 32 * 3))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.active = False
        self.visible = False

    def activate(self):
        """Делает выход видимым и доступным."""
        if not self.active:
            self.active = True
            self.visible = True
            return True
        return False

    def draw(self, screen, offset):
        """Отрисовка норы с учетом камеры."""
        if self.visible:
            screen.blit(self.image, self.rect.topleft - offset)
