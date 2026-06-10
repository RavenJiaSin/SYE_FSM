from vision.types import Detection, BBox


class Perception:
    """
    PURE TRANSFORM LAYER
    - stateless
    - no counters
    - no debounce
    - no temporal logic
    """

    # ======================================================
    # OD PARSE
    # ======================================================
    # def parse_od(self, od):
    #     if not od:
    #         return {
    #             "product": None,
    #             "glove_left": None,
    #             "glove_right": None,
    #         }

    #     objs = od.get("last_location", [])

    #     product = None
    #     gloves = []

    #     for o in objs:
    #         det = Detection(
    #             cls=o["cls"],
    #             conf=o["conf"],
    #             bbox=BBox(o["x1"], o["y1"], o["x2"], o["y2"]),
    #         )

    #         if o["cls"] == "product":
    #             if product is None or det.conf > product.conf:
    #                 product = det

    #         elif o["cls"] == "glove":
    #             gloves.append(det)

    #     gloves = sorted(gloves, key=lambda g: g.bbox.x1)

    #     return {
    #         "product": product,
    #         "glove_left": gloves[0] if len(gloves) > 0 else None,
    #         "glove_right": gloves[-1] if len(gloves) > 1 else None,
    #     }

    def parse_worker_efs(self, od):
        if not od:
            return {
                "product": None,
                "front": None,
                "side": None,
                "glove_left": None,
                "glove_right": None,
            }

        objs = od.get("last_location", [])

        product = None
        front = None
        side = None
        gloves = []

        for o in objs:
            det = Detection(
                cls=o["cls"],
                conf=o["conf"],
                bbox=BBox(o["x1"], o["y1"], o["x2"], o["y2"]),
            )

            if o["cls"] == "product":
                if product is None or det.conf > product.conf:
                    product = det
            elif o["cls"] == "front":
                if front is None or det.conf > front.conf:
                    front = det
            elif o["cls"] == "side":
                if side is None or det.conf > side.conf:
                    side = det
            elif o["cls"] == "glove":
                gloves.append(det)

        gloves = sorted(gloves, key=lambda g: g.bbox.x1)

        return {
            "product": product,
            "front": front,
            "side": side,
            "glove_left": gloves[0] if len(gloves) > 0 else None,
            "glove_right": gloves[-1] if len(gloves) > 1 else None,
        }

    # ======================================================
    # EFS PARSE (NO STATE, NO DEBOUNCE)
    # ======================================================
    def parse_platform_efs(self, efs):
        if not efs:
            return []

        events = efs.get("last_result", [])

        # normalize event format
        return [
            {
                "label": e["label"],
                "count": e.get("number", 1),
            }
            for e in events
        ]

    # ======================================================
    # MERGE (FRAME OBSERVATION ONLY)
    # ======================================================
    def merge(self, worker_efs_result, platform_efs_result):
        worker_p = self.parse_worker_efs(worker_efs_result)
        platform_p = self.parse_platform_efs(platform_efs_result)

        return {
            # object-level perception
            "product": worker_p["product"],
            "front": worker_p["front"],
            "side": worker_p["side"],
            "glove_left": worker_p["glove_left"],
            "glove_right": worker_p["glove_right"],
            # raw event stream (NO interpretation)
            "EFSevents": platform_p,
        }
