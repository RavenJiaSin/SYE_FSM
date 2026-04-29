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
    def parse_od(self, od):
        if not od:
            return {
                "product": None,
                "glove_left": None,
                "glove_right": None,
            }

        objs = od.get("last_location", [])

        product = None
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

            elif o["cls"] == "glove":
                gloves.append(det)

        gloves = sorted(gloves, key=lambda g: g.bbox.x1)

        return {
            "product": product,
            "glove_left": gloves[0] if len(gloves) > 0 else None,
            "glove_right": gloves[-1] if len(gloves) > 1 else None,
        }

    # ======================================================
    # EFS PARSE (NO STATE, NO DEBOUNCE)
    # ======================================================
    def parse_efs(self, efs):
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
    def merge(self, od, efs):
        od_p = self.parse_od(od)
        efs_p = self.parse_efs(efs)

        return {
            # object-level perception
            "product": od_p["product"],
            "glove_left": od_p["glove_left"],
            "glove_right": od_p["glove_right"],
            # raw event stream (NO interpretation)
            "EFSevents": efs_p,
        }
