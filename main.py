import time
import config as cfg

from vision.camera_client import CameraClient
# from vision.od_client import ODClient
from vision.efs_client import EFSClient
from vision.perception import Perception
from vision.vision_system import VisionSystem
from vision.event_engine import EventEngine
import webbrowser
from fsm.context import FSMContext



def main():

    # ================= INIT =================
    camera = CameraClient(cfg.URL)
    # od = ODClient(cfg.URL, cfg.CAM_NAME, cfg.TASK_NAME, cfg.MODEL_NAME, cfg.THRESHOLD)
    worker_efs = EFSClient(
        cfg.URL,
        cfg.CAM_NAME,
        cfg.TASK_NAME[0],
        cfg.MODEL_NAME,
        cfg.WORKER_AREA,
        cfg.THRESHOLD,
    )
    platform_efs = EFSClient(
        cfg.URL,
        cfg.CAM_NAME,
        cfg.TASK_NAME[1],
        cfg.MODEL_NAME,
        cfg.PLATFORM_AREA,
        cfg.THRESHOLD,
    )

    perception = Perception()
    vision = VisionSystem(worker_efs, platform_efs, perception)
    event = EventEngine()

    fsm = FSMContext('idle')

    # bind config to FSM
    fsm.N_MISSING_FRAMES = cfg.N_MISSING_FRAMES
    fsm.N_DOUBLE_HAND_FRAMES = cfg.N_DOUBLE_HAND_FRAMES
    fsm.WAIT_TIMEOUT_FRAMES = cfg.WAIT_TIMEOUT_FRAMES
    fsm.MIN_PLACE_FRAMES = cfg.MIN_PLACE_FRAMES

    # ================= START =================
    camera.open(cfg.CAM_NAME, cfg.CAM_SRC)
    worker_efs.init_model()
    platform_efs.init_model()

    worker_efs.start()
    platform_efs.start()

    print("SYSTEM STARTED")

    stream_url_worker = f"{cfg.URL}/api/infer_efs/live?name={cfg.TASK_NAME[0]}"
    stream_url_platform = f"{cfg.URL}/api/infer_efs/live?name={cfg.TASK_NAME[1]}"
    webbrowser.open(stream_url_worker)
    webbrowser.open(stream_url_platform)

    # ================= LOOP =================
    try:
        while True:
            # 1. get fused observation
            obs = vision.step()

            # 2. event engine
            events = event.update(obs)
            

            # 3. update FSM
            fsm.update(events)

            # 4. debug output (optional)
            # print(f"Events: {events}")

            time.sleep(0.03)  # ~30 FPS control

    except KeyboardInterrupt:
        print("KEYBOARD INTERRUPT - STOPPING SYSTEM")
    except Exception as e:
        print(e)
        print("STOPPING SYSTEM")

    finally:
        worker_efs.stop()
        platform_efs.stop()
        camera.close(cfg.CAM_NAME)


if __name__ == "__main__":
    main()
