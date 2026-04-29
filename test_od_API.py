import requests
import json
import time
import webbrowser

URL = "http://127.0.0.1:8000"

CAM_NAME = "camera_efs_demo"
CAM_SRC = r"D:\NCU\intern\workspace\EFS\program_example\sye_0414.mp4"

MODEL_NAME = "sye"
TASK_NAME = "od_task_demo"
THRESHOLD = 0.6

session = requests.Session()


def pp(title, res):
    print(f"\n==== {title} ====")
    try:
        print(json.dumps(res.json(), indent=2, ensure_ascii=False))
    except:
        print(res.text)


# ================= 1. 開攝影機 =================
res = session.post(
    f"{URL}/api/camera/open", data={"cam_type": "cv", "name": CAM_NAME, "src": CAM_SRC}
)
pp("camera/open", res)


# ================= 2. init OD =================
res = session.post(
    f"{URL}/api/init_od", json={"model_name": MODEL_NAME, "threshold": THRESHOLD}
)
pp("init_od", res)


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
    except:
        print("invalid json")

    time.sleep(0.5)


# ================= 5. stop =================
session.post(f"{URL}/api/stop_live_infer_od")


# ================= 6. close camera =================
session.post(f"{URL}/api/camera/close", json={"name": CAM_NAME})
