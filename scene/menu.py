import pygame
from scene.base import Scene
from ui.button import Button
from constant import SCREEN_WIDTH, SCREEN_HEIGHT, BG_MENU, BG_KITCHEN
from core.resource import resource_manager
from core.mixer import mixer
import os

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        raw_bg = resource_manager.get_image(BG_MENU)
        # Scale to screen height 720
        bg_height = 720
        bg_aspect = raw_bg.get_width() / raw_bg.get_height()
        bg_width = int(bg_height * bg_aspect)
        self.bg = pygame.transform.scale(raw_bg, (bg_width, bg_height))
        self.bg_width = self.bg.get_width()
        
        center_x = SCREEN_WIDTH // 2
        self.buttons = [
            Button(center_x, 300, "Start Game", self.start_game),
            Button(center_x, 400, "Settings", self.open_settings),
            Button(center_x, 500, "Exit", self.exit_game)
        ]

    def enter(self, **kwargs):
        # Play menu music
        from constant import MUSIC_DIR
        menu_music = os.path.join(MUSIC_DIR, "menu.mp3")
        mixer.play_music(menu_music)

    def start_game(self):
        self.game.state_machine.set_state("LEVEL", level_id=1)

    def open_settings(self):
        self.game.state_machine.set_state("SETTINGS")

    def exit_game(self):
        self.game.quit()

    def handle_events(self, events):
        for button in self.buttons:
            button.handle_events(events)

    def draw(self, screen):
        # Draw tiled/scaled background
        screen.blit(self.bg, (0, 0))
        if self.bg_width < SCREEN_WIDTH:
            screen.blit(self.bg, (self.bg_width, 0))
            
        for button in self.buttons:
            button.draw(screen)
