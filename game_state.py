class GameStateManager:
    def __init__(self, current_state):
        self.current_state = current_state
        self.previous_state = None

    def get_state(self):
        return self.current_state

    def set_state(self, state):
        self.previous_state = self.current_state
        self.current_state = state

    def get_previous_state(self):
        return self.previous_state

    def remove_state(self):
        self.previous_state = None
        self.set_state("start")
