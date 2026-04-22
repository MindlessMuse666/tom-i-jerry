import pygame
from constant import SCREEN_WIDTH, SCREEN_HEIGHT, LOGICAL_WIDTH, LOGICAL_HEIGHT
from setting import settings
from core.state_machine import StateMachine

class Game:
    def __init__(self):
        # Set up display
        # Use SCALED to automatically handle the internal logical resolution
        # and FULLSCREEN to use the actual monitor resolution
        flags = pygame.SCALED | pygame.FULLSCREEN
        
        # We set the logical resolution as the base, 
        # and SCALED will stretch it to SCREEN_WIDTH/HEIGHT
        self.screen = pygame.display.set_mode((LOGICAL_WIDTH, LOGICAL_HEIGHT), flags)
        pygame.display.set_caption("Jerry's Escape from the Crazy Cat's House")
        
        self.running = True
        self.state_machine = StateMachine()
        
        from scene.menu import MenuScene
        from scene.settings import SettingsScene
        from scene.level import LevelScene
        from scene.game_over import GameOverScene
        from scene.level_win import LevelWinScene
        from scene.pause import PauseScene
        from scene.credits import CreditsScene
        
        self.state_machine.add_state("MENU", MenuScene(self))
        self.state_machine.add_state("SETTINGS", SettingsScene(self))
        self.state_machine.add_state("LEVEL", LevelScene(self))
        self.state_machine.add_state("GAME_OVER", GameOverScene(self))
        self.state_machine.add_state("LEVEL_WIN", LevelWinScene(self))
        self.state_machine.add_state("PAUSE", PauseScene(self))
        self.state_machine.add_state("CREDITS", CreditsScene(self))
        self.state_machine.set_state("MENU")
        
        # Set window icon
        try:
            icon = pygame.image.load("asset/other/icon.ico")
            pygame.display.set_icon(icon)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Cursor handling
        pygame.mouse.set_visible(False)
        from constant import CUR_BASIC, CUR_SELECT, CUR_CANCEL, CUR_SLIDER
        from core.resource import resource_manager
        self.cursors = {
            "basic": resource_manager.get_image(CUR_BASIC),
            "select": resource_manager.get_image(CUR_SELECT),
            "cancel": resource_manager.get_image(CUR_CANCEL),
            "slider": resource_manager.get_image(CUR_SLIDER)
        }
        self.current_cursor_type = "basic"

    def handle_events(self):
        events = pygame.event.get()
        # Reset cursor type to basic each frame, buttons will change it if hovered
        self.current_cursor_type = "basic"
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        
        self.state_machine.handle_events(events)

    def update(self, dt):
        self.state_machine.update(dt)

    def draw(self):
        self.screen.fill((0, 0, 0)) # Default black fill
        self.state_machine.draw(self.screen)
        
        # Draw custom cursor last
        cursor_img = self.cursors.get(self.current_cursor_type, self.cursors["basic"])
        self.screen.blit(cursor_img, pygame.mouse.get_pos())
        
        pygame.display.flip()

    def quit(self):
        self.running = False
