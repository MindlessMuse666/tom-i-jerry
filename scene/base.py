from core.state_machine import BaseState

class Scene(BaseState):
    def __init__(self, game):
        super().__init__(game)
