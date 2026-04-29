from .base_state import BaseState
from utils.logger import Logger


class WaitPlaceState(BaseState):
    def __init__(self, context):
        super().__init__(context)
        self.timeout_frame_counter = 0
        self.missing_product_frames = 0

    def update(self, events):

        self.timeout_frame_counter += 1

        # success condition
        if 'PRODUCT_APPEAR' not in events:
            self.missing_product_frames += 1
            if self.missing_product_frames > self.context.N_MISSING_FRAMES:
                self.context.transition_to("place")
                self.timeout_frame_counter = 0
                self.missing_product_frames = 0

        # timeout
        if self.timeout_frame_counter > self.context.WAIT_TIMEOUT_FRAMES:
            Logger.warn("未完成放置動作（timeout）")
            self.context.transition_to("carry")

        return
