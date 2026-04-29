import requests
import time
import json
import webbrowser
import config as cfg

URL = cfg.URL

CAM_NAME = cfg.CAM_NAME
CAM_SRC = cfg.CAM_SRC
ALERT_AREA = cfg.ALERT_AREA
MODEL_NAME = cfg.MODEL_NAME
TASK_NAME = cfg.TASK_NAME
THRESHOLD = cfg.THRESHOLD

session = requests.Session()


def pp(title, data):
    print("\n" + "=" * 20)
    print(title)
    print("=" * 20)
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ================= 1. camera =================
def test_camera():
    res = session.post(
        f"{URL}/api/camera/open",
        data={
            "cam_type": "cv",
            "name": CAM_NAME,
            "src": CAM_SRC,
        },
    )
    pp("camera/open", res.json())


# ================= 2. init =================
def test_init():
    res = session.post(
        f"{URL}/api/init_efs",
        json={
            "alert_area": ALERT_AREA,
            "model_name": MODEL_NAME,
            "name": TASK_NAME,
        },
    )
    pp("init_efs", res.json())


# ================= 3. start =================
def test_start():
    res = session.post(
        f"{URL}/api/start_live_infer_efs",
        data={
            "cam_name": CAM_NAME,
            "name": TASK_NAME,
            "threshold": str(THRESHOLD),
        },
    )
    pp("start_live_infer_efs", res.json())


# ================= 4. live check =================
def test_live():
    print("\n[LIVE MONITOR]")

    for i in range(20):
        res = session.get(
            f"{URL}/api/infer_efs/live_result",
            params={"name": TASK_NAME},
        )

        data = res.json()

        print("\nframe", i)
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # ===== analysis =====
        if data.get("result"):
            last = data["result"].get("last_result", [])

            labels = [x["label"] for x in last]

            print("labels:", labels)

        time.sleep(0.5)


# ================= 5. stop =================
def test_stop():
    res = session.post(
        f"{URL}/api/stop_live_infer_efs",
        json={"name": TASK_NAME},
    )
    pp("stop", res.json())


# ================= 6. close =================
def test_close():
    res = session.post(
        f"{URL}/api/camera/close",
        json={"name": CAM_NAME},
    )
    pp("close", res.json())

def test_stream():
    stream_url = f"{URL}/api/infer_efs/live?name={TASK_NAME}"
    print("STREAM:", stream_url)

    webbrowser.open(stream_url)

if __name__ == "__main__":
    test_camera()
    test_init()
    test_start()
    test_stream()
    test_live()
    test_stop()
    test_close()
