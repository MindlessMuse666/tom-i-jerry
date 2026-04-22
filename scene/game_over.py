import pygame
from scene.base import Scene
from ui.button import Button
from constant import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_FONT, BG_GAME_OVER, LOGICAL_WIDTH, LOGICAL_HEIGHT
from core.resource import resource_manager
from core.mixer import mixer
import os

class GameOverScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.cheese_count = 0
        self.font_large = resource_manager.get_font(DEFAULT_FONT, 56) # Reduced from 72 to 56
        self.font_medium = resource_manager.get_font(DEFAULT_FONT, 32) # Reduced from 48 to 32
        
        # Load background
        raw_bg = resource_manager.get_image(BG_GAME_OVER)
        self.bg = pygame.transform.scale(raw_bg, (LOGICAL_WIDTH, LOGICAL_HEIGHT))
        
        # Background blur/darken overlay
        self.overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 100)) # Dark semi-transparent overlay
        
        center_x = LOGICAL_WIDTH // 2
        self.buttons = [
            Button(center_x, 450, "Заново", self.restart_level, game=self.game),
            Button(center_x, 550, "В меню", self.go_to_menu, game=self.game)
        ]

    def enter(self, **kwargs):
        self.cheese_count = kwargs.get("cheese_count", 0)
        # Stop background music and all ongoing SFX
        mixer.stop_music()
        mixer.stop_all_sfx()
        from constant import SFX_DIR
        game_over_music = os.path.join(SFX_DIR, "game_over.mp3")
        mixer.play_music(game_over_music, loop=0) # Play once

    def restart_level(self):
        # We need to know which level to restart. For now, default to 1.
        # In a real game, this would be passed via kwargs.
        self.game.state_machine.set_state("LEVEL", level_id=1)

    def go_to_menu(self):
        self.game.state_machine.set_state("MENU")

    def update(self, dt):
        pass

    def draw(self, screen):
        # Draw background
        screen.blit(self.bg, (0, 0))
        screen.blit(self.overlay, (0, 0))
        
        # Game Over Text
        title_surf = self.font_large.render("ИГРА ОКОНЧЕНА", True, (255, 50, 50))
        title_rect = title_surf.get_rect(center=(LOGICAL_WIDTH // 2, 200))
        screen.blit(title_surf, title_rect)
        
        # Score Text
        score_surf = self.font_medium.render(f"Собрано сыра: {self.cheese_count}", True, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(LOGICAL_WIDTH // 2, 300))
        screen.blit(score_surf, score_rect)
        
        for button in self.buttons:
            button.draw(screen)
