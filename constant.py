"""
Глобальные константы и настройки путей проекта.
Здесь определены параметры экрана, цвета и пути ко всем ресурсам игры.
"""

import os
import pygame
import ctypes

# Настройка осведомленности о DPI для корректного отображения на Windows
try:
    ctypes.windll.user32.SetProcessDPIAware()
    SCREEN_WIDTH = ctypes.windll.user32.GetSystemMetrics(0)
    SCREEN_HEIGHT = ctypes.windll.user32.GetSystemMetrics(1)
except Exception:
    # Значения по умолчанию для других систем или в случае ошибки
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720

# Логическое разрешение (внутреннее разрешение отрисовки)
LOGICAL_WIDTH = 1280
LOGICAL_HEIGHT = 720
FPS = 60

# Цветовая палитра
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Базовые директории
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "asset")
VISUAL_DIR = os.path.join(ASSET_DIR, "visual")
AUDIO_DIR = os.path.join(ASSET_DIR, "audio")
FONT_DIR = os.path.join(ASSET_DIR, "font")

# Пути к спрайтам сущностей
ENTITY_DIR = os.path.join(VISUAL_DIR, "entity")
PLAYER_PATH = os.path.join(ENTITY_DIR, "player", "player.png")
TOM_PATH = os.path.join(ENTITY_DIR, "enemy", "tom", "tom.png")
BROOM_PATH = os.path.join(ENTITY_DIR, "enemy", "broom", "broom.png")
BOSS_PATH = os.path.join(ENTITY_DIR, "enemy", "boss_tom", "boss_tom.png")
CHEESE_PATH = os.path.join(ENTITY_DIR, "env", "cheese", "cheese.png")
RED_CHEESE_PATH = os.path.join(ENTITY_DIR, "env", "cheese", "red_cheese.png")
CRATE_PATH = os.path.join(ENTITY_DIR, "env", "crate", "crate.png")
TRAP_PATH = os.path.join(ENTITY_DIR, "env", "trap", "trap.png")
HOLE_PATH = os.path.join(ENTITY_DIR, "env", "hole", "hole.png")
DECOY_PATH = os.path.join(ENTITY_DIR, "projectile", "decoy", "decoy.png")
ROCKET_PATH = os.path.join(ENTITY_DIR, "projectile", "rocket", "rocket.png")

# Пути к элементам интерфейса
UI_DIR = os.path.join(VISUAL_DIR, "ui")
BG_DIR = os.path.join(UI_DIR, "bg")
BTN_DIR = os.path.join(UI_DIR, "btn")
HUD_DIR = os.path.join(UI_DIR, "hud")
SLIDER_DIR = os.path.join(UI_DIR, "slider")
CURSOR_DIR = os.path.join(ASSET_DIR, "cursor")

# Курсоры
CUR_BASIC = os.path.join(CURSOR_DIR, "cur_basic.png")
CUR_SELECT = os.path.join(CURSOR_DIR, "cur_select.png")
CUR_CANCEL = os.path.join(CURSOR_DIR, "cur_cancel.png")
CUR_SLIDER = os.path.join(CURSOR_DIR, "cur_slider.png")

# Фоновые изображения
BG_MENU = os.path.join(BG_DIR, "bg_menu.png")
BG_GAME_OVER = os.path.join(BG_DIR, "bg_game_over.png")
BG_PAUSE = os.path.join(BG_DIR, "bg_pause.png")
BG_WIN = os.path.join(BG_DIR, "bg_win.png")
BG_KITCHEN = os.path.join(BG_DIR, "bg_kitchen.png")
BG_BASEMENT = os.path.join(BG_DIR, "bg_basement.png")
BG_GARAGE = os.path.join(BG_DIR, "bg_garage.png")

# Кнопки
BTN_NORMAL = os.path.join(BTN_DIR, "btn.png")
BTN_HOVER = os.path.join(BTN_DIR, "btn_hover.png")

# HUD
HEART_FULL = os.path.join(HUD_DIR, "heart.png")
HEART_EMPTY = os.path.join(HUD_DIR, "heart_empty.png")
CHEESE_HUD = os.path.join(HUD_DIR, "cheese_hud.png")
CHEESE_HUD_EMPTY = os.path.join(HUD_DIR, "cheese_empty.png")

# Слайдеры
SLIDER_BG = os.path.join(SLIDER_DIR, "slider_bg.png")
SLIDER_HANDLE = os.path.join(SLIDER_DIR, "slider_handle.png")

# Окружение
ENV_DIR = os.path.join(UI_DIR, "env")
GROUND_PATH = os.path.join(ENV_DIR, "ground.png")
PLATFORM_PATH = os.path.join(ENV_DIR, "platform.png")
MOVING_PLATFORM_PATH = os.path.join(ENV_DIR, "moving_platform.png")

# Музыка и звуки
MUSIC_DIR = os.path.join(AUDIO_DIR, "music")
SFX_DIR = os.path.join(AUDIO_DIR, "sfx")

# Звуковые эффекты
SFX_JUMP = os.path.join(SFX_DIR, "jump.mp3")
SFX_CHEESE = os.path.join(SFX_DIR, "cheese.mp3")
SFX_HURT = os.path.join(SFX_DIR, "hurt.mp3")
SFX_CRATE_BREAK = os.path.join(SFX_DIR, "crate_break.mp3")
SFX_TRAP_SNAP = os.path.join(SFX_DIR, "trap_snap.mp3")
SFX_UI_CLICK = os.path.join(SFX_DIR, "ui_click.mp3")
SFX_WIN = os.path.join(SFX_DIR, "win.mp3")
SFX_ROCKET_LAUNCH = os.path.join(SFX_DIR, "rocket_launch.mp3")
SFX_EXPLOSION = os.path.join(SFX_DIR, "explosion.mp3")
SFX_TOM_DEATH = os.path.join(SFX_DIR, "tom_death.mp3")
SFX_BOSS_DEATH = os.path.join(SFX_DIR, "boss_death.mp3")
SFX_LEVEL_START = os.path.join(SFX_DIR, "level_start.mp3")
SFX_DECOY_THROW = os.path.join(SFX_DIR, "decoy_throw.mp3")
SFX_DECOY_LAND = os.path.join(SFX_DIR, "decoy_land.mp3")
SFX_DECOY_MAIN = os.path.join(SFX_DIR, "decoy_main.mp3")

# Шрифты
DEFAULT_FONT = os.path.join(FONT_DIR, "public-pixel.ttf")
