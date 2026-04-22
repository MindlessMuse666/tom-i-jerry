import pygame
from core.resource import resource_manager
from core.mixer import mixer
from constant import BTN_NORMAL, BTN_HOVER, DEFAULT_FONT, SFX_UI_CLICK

class Button:
    def __init__(self, x, y, text, callback, font_size=32, game=None, width=280, height=80): 
        self.game = game
        raw_normal = resource_manager.get_image(BTN_NORMAL)
        raw_hover = resource_manager.get_image(BTN_HOVER)
        
        # Scale button images
        self.normal_img = pygame.transform.scale(raw_normal, (width, height))
        self.hover_img = pygame.transform.scale(raw_hover, (width, height))
        
        self.rect = self.normal_img.get_rect(center=(x, y))
        self.text = text
        self.callback = callback
        self.font = resource_manager.get_font(DEFAULT_FONT, font_size)
        self.is_hovered = False
        self.is_selected = False
        
        # Determine cursor type
        self.cursor_type = "select"
        if text in ["Выход", "Меню", "Назад"]:
            self.cursor_type = "cancel"

        # Pre-load click sound
        self.click_sfx = resource_manager.get_sound(SFX_UI_CLICK)

        # Render text
        self.text_surf = self.font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        # Shift text slightly up if it's too low in the button
        self.text_rect.centery -= 2 

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if self.is_hovered and self.game:
            self.game.current_cursor_type = self.cursor_type

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.is_hovered:
                    self.click()

    def click(self):
        mixer.play_sfx(self.click_sfx)
        self.callback()

    def draw(self, screen):
        img = self.hover_img if (self.is_hovered or self.is_selected) else self.normal_img
        screen.blit(img, self.rect)
        screen.blit(self.text_surf, self.text_rect)

