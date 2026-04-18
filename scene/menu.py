import pygame
from scene.base import Scene
from ui.button import Button
from constant import SCREEN_WIDTH, SCREEN_HEIGHT, BG_MENU
from core.resource import resource_manager

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.bg = resource_manager.get_image(BG_MENU)
        
        center_x = SCREEN_WIDTH // 2
        self.buttons = [
            Button(center_x, 300, "Start Game", self.start_game),
            Button(center_x, 400, "Settings", self.open_settings),
            Button(center_x, 500, "Exit", self.exit_game)
        ]

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
        screen.blit(self.bg, (0, 0))
        for button in self.buttons:
            button.draw(screen)
