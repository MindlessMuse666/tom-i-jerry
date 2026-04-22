import pygame
from scene.base import Scene
from ui.button import Button
from ui.slider import Slider
from constant import SCREEN_WIDTH, SCREEN_HEIGHT, BG_MENU, DEFAULT_FONT, LOGICAL_WIDTH, LOGICAL_HEIGHT
from core.resource import resource_manager
from setting import settings

class SettingsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        raw_bg = resource_manager.get_image(BG_MENU)
        self.bg = pygame.transform.scale(raw_bg, (LOGICAL_WIDTH, LOGICAL_HEIGHT))
        self.font = resource_manager.get_font(DEFAULT_FONT, 32)
        self.previous_state = "MENU"
        
        center_x = LOGICAL_WIDTH // 2
        
        # Labels - Colored
        self.music_label = self.font.render("Музыка", True, (255, 50, 50)) # Red-ish
        self.sfx_label = self.font.render("Эффекты", True, (50, 150, 255)) # Blue-ish
        
        # Volume Sliders - Increased width and better vertical spacing
        slider_w = 400
        self.music_slider = Slider(center_x - slider_w // 2, 220, slider_w, settings.music_volume, self.set_music_volume, game=self.game)
        self.sfx_slider = Slider(center_x - slider_w // 2, 420, slider_w, settings.sfx_volume, self.set_sfx_volume, game=self.game)
        
        # Back Button - Lowered to separate it from sliders
        self.back_button = Button(center_x, 620, "Назад", self.go_back, game=self.game)
        self.buttons = [self.back_button]

    def set_music_volume(self, value):
        settings.music_volume = value
        pygame.mixer.music.set_volume(value)
        settings.save()

    def set_sfx_volume(self, value):
        settings.sfx_volume = value
        resource_manager.set_sfx_volume(value)
        settings.save()

    def go_back(self):
        # We need to know where we came from (MENU or PAUSE)
        self.game.state_machine.set_state(self.previous_state)
        # Reset to default
        self.previous_state = "MENU"

    def handle_events(self, events):
        self.music_slider.handle_events(events)
        self.sfx_slider.handle_events(events)
        super().handle_events(events)

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        
        # Draw labels - Positioned above sliders
        screen.blit(self.music_label, (LOGICAL_WIDTH // 2 - self.music_label.get_width() // 2, 170))
        screen.blit(self.sfx_label, (LOGICAL_WIDTH // 2 - self.sfx_label.get_width() // 2, 370))
        
        self.music_slider.draw(screen)
        self.sfx_slider.draw(screen)
        self.back_button.draw(screen)
