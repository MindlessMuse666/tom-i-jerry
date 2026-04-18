import os

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
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

# Audio paths
MUSIC_DIR = os.path.join(AUDIO_DIR, "music")
SFX_DIR = os.path.join(AUDIO_DIR, "sfx")

# Fonts
DEFAULT_FONT = os.path.join(FONT_DIR, "VT323.ttf")
