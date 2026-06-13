from .pick_state import PickState
from .idle_state import IdleState
from .carry_state import CarryState
from .wait_place_state import WaitPlaceState
from .place_state import PlaceState


STATE_MAP = {
    "idle": IdleState,
    "pick": PickState,
    "carry": CarryState,
    "wait_place": WaitPlaceState,
    "place": PlaceState,
}
