from .base_state import BaseState
from utils.logger import Logger


class IdleState(BaseState):
    def update(self, events):

        if "PRODUCT_APPEAR" in events and "PRODUCT_CARRIED" in events:
            self.context.transition_to("carry")
            return

        # warning: idle touch platform
        if "GLOVE_IN_PLATFORM" in events:
            Logger.warn("手中沒product不應該觸碰PLATFORM")

        return
