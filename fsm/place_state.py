from .base_state import BaseState




class PlaceState(BaseState):
    def __init__(self, context):
        super().__init__(context)
        self.place_frames = 0

    def update(self, events):
        if 'GLOVE_IN_PLATFORM' not in events:
            self.context.transition_to("idle")
        if self.place_frames > self.context.MIN_PLACE_FRAMES:
            self.context.transition_to("idle")
        else:
            self.place_frames += 1

        return
