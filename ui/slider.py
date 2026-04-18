import pygame
from core.resource import resource_manager
from constant import SLIDER_BG, SLIDER_HANDLE

class Slider:
    def __init__(self, x, y, width, value, callback):
        self.bg_img = resource_manager.get_image(SLIDER_BG)
        # Scale background if needed, but the specification says 200x20
        self.rect = self.bg_img.get_rect(topleft=(x, y))
        self.width = width # Logic width
        
        self.handle_img = resource_manager.get_image(SLIDER_HANDLE)
        self.handle_rect = self.handle_img.get_rect(center=(x + value * width, self.rect.centery))
        
        self.value = value
        self.callback = callback
        self.dragging = False

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.handle_rect.collidepoint(mouse_pos):
                    self.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
        
        if self.dragging:
            # Update value based on mouse position
            new_x = max(self.rect.left, min(mouse_pos[0], self.rect.right))
            self.value = (new_x - self.rect.left) / self.width
            self.handle_rect.centerx = new_x
            self.callback(self.value)

    def draw(self, screen):
        screen.blit(self.bg_img, self.rect)
        screen.blit(self.handle_img, self.handle_rect)
