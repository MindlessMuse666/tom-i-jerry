import pygame
from scene.base import Scene
from ui.button import Button
from constant import SCREEN_WIDTH, SCREEN_HEIGHT, BG_MENU, BG_KITCHEN, LOGICAL_WIDTH, LOGICAL_HEIGHT
from core.resource import resource_manager
from core.mixer import mixer
import os

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        raw_bg = resource_manager.get_image(BG_MENU)
        # Scale to full logical resolution 1280x720 as requested
        self.bg = pygame.transform.scale(raw_bg, (LOGICAL_WIDTH, LOGICAL_HEIGHT))
        
        center_x = LOGICAL_WIDTH // 2
        self.buttons = [
            Button(center_x, 320, "Начать", self.start_game, game=self.game),
            Button(center_x, 420, "Опции", self.open_settings, game=self.game),
            Button(center_x, 580, "Выход", self.exit_game, game=self.game)
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

    def draw(self, screen):
        # Draw full background
        screen.blit(self.bg, (0, 0))
            
        for button in self.buttons:
            button.draw(screen)

