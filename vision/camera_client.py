# vision/camera_client.py

import requests


class CameraClient:
    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()

    def open(self, name, src):
        return self.session.post(
            f"{self.url}/api/camera/open",
            files={
                "cam_type": (None, "cv"),
                "name": (None, name),
                "src": (None, str(src)),
            },
        ).json()

    def close(self, name):
        return self.session.post(
            f"{self.url}/api/camera/close",
            json={"name": name},
        ).json()
