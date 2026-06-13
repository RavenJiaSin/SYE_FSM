from .base_state import BaseState
from utils.logger import Logger


class WaitPlaceState(BaseState):
    def __init__(self, context):
        super().__init__(context)
        self.timeout_frame_counter = 0
        self.product_placing_frames = 0

    def update(self, events):

        self.timeout_frame_counter += 1

        # success condition
        if 'PRODUCT_APPEAR' not in events:
            self.product_placing_frames += 1
            if self.product_placing_frames > self.context.MIN_PLACING_FRAMES:
                if self.context.pass_events == {"PRODUCT_AT_SIDE"}:
                    Logger.warn("從側邊放置 PRODUCT", direction=self.context.direction)
                self.context.transition_to("place", direction=self.context.direction)
                self.timeout_frame_counter = 0
                self.product_placing_frames = 0
                return

        # timeout
        if self.timeout_frame_counter > self.context.MAX_PLACING_FRAMES:
            Logger.warn("未完成放置動作（timeout）", direction=self.context.direction)
            self.context.transition_to("carry", direction=self.context.direction)
            self.timeout_frame_counter = 0
            self.product_placing_frames = 0
            return

        return
