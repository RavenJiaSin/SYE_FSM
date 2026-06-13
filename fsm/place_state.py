from .base_state import BaseState
from utils.logger import Logger



class PlaceState(BaseState):
    def __init__(self, context):
        super().__init__(context)

    def update(self, events):
        if self.context.direction == "to_platform":
            Logger.info("完成放置於 platform", direction=self.context.direction)
            self.context.direction = None           
            self.context.transition_to("idle", direction=None)
            return
        if self.context.direction == "to_cart":
            Logger.info("完成放置於 cart", direction=self.context.direction)
            self.context.direction = None
            self.context.transition_to("idle", direction=None)
            return

        return
