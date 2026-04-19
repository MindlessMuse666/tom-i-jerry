import pygame
from scene.base import Scene
from ui.button import Button
from constant import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_FONT, BG_MENU, LOGICAL_WIDTH, LOGICAL_HEIGHT
from core.resource import resource_manager
from core.mixer import mixer
import os

class GameOverScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.cheese_count = 0
        self.font_large = resource_manager.get_font(DEFAULT_FONT, 72)
        self.font_medium = resource_manager.get_font(DEFAULT_FONT, 48)
        
        # Background blur/darken will be handled in draw
        self.overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180)) # Dark semi-transparent overlay
        
        center_x = LOGICAL_WIDTH // 2
        self.buttons = [
            Button(center_x, 450, "Restart", self.restart_level),
            Button(center_x, 550, "Main Menu", self.go_to_menu)
        ]

    def enter(self, **kwargs):
        self.cheese_count = kwargs.get("cheese_count", 0)
        from constant import SFX_DIR
        game_over_music = os.path.join(SFX_DIR, "game_over.mp3")
        mixer.play_music(game_over_music, loop=0) # Play once

    def restart_level(self):
        # We need to know which level to restart. For now, default to 1.
        # In a real game, this would be passed via kwargs.
        self.game.state_machine.set_state("LEVEL", level_id=1)

    def go_to_menu(self):
        self.game.state_machine.set_state("MENU")

    def handle_events(self, events):
        for button in self.buttons:
            button.handle_events(events)

    def update(self, dt):
        pass

    def draw(self, screen):
        # The game screen should have been drawn already if we use a stack, 
        # but our StateMachine is simple and replaces states.
        # To get the "blur" effect, we'd need to capture the last frame of the level.
        # For now, we'll just draw the darkened overlay over the menu background 
        # as a placeholder or just the dark overlay.
        
        screen.fill((20, 20, 20)) # Very dark background
        screen.blit(self.overlay, (0, 0))
        
        # Game Over Text
        title_surf = self.font_large.render("GAME OVER", True, (255, 50, 50))
        title_rect = title_surf.get_rect(center=(LOGICAL_WIDTH // 2, 200))
        screen.blit(title_surf, title_rect)
        
        # Score Text
        score_surf = self.font_medium.render(f"Cheese Collected: {self.cheese_count}", True, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(LOGICAL_WIDTH // 2, 300))
        screen.blit(score_surf, score_rect)
        
        for button in self.buttons:
            button.draw(screen)
