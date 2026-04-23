import pygame
import os
from core.resource import resource_manager
from constant import DECOY_PATH, ROCKET_PATH, SFX_ROCKET_LAUNCH, SFX_EXPLOSION, SFX_CRATE_BREAK, SFX_DECOY_LAND, SFX_DECOY_MAIN
from core.mixer import mixer

class Decoy(pygame.sprite.Sprite):
    """
    Приманка-сыр, которую Джерри может бросать для отвлечения врагов.
    Приземлившись, издает звук, привлекающий внимание Тома и других противников.
    """
    def __init__(self, x: float, y: float, vel_x: float, vel_y: float):
        """
        Инициализация приманки.

        Args:
            x: Начальная координата X.
            y: Начальная координата Y.
            vel_x: Горизонтальная скорость броска.
            vel_y: Вертикальная скорость броска.
        """
        super().__init__()
        
        # Загрузка визуальных ресурсов
        self.sprite_sheet = resource_manager.get_image(DECOY_PATH)
        self.frames = self.load_frames()
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8 # Скорость анимации мигания
        
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        
        # Физические параметры
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(vel_x, vel_y)
        self.gravity = 1200
        self.friction = 300
        self.bounce = 0.2 # Коэффициент отскока
        
        self.on_ground = False
        self.bounce_count = 0
        self.life_timer = None # Устанавливается после приземления
        self.main_sound_channel = None

    def load_frames(self):
        """Разбивка спрайт-листа на отдельные кадры."""
        frames = []
        # decoy.png (64x32), 2 кадра размером 32x32
        for i in range(2):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            surf.blit(self.sprite_sheet, (0, 0), (i * 32, 0, 32, 32))
            # Масштабирование в 2 раза (64x64)
            frames.append(pygame.transform.scale(surf, (64, 64)))
        return frames
        
    def update(self, dt: float, platforms: pygame.sprite.Group):
        """
        Обновление состояния приманки.

        Args:
            dt: Дельта времени.
            platforms: Группа спрайтов платформ для обработки коллизий.
        """
        # Анимация
        self.animation_timer += dt
        if self.animation_timer >= 1.0 / self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

        # 1. Гравитация (если еще летит или отскакивает)
        if not self.on_ground:
            self.vel.y += self.gravity * dt
        
        # 2. Горизонтальное движение
        if not self.on_ground:
            self.pos.x += self.vel.x * dt
            self.rect.centerx = round(self.pos.x)
            self.check_collisions(platforms, 'horizontal')
        
        # 3. Вертикальное движение
        if not self.on_ground:
            self.pos.y += self.vel.y * dt
            self.rect.centery = round(self.pos.y)
            self.check_collisions(platforms, 'vertical')
        
        # 4. Таймер жизни (запускается после окончательной остановки)
        if self.on_ground:
            if self.life_timer is None:
                self.life_timer = 3.0
                # Запуск цикличного звука работы приманки
                self.main_sound_channel = mixer.play_sfx(resource_manager.get_sound(SFX_DECOY_MAIN), loops=-1)
            
            self.life_timer -= dt
            if self.life_timer <= 0:
                if self.main_sound_channel:
                    self.main_sound_channel.stop()
                self.kill()

    def check_collisions(self, platforms: pygame.sprite.Group, direction: str):
        """
        Обработка столкновений с платформами.

        Args:
            platforms: Платформы для проверки.
            direction: Направление движения ('horizontal' или 'vertical').
        """
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == 'horizontal':
                    if self.vel.x > 0:
                        self.rect.right = platform.rect.left
                    elif self.vel.x < 0:
                        self.rect.left = platform.rect.right
                    
                    if self.bounce_count >= 1:
                        self.vel.x = 0
                        self.on_ground = True
                    else:
                        self.vel.x *= -self.bounce
                    
                    self.bounce_count += 1
                    self.pos.x = float(self.rect.centerx)
                    # Звук удара/отскока
                    mixer.play_sfx(resource_manager.get_sound(SFX_DECOY_LAND))
                else:
                    if self.vel.y > 0: # Падение
                        self.rect.bottom = platform.rect.top
                        
                        if self.bounce_count >= 1:
                            self.vel.y = 0
                            self.vel.x = 0
                            self.on_ground = True
                        else:
                            self.vel.y *= -self.bounce
                        
                        self.bounce_count += 1
                        # Звук удара/отскока
                        mixer.play_sfx(resource_manager.get_sound(SFX_DECOY_LAND))
                    elif self.vel.y < 0: # Удар о потолок
                        self.rect.top = platform.rect.bottom
                        self.vel.y *= -self.bounce
                    self.pos.y = float(self.rect.centery)

class Rocket(pygame.sprite.Sprite):
    """
    Ракета, выпускаемая Боссом Томом.
    Летит в точку, где находился игрок в момент запуска.
    """
    def __init__(self, x: float, y: float, target_pos: tuple):
        """
        Инициализация ракеты.

        Args:
            x: Начальная координата X.
            y: Начальная координата Y.
            target_pos: Координаты цели (игрока).
        """
        super().__init__()
        import random
        img = resource_manager.get_image(ROCKET_PATH)
        # Масштабирование ракеты (16x28 -> игровое увеличение 3x)
        self.image = pygame.transform.scale(img, (16 * 3, 28 * 3))
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        
        # Базовая скорость увеличена и рандомизирована для динамики
        base_speed = 650 
        self.speed = base_speed + random.randint(-50, 50)
        
        # Таймер жизни ракеты
        self.life_timer = 6.0 
        
        # Расчет направления к цели
        direction = (pygame.Vector2(target_pos) - self.pos).normalize()
        self.vel = direction * self.speed
        
        # Вращение спрайта по направлению полета
        # Исходный спрайт смотрит ВВЕРХ (отрицательный Y)
        angle = self.vel.angle_to(pygame.Vector2(0, -1))
        self.image = pygame.transform.rotate(self.image, angle)
        
        # Звук запуска
        mixer.play_sfx(resource_manager.get_sound(SFX_ROCKET_LAUNCH))

    def update(self, dt: float):
        """
        Обновление позиции ракеты.

        Args:
            dt: Дельта времени.
        """
        self.life_timer -= dt
        if self.life_timer <= 0:
            self.kill()
            return

        self.pos += self.vel * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
        # Удаление при выходе за расширенные границы уровня
        if self.pos.x < -500 or self.pos.x > 5500 or self.pos.y < -500 or self.pos.y > 1500:
            self.kill()

    def explode(self):
        """Проигрывание звука взрыва и удаление объекта."""
        mixer.play_sfx(resource_manager.get_sound(SFX_EXPLOSION))
        self.kill()
