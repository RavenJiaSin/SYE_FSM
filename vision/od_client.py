# vision/od_client.py

# =======================================================
# NOT USEED in version 2026/06/10
# Kept for reference, may be used in future for OD-based system or combined OD+EFS system
# =======================================================

import requests


class ODClient:
    def __init__(self, url: str,camera_name: str, task_name: str, model_name: str, threshold: float):
        self.url = url
        self.camera_name = camera_name
        self.task_name = task_name
        self.model_name = model_name
        self.threshold = threshold
        self.session = requests.Session()
        

    def init_model(self):
        return self.session.post(
            f"{self.url}/api/init_od",
            json={
                "model_name": self.model_name,
                "name": self.task_name,
            },
        ).json()

    def get_labels(self):
        return self.session.post(f"{self.url}/api/class_names_od").json()

    def start(self):
        return self.session.post(
            f"{self.url}/api/start_live_infer_od",
            files={
                "cam_name": (None, self.camera_name),
                "name": (None, self.task_name),
                "threshold": (None, str(self.threshold)),
            },
        ).json()

    def stop(self):
        return self.session.post(f"{self.url}/api/stop_live_infer_od").json()

    def infer_live(self):
        resp = self.session.get(
            f"{self.url}/api/infer_od/live_result",
            params={"name": self.task_name},
        ).json()

        if resp.get("code") != 0:
            return None

        return resp.get("result")
