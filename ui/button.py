import pygame
from core.resource import resource_manager
from constant import BTN_NORMAL, BTN_HOVER, DEFAULT_FONT

class Button:
    def __init__(self, x, y, text, callback, font_size=24): # Reduced default font size from 32 to 24
        self.normal_img = resource_manager.get_image(BTN_NORMAL)
        self.hover_img = resource_manager.get_image(BTN_HOVER)
        self.rect = self.normal_img.get_rect(center=(x, y))
        self.text = text
        self.callback = callback
        self.font = resource_manager.get_font(DEFAULT_FONT, font_size)
        self.is_hovered = False

        # Render text
        self.text_surf = self.font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        # Shift text slightly up if it's too low in the button
        self.text_rect.centery -= 2 

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.is_hovered:
                    self.callback()

    def draw(self, screen):
        img = self.hover_img if self.is_hovered else self.normal_img
        screen.blit(img, self.rect)
        screen.blit(self.text_surf, self.text_rect)
