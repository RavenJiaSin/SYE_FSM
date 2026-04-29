import time
import config as cfg

from vision.camera_client import CameraClient
from vision.od_client import ODClient
from vision.efs_client import EFSClient
from vision.perception import Perception
from vision.vision_system import VisionSystem

from vision.event_engine import EventEngine


# ================= INIT =================
URL = cfg.URL
CAM_NAME = cfg.CAM_NAME
CAM_SRC = cfg.CAM_SRC
TASK = cfg.TASK_NAME


camera = CameraClient(URL)
od = ODClient(URL, TASK)
efs = EFSClient(URL, TASK)

perception = Perception()
vision = VisionSystem(od, efs, perception)

engine = EventEngine()


# ================= TEST =================
def test_event_stream(duration_sec=20):

    print("\n==============================")
    print("TEST EVENT ENGINE (REAL STREAM)")
    print("==============================")

    start_time = time.time()

    seen_events = set()
    frame_count = 0

    while time.time() - start_time < duration_sec:
        # 1. get real observation
        obs = vision.get_observation()

        # 2. run event engine
        events = engine.update(obs)

        # 3. log frame
        print(f"frame {frame_count}: {events}")

        # 4. collect events
        for e in events:
            seen_events.add(e)

        frame_count += 1
        time.sleep(0.03)

    # ================= ASSERTIONS =================
    print("\n==============================")
    print("EVENT SUMMARY")
    print("==============================")

    print("seen events:", seen_events)

    assert "PRODUCT_STABLE" in seen_events, "PRODUCT_STABLE not detected"
    assert "GLOVE_STABLE" in seen_events, "GLOVE_STABLE not detected"

    print("[PASS] PRODUCT_STABLE detected")
    print("[PASS] GLOVE_STABLE detected")


# ================= ENTRY =================
if __name__ == "__main__":
    print("\nSTART EVENT ENGINE TEST\n")

    camera.open(CAM_NAME, CAM_SRC)
    od.init_model()
    efs.init_model()

    od.start()
    efs.start()

    try:
        test_event_stream()

    finally:
        od.stop()
        efs.stop()
        camera.close(CAM_NAME)

    print("\nALL TESTS PASSED\n")
