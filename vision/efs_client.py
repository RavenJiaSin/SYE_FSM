# vision/efs_client.py

import requests



class EFSClient:
    def __init__(self, url: str, camera_name: str, task_name: str, model_name: str, alert_area: list, threshold: float):
        self.url = url
        self.camera_name = camera_name
        self.task_name = task_name
        self.model_name = model_name
        self.alert_area = alert_area
        self.threshold = threshold
        self.session = requests.Session()

    def init_model(self):
        return self.session.post(
            f"{self.url}/api/init_efs",
            json={
                "alert_area": self.alert_area,
                "model_name": self.model_name,
                "name": self.task_name,
            },
        ).json()

    def start(self):
        return self.session.post(
            f"{self.url}/api/start_live_infer_efs",
            files={
                "cam_name": (None, self.camera_name),
                "name": (None, self.task_name),
                "threshold": (None, str(self.threshold)),
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
