# vision/efs_client.py

import requests
import config as cfg


class EFSClient:
    def __init__(self, url: str, task_name: str):
        self.url = url
        self.task_name = task_name
        self.session = requests.Session()

    def init_model(self):
        return self.session.post(
            f"{self.url}/api/init_efs",
            json={
                "alert_area": cfg.ALERT_AREA,
                "model_name": cfg.MODEL_NAME,
                "name": self.task_name,
            },
        ).json()

    def start(self):
        return self.session.post(
            f"{self.url}/api/start_live_infer_efs",
            files={
                "cam_name": (None, cfg.CAM_NAME),
                "name": (None, self.task_name),
                "threshold": (None, str(cfg.THRESHOLD)),
            },
        ).json()

    def stop(self):
        return self.session.post(
            f"{self.url}/api/stop_live_infer_efs",
            json={"name": self.task_name},
        ).json()

    def infer_live(self):
        resp = self.session.get(
            f"{self.url}/api/infer_efs/live_result",
            params={"name": self.task_name},
        ).json()

        if resp.get("code") != 0:
            return None

        return resp.get("result")
