import requests
import json
import time
import webbrowser
import config as cfg

URL = cfg.URL

CAM_NAME = cfg.CAM_NAME
CAM_SRC = cfg.CAM_SRC
MODEL_NAME = cfg.MODEL_NAME
TASK_NAME = cfg.TASK_NAME
THRESHOLD = cfg.THRESHOLD

session = requests.Session()


def pp(title, res):
    print(f"\n==== {title} ====")
    try:
        print(json.dumps(res.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error occurred: {e}")
        print(res.text)


def test_camera():
    # ================= 1. 開攝影機 =================
    res = session.post(
        f"{URL}/api/camera/open", data={"cam_type": "cv", "name": CAM_NAME, "src": CAM_SRC}
    )
    return pp("camera/open", res)
    

def test_init():
    # ================= 2. init OD =================
    res = session.post(
        f"{URL}/api/init_od", json={"model_name": MODEL_NAME, "threshold": THRESHOLD}
    )
    return pp("init_od", res)

def test_live():
    # ================= 3. start live =================
    res = session.post(
        f"{URL}/api/start_live_infer_od",
        data={"cam_name": CAM_NAME},
    )

    data = res.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))

    stream_url = URL + data["result"]["result_image"]

    print("\nSTREAM:", stream_url)

    webbrowser.open(stream_url)
    # ================= 4. polling =================
    for i in range(10):
        res = session.get(f"{URL}/api/infer_od/live_result")

        print(f"\nframe {i}")
        try:
            data = res.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error occurred: {e}")

        time.sleep(0.5)

def test_stop():
    # ================= 5. stop =================
    session.post(f"{URL}/api/stop_live_infer_od")

def test_close_camera():
    # ================= 6. close camera =================
    session.post(f"{URL}/api/camera/close", json={"name": CAM_NAME})

if __name__ == "__main__":
    try:
        test_camera()
        test_init()
        test_live()
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        test_stop()
        test_close_camera()
