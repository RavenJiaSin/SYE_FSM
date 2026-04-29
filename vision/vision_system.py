# vision/vision_system.py


class VisionSystem:
    def __init__(self, od_client, efs_client, perception):
        self.od = od_client
        self.efs = efs_client
        self.perception = perception

    def step(self):
        od = self.od.infer_live()
        efs = self.efs.infer_live()

        return self.perception.merge(od, efs)
