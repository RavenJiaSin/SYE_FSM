# ================= API SERVER =================
URL = "http://127.0.0.1:8000"

# ================= CAMERA =================
CAM_NAME = "camera_efs_demo"
CAM_SRC = (
    r"D:/NCU/intern/workspace/EFS/program_example/SYE_FSM/template_cam/sye_0414.mp4"
)

# ================= MODEL =================
MODEL_NAME = "sye_1"
TASK_NAME = ["WORKER",'PLATFORM']

THRESHOLD = 0.6

# ================= MONITOR =================
MONITOR_DURATION = 30  # seconds

# ================= PLATFORM ROI =================
# normalized coordinates (0~1)
PLATFORM_AREA = [
    [
        {"x": 0.6289, "y": 0.7625},
        {"x": 0.5266, "y": 0.7917},
        {"x": 0.5078, "y": 0.7236},
        {"x": 0.3125, "y": 0.8889},
        {"x": 0.332, "y": 0.9639},
        {"x": 0.3891, "y": 0.9931},
    ]
]

WORKER_AREA = [
    [
        {"x": 0.2062, "y": 0.0306},
        {"x": 0.225, "y": 0.9833},
        {"x": 0.6406, "y": 0.9903},
        {"x": 0.6594, "y": 0.0417},
    ]
]

# ================= FSM PARAMETERS =================
MAX_PRODUCT_MISSING_FRAMES = 30
MIN_DOUBLE_HAND_FRAMES = 10
MAX_PICK_UP_FRAMES = 40
MAX_PLACING_FRAMES = 60
MIN_PLACING_FRAMES = 5
