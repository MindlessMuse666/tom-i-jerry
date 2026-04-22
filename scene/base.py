from core.state_machine import BaseState

import pygame

class Scene(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.selected_button_index = -1 # No button selected by default

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
                        if self.selected_button_index == -1:
                            self.selected_button_index = len(self.buttons) - 1
                        else:
                            self.selected_button_index = (self.selected_button_index - 1) % len(self.buttons)
                    elif event.key == pygame.K_DOWN:
                        if self.selected_button_index == -1:
                            self.selected_button_index = 0
                        else:
                            self.selected_button_index = (self.selected_button_index + 1) % len(self.buttons)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_button_index == -1:
                            # If no selection, select the first one on Enter
                            self.selected_button_index = 0
                            self.buttons[0].click()
                        else:
                            self.buttons[self.selected_button_index].click()
            
            # Update selected state and handle mouse
            for i, button in enumerate(self.buttons):
                button.is_selected = (i == self.selected_button_index)
                button.handle_events(events)
                # If mouse hovers over a button, it takes over selection
                if button.is_hovered:
                    self.selected_button_index = i

    def update(self, dt):
        pass

    def draw(self, screen):
        pass
