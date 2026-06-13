from .base_state import BaseState
from utils.logger import Logger


class PickState(BaseState):
    def __init__(self, context):
        super().__init__(context)
        self.pickup_frames = 0

    def update(self, events):
        self.pickup_frames += 1

        if "PRODUCT_APPEAR" in events and "PRODUCT_CARRIED" in events:
            if self.context.pass_events == {"GLOVE_AT_SIDE"}:
                Logger.warn("從側邊拿取 PRODUCT", direction=self.context.direction)
            self.context.transition_to("carry", direction=self.context.direction)
            self.pickup_frames = 0
            return

        if self.pickup_frames > self.context.MAX_PICK_UP_FRAMES:
            # warning: touch platform but not pick up product
            if "GLOVE_AT_PLATFORM" in events:
                Logger.warn("手中沒product不應該觸碰PLATFORM")
            self.context.direction = None
            self.context.transition_to("idle", direction=None)
            self.pickup_frames = 0
            return

        return
