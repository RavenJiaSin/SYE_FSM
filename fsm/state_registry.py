from .idle_state import IdleState
from .carry_state import CarryState
from .wait_place_state import WaitPlaceState
from .place_state import PlaceState


STATE_MAP = {
    "idle": IdleState,
    "carry": CarryState,
    "wait_place": WaitPlaceState,
    "place": PlaceState,
}
