import pygame
from scene.base import Scene
from ui.button import Button
from constant import DEFAULT_FONT, LOGICAL_WIDTH, LOGICAL_HEIGHT, BG_PAUSE
from core.resource import resource_manager
from core.mixer import mixer

class PauseScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_large = resource_manager.get_font(DEFAULT_FONT, 56)
        
        # Load background
        raw_bg = resource_manager.get_image(BG_PAUSE)
        self.bg = pygame.transform.scale(raw_bg, (LOGICAL_WIDTH, LOGICAL_HEIGHT))
        
        self.overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 100)) 
        
        center_x = LOGICAL_WIDTH // 2
        self.buttons = [
            Button(center_x, 320, "Игра", self.resume_game, game=self.game),
            Button(center_x, 420, "Опции", self.open_settings, game=self.game),
            Button(center_x, 580, "Меню", self.go_to_menu, game=self.game)
        ]
        self.current_level_id = 1

    def enter(self, **kwargs):
        self.current_level_id = kwargs.get("level_id", 1)
        # We don't stop music on pause, just show overlay

    def resume_game(self):
        self.game.state_machine.set_state("LEVEL", level_id=self.current_level_id, resume=True)

    def open_settings(self):
        # Tell settings to return to PAUSE
        self.game.state_machine.get_state("SETTINGS").previous_state = "PAUSE"
        self.game.state_machine.set_state("SETTINGS")

    def go_to_menu(self):
        mixer.stop_music()
        mixer.stop_all_sfx()
        self.game.state_machine.set_state("MENU")

    def update(self, dt):
        pass

    def draw(self, screen):
        # Draw background
        screen.blit(self.bg, (0, 0))
        screen.blit(self.overlay, (0, 0))
        
        # Title
        title_surf = self.font_large.render("ПАУЗА", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(LOGICAL_WIDTH // 2, 150))
        screen.blit(title_surf, title_rect)
        
        for button in self.buttons:
            button.draw(screen)
