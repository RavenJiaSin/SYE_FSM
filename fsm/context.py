from .state_registry import STATE_MAP


class FSMContext:
    def __init__(self, initial_state_name):
        self.state = STATE_MAP[initial_state_name](self)

    def transition_to(self, state_name: str):
        print(f"Transitioning to {state_name} state.")
        self.state = STATE_MAP[state_name](self)

    def update(self, events):
        self.state.update(events)
