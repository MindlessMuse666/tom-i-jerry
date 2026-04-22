import pygame
import os
from scene.base import Scene
from ui.button import Button
from constant import DEFAULT_FONT, LOGICAL_WIDTH, LOGICAL_HEIGHT
from core.resource import resource_manager
from core.mixer import mixer

class LevelWinScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.cheese_count = 0
        self.current_level_id = 1
        self.font_large = resource_manager.get_font(DEFAULT_FONT, 56)
        self.font_medium = resource_manager.get_font(DEFAULT_FONT, 32)
        
        self.overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180)) 
        
        center_x = LOGICAL_WIDTH // 2
        self.buttons = [
            Button(center_x, 450, "Вперёд!", self.next_level),
            Button(center_x, 550, "В меню", self.go_to_menu)
        ]

    def enter(self, **kwargs):
        self.cheese_count = kwargs.get("cheese_count", 0)
        self.current_level_id = kwargs.get("level_id", 1)
        # Stop background music and all ongoing SFX
        mixer.stop_music()
        mixer.stop_all_sfx()
        from constant import SFX_WIN
        mixer.play_sfx(resource_manager.get_sound(SFX_WIN))

    def next_level(self):
        next_id = self.current_level_id + 1
        # Check if next level exists
        next_path = os.path.join("level", f"level{next_id}.json")
        if os.path.exists(next_path):
            self.game.state_machine.set_state("LEVEL", level_id=next_id)
        else:
            # All levels finished!
            self.game.state_machine.set_state("MENU")

    def go_to_menu(self):
        self.game.state_machine.set_state("MENU")

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((20, 20, 20)) 
        screen.blit(self.overlay, (0, 0))
        
        # Title
        title_surf = self.font_large.render("УРОВЕНЬ ПРОЙДЕН!", True, (50, 255, 50))
        title_rect = title_surf.get_rect(center=(LOGICAL_WIDTH // 2, 200))
        screen.blit(title_surf, title_rect)
        
        # Stats
        score_surf = self.font_medium.render(f"Собрано сыра: {self.cheese_count}", True, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(LOGICAL_WIDTH // 2, 300))
        screen.blit(score_surf, score_rect)
        
        for button in self.buttons:
            button.draw(screen)
