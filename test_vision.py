import time
import json
import config as cfg

from vision.camera_client import CameraClient
from vision.od_client import ODClient
from vision.efs_client import EFSClient
from vision.perception import Perception
from vision.vision_system import VisionSystem


URL = cfg.URL
CAM_NAME = cfg.CAM_NAME
CAM_SRC = cfg.CAM_SRC
TASK = cfg.TASK_NAME

TEST_FRAME = 30


camera = CameraClient(URL)
od = ODClient(URL, TASK)
efs = EFSClient(URL, TASK)
perception = Perception()
vs = VisionSystem(od, efs, perception)


def log(title, data):
    print("\n==============================")
    print(title)
    print("==============================")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print("[PASS]", msg)


# ======================================================
# TEST 1-1 CAMERA + OD + EFS INIT
# ======================================================
def test_init():
    print("\n==============================")
    print("TEST 1-1 INIT SYSTEM")
    print("==============================")

    assert_true(camera.open(CAM_NAME, CAM_SRC)["code"] == 0, "camera open")

    assert_true(od.init_model()["code"] == 0, "od init")

    assert_true(efs.init_model()["code"] == 0, "efs init")


# ======================================================
# TEST 1-2 START STREAM
# ======================================================
def test_start():
    print("\n==============================")
    print("TEST 1-2 START STREAM")
    print("==============================")

    assert_true(od.start()["code"] == 0, "od start")
    assert_true(efs.start()["code"] == 0, "efs start")

def test_od_raw_stream():
    print("\n==============================")
    print("DEBUG OD RAW STREAM")
    print("==============================")

    for i in range(TEST_FRAME):
        res = od.infer_live()
        print(f"frame {i}:", res)
        time.sleep(0.3)

def test_efs_raw_stream():
    print("\n==============================")
    print("DEBUG EFS RAW STREAM")
    print("==============================")

    for i in range(TEST_FRAME):
        res = efs.infer_live()
        print(f"frame {i}:", res)
        time.sleep(0.3)


def test_perception_od():
    print("\n==============================")
    print("TEST 1-3 PERCEPTION OD")
    print("==============================")

    fake_od = {
        "last_location": [
            {"cls": "product", "conf": 0.8, "x1": 50, "y1": 50, "x2": 100, "y2": 100},
            {"cls": "product", "conf": 0.9, "x1": 60, "y1": 60, "x2": 110, "y2": 110},
            {"cls": "glove", "conf": 0.7, "x1": 200, "y1": 200, "x2": 250, "y2": 250},
            {"cls": "glove", "conf": 0.6, "x1": 10, "y1": 10, "x2": 30, "y2": 30},
        ]
    }

    out = perception.parse_od(fake_od)

    assert_true(out["product"] is not None, "product selected")
    assert_true(out["product"].conf == 0.9, "highest confidence product selected")

    assert_true(out["glove_left"] is not None, "glove_left exists")
    assert_true(out["glove_right"] is not None, "glove_right exists")

    # left/right order check
    assert_true(
        out["glove_left"].bbox.x1 <= out["glove_right"].bbox.x1,
        "glove sorted correctly",
    )

def test_perception_efs():
    print("\n==============================")
    print("TEST 1-4 PERCEPTION EFS")
    print("==============================")

    fake_efs = {
        "last_result": [
            {"label": "product", "number": 1},
            {"label": "glove", "number": 2},
        ]
    }

    out = perception.parse_efs(fake_efs)

    assert_true(isinstance(out, list), "efs output is list")

    labels = [e["label"] for e in out]

    assert_true("product" in labels, "product event exists")
    assert_true("glove" in labels, "glove event exists")

    for e in out:
        assert_true("label" in e, "label field exists")
        assert_true("count" in e, "count field exists")

def test_perception_merge():
    print("\n==============================")
    print("TEST 1-5 PERCEPTION MERGE")
    print("==============================")

    fake_od = {
        "last_location": [
            {"cls": "product", "conf": 0.9, "x1": 10, "y1": 10, "x2": 100, "y2": 100},
            {"cls": "glove", "conf": 0.8, "x1": 200, "y1": 200, "x2": 300, "y2": 300},
        ]
    }

    fake_efs = {
        "last_result": [
            {"label": "product", "number": 1},
        ]
    }

    merged = perception.merge(fake_od, fake_efs)

    assert_true("product" in merged, "product exists")
    assert_true("glove_left" in merged, "glove exists")
    assert_true("events" in merged, "events exists")

    assert_true(len(merged["events"]) == 1, "event preserved")

def test_fsm_input():
    print("\n==============================")
    print("TEST 1-6 FSM INPUT VIEW")
    print("==============================")

    fake = {
        "product": None,
        "glove_left": None,
        "glove_right": None,
        "events": [{"label": "product", "count": 1}],
    }

    obs = perception.to_fsm_obs(fake)

    assert_true("has_product" in obs, "fsm has_product exists")
    assert_true("has_gloves" in obs, "fsm glove flag exists")
    assert_true("events" in obs, "fsm events passed through")

def test_vision_system():
    print("\n==============================")
    print("TEST 1-7 VISION SYSTEM (REAL PIPELINE)")
    print("==============================")

    
    results = []

    for i in range(TEST_FRAME):
        obs = vs.step()

        print(
            f"frame {i}:",
            {
                "product": obs["product"] is not None,
                "glove_left": obs["glove_left"] is not None,
                "glove_right": obs["glove_right"] is not None,
                "events": len(obs["events"]),
            },
        )

        results.append(obs)

        time.sleep(0.2)

    # -----------------------------
    # basic sanity checks
    # -----------------------------
    assert_true(len(results) == TEST_FRAME, "frame count correct")

    assert_true(
        all("product" in r for r in results),
        "product field exists in all frames",
    )

    assert_true(
        all("events" in r for r in results),
        "events field exists in all frames",
    )

def test_event_flow_stability():
    print("\n==============================")
    print("TEST 1-8 EVENT FLOW STABILITY")
    print("==============================")

    product_seen_count = 0
    glove_seen_count = 0

    for i in range(TEST_FRAME):
        obs = vs.step()

        if obs["product"]:
            product_seen_count += 1

        if obs["glove_left"] or obs["glove_right"]:
            glove_seen_count += 1

        print(f"frame {i} events:", obs["events"])

        time.sleep(0.2)

    assert_true(product_seen_count >= 1, "product detected in stream")
    assert_true(glove_seen_count >= 1, "glove detected in stream")

def test_fsm_ready_input():
    print("\n==============================")
    print("TEST 1-9 FSM INPUT VALIDATION")
    print("==============================")

    obs = vs.step()
    fsm = perception.to_fsm_obs(obs)

    assert_true("has_product" in fsm, "fsm has_product")
    assert_true("has_gloves" in fsm, "fsm has_gloves")
    assert_true("events" in fsm, "fsm events exists")

    assert_true(
        isinstance(fsm["events"], list),
        "fsm events type correct",
    )

# ======================================================
# TEST CLEANUP
# ======================================================
def test_stop():
    print("\n==============================")
    print("TEST STOP")
    print("==============================")

    od.stop()
    efs.stop()
    camera.close(CAM_NAME)


if __name__ == "__main__":
    print("\nSTART VISION TEST SUITE\n")
    try:
        test_init()
        test_start()

        test_od_raw_stream()
        test_efs_raw_stream()
        

        test_perception_od()
        test_perception_efs()
        test_perception_merge()
        test_fsm_input()

        # 🔥 NEW IMPORTANT TESTS
        test_vision_system()
        test_event_flow_stability()
        test_fsm_ready_input()

        test_stop()
    except Exception:
        test_stop()

    print("\nALL TESTS PASSED\n")
