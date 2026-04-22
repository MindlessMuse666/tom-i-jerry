from core.state_machine import BaseState

import pygame

class Scene(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.selected_button_index = 0

    def enter(self, **kwargs):
        pass

    def exit(self):
        pass

    def handle_events(self, events):
        # Default button navigation
        if self.buttons:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_button_index = (self.selected_button_index - 1) % len(self.buttons)
                    elif event.key == pygame.K_DOWN:
                        self.selected_button_index = (self.selected_button_index + 1) % len(self.buttons)
                    elif event.key == pygame.K_RETURN:
                        self.buttons[self.selected_button_index].click()
            
            # Update selected state
            for i, button in enumerate(self.buttons):
                button.is_selected = (i == self.selected_button_index)
                button.handle_events(events)

    def update(self, dt):
        pass

    def draw(self, screen):
        pass
