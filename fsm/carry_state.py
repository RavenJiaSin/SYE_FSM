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
            if self.missing_product_frames > self.context.N_MISSING_FRAMES:
                Logger.warn("product 於搬運中消失")
                self.context.transition_to("idle")
            return
        else:
            self.missing_product_frames = 0

        # product at front or side
        if 'PRODUCT_AT_FRONT' in events and 'PRODUCT_CARRIED' in events:
            # Logger.warn("product 自front出現")
            pass
        if 'PRODUCT_AT_SIDE' in events:
            Logger.warn("product 自 side 出現")

        # double hand check
        if 'PRODUCT_CARRIED_BY_BOTH_GLOVES' not in events:
            self.no_double_hand_frames += 1
            if self.no_double_hand_frames > self.context.N_DOUBLE_HAND_FRAMES:
                Logger.warn("未使用雙手搬運")
        else:
            self.no_double_hand_frames = 0

        # transition to wait_place
        if 'PRODUCT_IN_PLATFORM' in events:
            self.context.transition_to("wait_place")

        return
