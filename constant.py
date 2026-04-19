import os
import pygame
import ctypes

# DPI Awareness for Windows
try:
    ctypes.windll.user32.SetProcessDPIAware()
    SCREEN_WIDTH = ctypes.windll.user32.GetSystemMetrics(0)
    SCREEN_HEIGHT = ctypes.windll.user32.GetSystemMetrics(1)
except Exception:
    # Fallback for non-windows or errors
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720

LOGICAL_WIDTH = 1280
LOGICAL_HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "asset")
VISUAL_DIR = os.path.join(ASSET_DIR, "visual")
AUDIO_DIR = os.path.join(ASSET_DIR, "audio")
FONT_DIR = os.path.join(ASSET_DIR, "font")

# Entity visual paths
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

# UI visual paths
UI_DIR = os.path.join(VISUAL_DIR, "ui")
BG_DIR = os.path.join(UI_DIR, "bg")
BTN_DIR = os.path.join(UI_DIR, "btn")
HUD_DIR = os.path.join(UI_DIR, "hud")
SLIDER_DIR = os.path.join(UI_DIR, "slider")

BG_MENU = os.path.join(BG_DIR, "bg_menu.png")
BG_KITCHEN = os.path.join(BG_DIR, "bg_kitchen.png")
BG_BASEMENT = os.path.join(BG_DIR, "bg_basement.png")
BG_GARAGE = os.path.join(BG_DIR, "bg_garage.png")

BTN_NORMAL = os.path.join(BTN_DIR, "btn.png")
BTN_HOVER = os.path.join(BTN_DIR, "btn_hover.png")

HEART_FULL = os.path.join(HUD_DIR, "heart.png")
HEART_EMPTY = os.path.join(HUD_DIR, "heart_empty.png")
CHEESE_HUD = os.path.join(HUD_DIR, "cheese_hud.png")
CHEESE_HUD_EMPTY = os.path.join(HUD_DIR, "cheese_empty.png")

SLIDER_BG = os.path.join(SLIDER_DIR, "slider_bg.png")
SLIDER_HANDLE = os.path.join(SLIDER_DIR, "slider_handle.png")

# Environment visual paths
ENV_DIR = os.path.join(UI_DIR, "env")
GROUND_PATH = os.path.join(ENV_DIR, "ground.png")
PLATFORM_PATH = os.path.join(ENV_DIR, "platform.png")
MOVING_PLATFORM_PATH = os.path.join(ENV_DIR, "moving_platform.png")

# Audio paths
MUSIC_DIR = os.path.join(AUDIO_DIR, "music")
SFX_DIR = os.path.join(AUDIO_DIR, "sfx")

# SFX paths
SFX_JUMP = os.path.join(SFX_DIR, "jump.mp3")
SFX_CHEESE = os.path.join(SFX_DIR, "cheese.mp3")
SFX_HURT = os.path.join(SFX_DIR, "hurt.mp3")
SFX_CRATE_BREAK = os.path.join(SFX_DIR, "crate_break.mp3")
SFX_TRAP_SNAP = os.path.join(SFX_DIR, "trap_snap.mp3")
SFX_UI_CLICK = os.path.join(SFX_DIR, "ui_click.mp3")
SFX_WIN = os.path.join(SFX_DIR, "win.mp3")

# Fonts
DEFAULT_FONT = os.path.join(FONT_DIR, "VT323.ttf")
