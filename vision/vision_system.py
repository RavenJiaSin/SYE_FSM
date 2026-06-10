# vision/vision_system.py


class VisionSystem:
    def __init__(self, worker_efs_client, platform_efs_client, perception):
        self.worker_efs = worker_efs_client
        self.platform_efs = platform_efs_client
        self.perception = perception

    def step(self):
        worker_efs = self.worker_efs.infer_live()
        platform_efs = self.platform_efs.infer_live()

        return self.perception.merge(worker_efs, platform_efs)
