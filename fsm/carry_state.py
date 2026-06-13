from .base_state import BaseState
from utils.logger import Logger



class CarryState(BaseState):
    def __init__(self, context):
        super().__init__(context)
        self.no_double_hand_frames = 0
        self.missing_product_frames = 0

    def update(self, events):

        # product missing
        if 'PRODUCT_APPEAR' not in events:
            self.missing_product_frames += 1
            if self.missing_product_frames > self.context.MAX_PRODUCT_MISSING_FRAMES:
                Logger.warn("product 於搬運中消失", direction=self.context.direction)
                self.context.transition_to("idle" , direction=None)
                self.no_double_hand_frames = 0
                self.missing_product_frames = 0
            return
        else:
            self.missing_product_frames = 0

        

        # double hand check
        if 'PRODUCT_CARRIED_BY_BOTH_GLOVES' not in events:
            self.no_double_hand_frames += 1
            if self.no_double_hand_frames > self.context.MIN_DOUBLE_HAND_FRAMES:
                Logger.warn("未使用雙手搬運", direction=self.context.direction)
        else:
            self.no_double_hand_frames = 0

        # transition to wait_place
        if self.context.direction == "to_platform" and 'PRODUCT_AT_PLATFORM' in events:
            self.context.transition_to("wait_place", direction=self.context.direction)
            self.no_double_hand_frames = 0
            self.missing_product_frames = 0
            return
        if self.context.direction == "to_cart" and ('PRODUCT_AT_FRONT' in events or 'PRODUCT_AT_SIDE' in events):
            if "PRODUCT_AT_SIDE" in events:
                self.context.transition_to("wait_place", direction=self.context.direction, pass_events=["PRODUCT_AT_SIDE"])
            else:
                self.context.transition_to("wait_place",direction=self.context.direction)

            self.no_double_hand_frames = 0
            self.missing_product_frames = 0
            return

        return
