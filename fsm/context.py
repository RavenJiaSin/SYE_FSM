from utils.logger import Logger

from .state_registry import STATE_MAP


class FSMContext:
    def __init__(self, initial_state_name, direction=None):
        self.state = STATE_MAP[initial_state_name](self)
        self.direction = direction
        self.pass_events = set()

    def transition_to(self, state_name: str, direction=None, pass_events=None):
        Logger.fsm_info(
            f"Transitioning to {state_name} state.", direction=self.direction
        )

        if direction is not None:
            self.direction = direction

        # ✅ reset + assign
        self.pass_events = set(pass_events) if pass_events else set()

        self.state = STATE_MAP[state_name](self)

    def update(self, events):
        self.state.update(events)
