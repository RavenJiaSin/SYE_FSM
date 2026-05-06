# ================= API SERVER =================
URL = "http://127.0.0.1:8000"

# ================= CAMERA =================
CAM_NAME = "camera_efs_demo"
CAM_SRC = (
    r"D:\NCU\intern\workspace\EFS\program_example\SYE_FSM\template_cam\sye_special.mp4"
)

# ================= MODEL =================
MODEL_NAME = "sye"
TASK_NAME = "efs_task_demo"
THRESHOLD = 0.6

# ================= MONITOR =================
MONITOR_DURATION = 30  # seconds

# ================= PLATFORM ROI =================
# normalized coordinates (0~1)
ALERT_AREA = [
    # [
    #     {"x": 0.4867, "y": 0.6347},
    #     {"x": 0.6492, "y": 0.7375},
    #     {"x": 0.3875, "y": 0.9931},
    #     {"x": 0.2547, "y": 0.8208},
    # ]
    [
        {"x": 0.6289, "y": 0.7625},
        {"x": 0.5266, "y": 0.7917},
        {"x": 0.5078, "y": 0.7236},
        {"x": 0.3125, "y": 0.8889},
        {"x": 0.332, "y": 0.9639},
        {"x": 0.3891, "y": 0.9931},
    ]
]

# ================= FSM PARAMETERS =================
N_MISSING_FRAMES = 10
N_DOUBLE_HAND_FRAMES = 10
WAIT_TIMEOUT_FRAMES = 20
MIN_PLACE_FRAMES = 30
