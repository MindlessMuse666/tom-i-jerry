import pygame
from scene.base import Scene
from ui.button import Button
from ui.slider import Slider
from constant import SCREEN_WIDTH, SCREEN_HEIGHT, BG_MENU, DEFAULT_FONT
from core.resource import resource_manager
from setting import settings

class SettingsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.bg = resource_manager.get_image(BG_MENU)
        self.font = resource_manager.get_font(DEFAULT_FONT, 48)
        
        center_x = SCREEN_WIDTH // 2
        
        # Volume Sliders
        self.music_slider = Slider(center_x - 100, 300, 200, settings.music_volume, self.set_music_volume)
        self.sfx_slider = Slider(center_x - 100, 400, 200, settings.sfx_volume, self.set_sfx_volume)
        
        self.back_button = Button(center_x, 550, "Back", self.go_back)
        
        # Labels
        self.music_label = self.font.render("Music Volume", True, (255, 255, 255))
        self.sfx_label = self.font.render("SFX Volume", True, (255, 255, 255))

    def set_music_volume(self, value):
        settings.music_volume = value
        pygame.mixer.music.set_volume(value)
        settings.save()

    def set_sfx_volume(self, value):
        settings.sfx_volume = value
        # Update volume for all loaded sounds? Or just set global
        settings.save()

    def go_back(self):
        self.game.state_machine.set_state("MENU")

    def handle_events(self, events):
        self.music_slider.handle_events(events)
        self.sfx_slider.handle_events(events)
        self.back_button.handle_events(events)

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        
        # Draw labels
        screen.blit(self.music_label, (SCREEN_WIDTH // 2 - self.music_label.get_width() // 2, 250))
        screen.blit(self.sfx_label, (SCREEN_WIDTH // 2 - self.sfx_label.get_width() // 2, 350))
        
        self.music_slider.draw(screen)
        self.sfx_slider.draw(screen)
        self.back_button.draw(screen)
