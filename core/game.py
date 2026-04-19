import pygame
from constant import SCREEN_WIDTH, SCREEN_HEIGHT
from setting import settings
from core.state_machine import StateMachine

class Game:
    def __init__(self):
        # Set up display
        flags = pygame.SCALED
        if settings.fullscreen:
            flags |= pygame.FULLSCREEN
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption("Jerry's Escape from the Crazy Cat's House")
        
        self.running = True
        self.state_machine = StateMachine()
        
        from scene.menu import MenuScene
        from scene.settings import SettingsScene
        from scene.level import LevelScene
        from scene.game_over import GameOverScene
        
        self.state_machine.add_state("MENU", MenuScene(self))
        self.state_machine.add_state("SETTINGS", SettingsScene(self))
        self.state_machine.add_state("LEVEL", LevelScene(self))
        self.state_machine.add_state("GAME_OVER", GameOverScene(self))
        self.state_machine.set_state("MENU")

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        
        self.state_machine.handle_events(events)

    def update(self, dt):
        self.state_machine.update(dt)

    def draw(self):
        self.screen.fill((0, 0, 0)) # Default black fill
        self.state_machine.draw(self.screen)
        pygame.display.flip()

    def quit(self):
        self.running = False
