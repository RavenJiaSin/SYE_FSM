from .base_state import BaseState
from utils.logger import Logger


class IdleState(BaseState):
    def __init__(self, context):
        super().__init__(context)
        

    def update(self, events):
        
        if "GLOVE_AT_FRONT" in events:
            self.context.direction = "to_platform"
            self.context.transition_to("pick", direction=self.context.direction)
            return
        if "GLOVE_AT_SIDE" in events:
            self.context.direction = "to_platform"
            self.context.transition_to("pick", direction=self.context.direction, pass_events=["GLOVE_AT_SIDE"])
            return
        if "GLOVE_AT_PLATFORM" in events:
            self.context.direction = "to_cart"
            self.context.transition_to("pick", direction=self.context.direction)
            return
        

        return
